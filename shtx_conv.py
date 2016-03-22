################################################################################
# Copyright © 2016 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os
from PyQt4 import QtGui
from PyQt4.QtGui import QImage, qRgba

from util import to_u16, list_all_files

SHTX_MAGIC   = "SHTX"
SHTXFS_MAGIC = "SHTXFS"

def convert_shtx_file(filename, out_file = None):
  
  if out_file == None:
    out_file = os.path.splitext(filename)[0] + ".png"
  
  data = None
  
  with open(filename, "rb") as f:
    
    if not f.read(4) == SHTX_MAGIC:
      return False
    
    f.seek(0)
    data = bytearray(f.read())
    
  img = convert_shtx(data)
  
  if not img:
    return False
    
  try:
    os.makedirs(os.path.dirname(out_file))
  except:
    pass
  
  img = img.convertToFormat(QImage.Format_ARGB32_Premultiplied)
  img.save(out_file)
  
  return True

def convert_shtx(data):
  
  if not data[:4] == SHTX_MAGIC:
    return
  
  if data[:6] == SHTXFS_MAGIC:
    img = convert_shtx_8bit(data[6:])
  
  else:
    img = convert_shtx_4bit(data[4:])
  
  return img

def convert_shtx_8bit(data):
  
  width  = to_u16(data[0:2])
  height = to_u16(data[2:4])
  unk    = to_u16(data[4:6])
  p      = 6
  
  palette = []
  
  for i in range(256):
    palette.append(qRgba(data[p], data[p + 1], data[p + 2], data[p + 3]))
    p += 4
  
  pixels = data[p : p + (width * height)]
  
  img = QImage(pixels, width, height, QImage.Format_Indexed8)
  img.setColorTable(palette)
  
  return img

def convert_shtx_4bit(data):
  
  width  = to_u16(data[0:2])
  height = to_u16(data[2:4])
  unk    = data[4:12]
  p      = 12
  
  palette = []
  
  for i in range(16):
    palette.append(qRgba(data[p], data[p + 1], data[p + 2], data[p + 3]))
    p += 4
  
  pixels = data[p : p + (width * height / 2)]
  pixels2 = bytearray()
  
  for b in pixels:
    pixels2.append(b & 0x0F)
    pixels2.append((b >> 4))
  
  img = QImage(pixels2, width, height, QImage.Format_Indexed8)
  img.setColorTable(palette)
  
  return img
  
if __name__ == "__main__":
  import argparse
  
  print
  print "**********************************************"
  print "* SHTX converter, written by BlackDragonHunt. "
  print "**********************************************"
  print
  
  parser = argparse.ArgumentParser(description = "Convert SHTX-formatted images to PNG.")
  parser.add_argument("input", metavar = "<input file|dir>", nargs = "+", help = "An input file or directory.")
  parser.add_argument("-o", "--output", metavar = "<output dir>", help = "The output directory.")
  args = parser.parse_args()
  
  for in_path in args.input:
    
    if os.path.isdir(in_path):
      base_dir = os.path.normpath(in_path)
      files = list_all_files(base_dir)
    elif os.path.isfile(in_path):
      base_dir = os.path.dirname(in_path)
      files = [in_path]
    else:
      continue
    
    if args.output:
      out_dir = os.path.normpath(args.output)
    else:
      out_dir = base_dir
  
    for filename in files:
      out_file = os.path.join(out_dir, filename[len(base_dir) + 1:])
      out_file = os.path.splitext(out_file)[0] + ".png"
      
      try:
        if convert_shtx_file(filename, out_file):
          print filename
          print " -->", out_file
          # print
      
      except:
        print "Failed to convert", filename
        # raise
  
  print
  raw_input("Press Enter to exit.")

### EOF ###