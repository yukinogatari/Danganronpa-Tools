################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
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
  
  unk1 = data.read(4)
  unk2 = data.read(4)
  unk3 = data.read(4)
  unk4 = data.read(4)
  
  if not unk1 == "\x10\x00\x00\x00":
    print "???"
    
  if not unk2 == "\xFB\xDB\x32\x01":
    print "???"
    
  if not unk3 == "\x41\xDC\x32\x01":
    print "???"
    
  if not unk4 == "\x00\x00\x00\x00":
    print "???"
  
  name = data.get_str()
  
  return name

################################################################################

# Via http://stackoverflow.com/a/14267825
def power_of_two(x):
  return 2**(x-1).bit_length()

def read_txr(data, subdata, filename, crop = False):
  unk1        = data.get_u32() # 01 00 00 00
  swiz        = data.get_u16()
  disp_width  = data.get_u16()
  disp_height = data.get_u16()
  scanline    = data.get_u16()
  fmt         = data.get_u8()
  unk2        = data.get_u8()
  unk3        = data.get_u16()
  
  print "%4d %4d %4d %4d 0x%02X 0x%02X %4d" % (swiz, disp_width, disp_height, scanline, fmt, unk2, unk3),
  
  img_data_type, img_data, img_subdata = read_srd_item(subdata)
  
  img_data.read(4) # 06 05 08 01
  img_data.read(4) # ???
  img_data.read(4) # ???
  name_offset = img_data.get_u32()
  
  img_start = img_data.get_u32() & 0x00FFFFFF # idk wtf the top byte is doing
  img_len   = img_data.get_u32()
  img_data.read(4) # 10 00 00 00
  img_data.read(4) # 00 00 00 00
  
  img_data.seek(name_offset)
  name = img_data.get_str()
  
  print "0x%08X 0x%08X" % (img_start, img_len), name
  
  filename_base = os.path.splitext(filename)[0]
  img_filename = filename_base + ".srdv"
  
  # Is there some consistent way to determine whether to use an srdv or srdi file?
  # If there isn't an srdv file, the srdi file seems to work fine,
  # but sometimes there are both so ???
  if not os.path.isfile(img_filename):
    img_filename = filename_base + ".srdi"
  
  with open(img_filename, "rb") as f:
    f.seek(img_start)
    img_data = bytearray(f.read(img_len))
  
  swizzled = False
  mode     = "RGBA"
  decoder  = None
  arg      = None
  
  if not swiz & 1:
    swizzled = True
  
  if fmt == 0x01:
    decoder = "raw"
    arg     = "BGRA"
    
    # Round up to nearest multiple of 8.
    # I'm not 100% sure this is correct, since there's only one image in the
    # entire game that isn't a multiple of 8, and doing this happens to fix it.
    height = int(math.ceil(disp_height / 8.0) * 8.0)
    width  = int(math.ceil(disp_width / 8.0) * 8.0)
    
    if swizzled:
      img_data = PostProcessMortonUnswizzle(img_data, width, height, 4)
  
  elif fmt in [0x0F, 0x11, 0x14, 0x16]:
    
    # DXT1
    if fmt == 0x0F:
      decoder = "bcn"
      arg     = 1
      bytespp = 8
    
    # DXT5
    elif fmt == 0x11:
      decoder = "bcn"
      arg     = 3
      bytespp = 16
    
    # BC5
    elif fmt == 0x14:
      decoder = "bcn"
      arg     = 5
      bytespp = 16
    
    # BC4
    elif fmt == 0x16:
      mode    = "L"
      decoder = "bcn"
      arg     = 4
      bytespp = 8
    
    # Round up to nearest power of two.
    width = power_of_two(disp_width)
    height = power_of_two(disp_height)
    
    if swizzled and width >= 4 and height >= 4:
      img_data = PostProcessMortonUnswizzle(img_data, width / 4, height / 4, bytespp)
  
  else:
    print "!!!", hex(fmt), "!!!"
    return None, None
  
  img = Image.frombytes(mode, (width, height), bytes(img_data), decoder, arg)
  
  # The game seems to handle BC5 differently than Pillow.
  # I'm not 100% sure this is right, but it seems to be based on what I've seen?
  if fmt == 0x14:
    r, g, b, a = img.split()
    b = g.copy()
    a = Image.new("L", (width, height), 0xFF)
    img = Image.merge("RGBA", (r, g, b, a))
  
  if crop and not (disp_width == width and disp_height == height):
    img = img.crop((0, 0, disp_width, disp_height))
  
  return name, img

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
      name, img = read_txr(data, subdata, filename, crop)
      
      if not name or not img:
        continue
      
      out_file = os.path.splitext(os.path.join(subdir, name))[0]
      
      try:
        os.makedirs(subdir)
      except:
        pass
      
      img.save(out_file + ".png")
    
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
    
    else:
      print data_type
    
if __name__ == "__main__":
  dirs = [
    # Retail data
    "dec/partition_data_vita",
    "dec/partition_resident_vita",
    "dec/partition_patch101_vita",
    
    # Demo data
    "dec/partition_data_vita_taiken_ja",
    "dec/partition_resident_vita_taiken_ja",
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