# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

import os
import math

from util import *
from swizzle import PostProcessMortonUnswizzle

from PIL import Image

def read_srd_item(f):
  
  data_type   = f.read(4)
  
  if len(data_type) < 4:
    return None, None, None
  
  if not data_type.startswith("$"):
    return None, None, None
  
  data_len    = f.get_u32be()
  subdata_len = f.get_u32be()
  padding     = f.get_u32be()
  
  # print data_type, data_len, subdata_len, padding
  
  data_padding = (0x10 - data_len % 0x10) % 0x10
  subdata_padding = (0x10 - subdata_len % 0x10) % 0x10
  
  data    = f.get_bin(data_len)
  f.read(data_padding)
  
  subdata = f.get_bin(subdata_len)
  f.read(subdata_padding)
  
  return data_type, data, subdata

################################################################################

def read_rsf(data, subdata):
  unk1 = data.read(4) # 10 00 00 00 ???
  unk2 = data.read(4) # FB DB 32 01 ???
  unk3 = data.read(4) # 41 DC 32 01 ???
  unk4 = data.read(4) # 00 00 00 00 ???
  name = data.get_str()
  return name

################################################################################

# Via http://stackoverflow.com/a/14267825
def power_of_two(x):
  return 2**(x-1).bit_length()

def read_txr(data, subdata, filename, crop = False, keep_mipmaps = False):
  unk1        = data.get_u32() # 01 00 00 00
  swiz        = data.get_u16()
  disp_width  = data.get_u16()
  disp_height = data.get_u16()
  scanline    = data.get_u16()
  fmt         = data.get_u8()
  unk2        = data.get_u8()
  palette     = data.get_u8()
  palette_id  = data.get_u8()
  
  img_data_type, img_data, img_subdata = read_srd_item(subdata)
  
  img_data.read(2) # 06 05
  unk5 = img_data.get_u8() # ???
  mipmap_count = img_data.get_u8()
  img_data.read(4) # ???
  img_data.read(4) # ???
  name_offset = img_data.get_u32()
  
  mipmaps = []
  for i in range(mipmap_count):
    mipmap_start = img_data.get_u32() & 0x0FFFFFFF # idk wtf the top byte is doing
    mipmap_len   = img_data.get_u32()
    mipmap_unk1  = img_data.get_u32() # XX 00 00 00
    mipmap_unk2  = img_data.get_u32() # 00 00 00 00
    
    mipmaps.append((mipmap_start, mipmap_len, mipmap_unk1, mipmap_unk2))
  
  # Do we have a palette?
  pal_start = None
  pal_len   = None
  
  # FIXME: ???
  if palette == 0x01:
    pal_start, pal_len, _, _ = mipmaps.pop(palette_id)
  
  img_data.seek(name_offset)
  name = img_data.get_str(encoding = "CP932")
  
  print "%4d %4d %2d 0x%02X 0x%02X %3d %3d %3d" % (swiz, scanline, mipmap_count, fmt, unk2, palette, palette_id, unk5), name.encode("UTF-8")
  # print "0x%02X %2d Mipmaps %3d %3d" % (fmt, mipmap_count, palette, palette_id), name.encode("UTF-8")
  
  filename_base = os.path.splitext(filename)[0]
  img_filename = filename_base + ".srdv"
  
  # Is there some consistent way to determine whether to use an srdv or srdi file?
  # If there isn't an srdv file, the srdi file seems to work fine,
  # but sometimes there are both so ???
  if not os.path.isfile(img_filename):
    img_filename = filename_base + ".srdi"
  
  images = []
  
  if not keep_mipmaps:
    mipmaps = mipmaps[:1]
  
  for i in range(len(mipmaps)):
    
    mipmap_name = os.path.splitext(name)[0]
    if len(mipmaps) > 1:
      mipmap_name += "_%dx%d" % (disp_width, disp_height)
    mipmap_name += ".png"
    
    with open(img_filename, "rb") as f:
      mipmap_start, mipmap_len, mipmap_unk1, mipmap_unk2 = mipmaps[i]
      f.seek(mipmap_start)
      img_data = bytearray(f.read(mipmap_len))
      print "     %4d %4d 0x%08X 0x%08X" % (disp_width, disp_height, mipmap_start, mipmap_len)
      
      pal_data = None
      if not pal_start is None:
        f.seek(pal_start)
        pal_data = bytearray(f.read(pal_len))
    
    swizzled = False
    mode     = "RGBA"
    decoder  = None
    arg      = None
    
    if not swiz & 1:
      swizzled = True
    
    # Raw formats.
    if fmt in [0x01, 0x02, 0x05, 0x1A]:
      decoder = "raw"
      
      # 32-bit BGRA
      if fmt == 0x01:
        arg     = "BGRA"
        bytespp = 4
      
      # 16-bit BGR
      elif fmt == 0x02:
        mode    = "RGB"
        arg     = "BGR;16"
        bytespp = 2
      
      # 16-bit BGRA
      elif fmt == 0x05:
        # Pillow doesn't support 16-bit raw BGRA, so take as RGBA and fix later.
        arg     = "RGBA;4B"
        bytespp = 2
      
      # 8-bit indexed
      elif fmt == 0x1A:
        arg     = "BGRA"
        bytespp = 4
        
        # I can't seem to get Pillow to cooperate with palettes that have alpha
        # channels, so I'm just going to be lazy and convert from indexed by hand.
        old_img_data = img_data
        img_data = bytearray()
        
        for p in old_img_data:
          img_data.extend(pal_data[p * 4 : p * 4 + 4])
      
      width = scanline / bytespp
      height = disp_height
      
      if swizzled:
        img_data = PostProcessMortonUnswizzle(img_data, width, height, bytespp)
    
    # Block-compression, power-of-two formats.
    elif fmt in [0x0F, 0x11, 0x14, 0x16, 0x1C]:
      decoder = "bcn"
      
      # DXT1
      if fmt == 0x0F:
        arg     = 1
        bytespp = 8
      
      # DXT5
      elif fmt == 0x11:
        arg     = 3
        bytespp = 16
      
      # BC5
      elif fmt == 0x14:
        arg     = 5
        bytespp = 16
      
      # BC4
      elif fmt == 0x16:
        mode    = "L"
        arg     = 4
        bytespp = 8
      
      # BC7 / DX10
      elif fmt == 0x1C:
        arg = 7
        bytespp = 16
      
      # FIXME: ???
      if unk5 == 0x08:
        # Round up to nearest power of two.
        width = power_of_two(disp_width)
        height = power_of_two(disp_height)
      
      else:
        width = disp_width
        height = disp_height
      
      if swizzled and width >= 4 and height >= 4:
        img_data = PostProcessMortonUnswizzle(img_data, width / 4, height / 4, bytespp)
    
    else:
      print "!!!", hex(fmt), "!!!"
      return []
    
    img = Image.frombytes(mode, (width, height), bytes(img_data), decoder, arg)
    
    # The game seems to handle BC5 differently than Pillow.
    # I'm not 100% sure this is right, but it seems to be based on what I've seen?
    if fmt == 0x14:
      r, g, b, a = img.split()
      b = g.copy()
      a = Image.new("L", (width, height), 0xFF)
      img = Image.merge("RGBA", (r, g, b, a))
    
    # Pillow doesn't handle 16-bit BGRA, so we have to swap the R and B channels.
    if fmt == 0x05:
      r, g, b, a = img.split()
      img = Image.merge("RGBA", (b, g, r, a))
    
    if crop and not (disp_width == width and disp_height == height):
      img = img.crop((0, 0, disp_width, disp_height))
    
    images.append((mipmap_name, img))
    
    disp_width = max(1, disp_width / 2)
    disp_height = max(1, disp_height / 2)
  
  return images

def read_txi(data, subdata, filename):
  return

################################################################################

def srd_ex(filename, out_dir = None, crop = False):
  out_dir = out_dir or os.path.splitext(filename)[0]
  f = BinaryFile(filename, "rb")
  srd_ex_data(f, filename, out_dir, crop)
  f.close()

def srd_ex_data(f, filename, out_dir, crop = False):
  
  subdir = out_dir
  
  while True:
    
    data_type, data, subdata = read_srd_item(f)
    
    if data_type is None:
      break
    
    # Header
    if data_type == "$CFH":
      # Always first in a file, so just ignoring it.
      pass
    
    # End item?
    elif data_type == "$CT0":
      # We don't seem to do any really complicated nesting, so ignoring this.
      pass
    
    # Resource (folder)?
    elif data_type == "$RSF":
      subdir = read_rsf(data, subdata)
      subdir = os.path.join(out_dir, subdir)
    
    # Texture (srdv file)?
    elif data_type == "$TXR":
      images = read_txr(data, subdata, filename, crop)
      
      for name, img in images:
        if not name or not img:
          continue
        
        # out_file = os.path.splitext(os.path.join(subdir, name))[0]
        out_file = os.path.join(subdir, name)
        
        try:
          os.makedirs(subdir)
        except:
          pass
        
        img.save(out_file)
    
    # Texture information?
    elif data_type == "$TXI":
      pass
    
    # Resource information?
    # elif data_type == "$RSI":
    #   pass
    
    # Vertex?
    elif data_type == "$VTX":
      pass
    
    # Scene?
    elif data_type == "$SCN":
      pass
    
    # Mesh?
    elif data_type == "$MSH":
      pass
    
    # ?
    elif data_type == "$TRE":
      pass
    
    # Material?
    elif data_type == "$MAT":
      pass
    
    # ?
    elif data_type == "$COL":
      pass
    
    # ?
    elif data_type == "$OVT":
      pass
    
    # Volume tree
    elif data_type == "$VTR":
      pass
    
    # Shader stuff?
    elif data_type == "$VSD":
      pass
    
    # Shader stuff?
    elif data_type == "$PSD":
      pass
    
    # ???
    elif data_type == "$SKL":
      pass
    
    else:
      print data_type
    
if __name__ == "__main__":
  dirs = [
    # Retail data
    "dec/partition_data_vita",
    "dec/partition_resident_vita",
    "dec/partition_patch101_vita",
    "dec/partition_patch102_vita",
    
    # Demo data
    "dec/partition_data_vita_taiken_ja",
    "dec/partition_resident_vita_taiken_ja",
    
    # PC demo data
    "dec/partition_data_win_demo",
    "dec/partition_data_win_demo_jp",
    "dec/partition_data_win_demo_us",
    "dec/partition_resident_win_demo",
  ]
  
  for dirname in dirs:
    for fn in list_all_files(dirname):
      if not os.path.splitext(fn)[1].lower() in [".srd", ".stx"]:
        continue
      
      out_dir = os.path.dirname(fn[len(dirname) + 1:])
      out_dir = os.path.join(dirname + "-ex", out_dir)
      
      print
      print fn
      print
      srd_ex(fn, out_dir, crop = True)

### EOF ###