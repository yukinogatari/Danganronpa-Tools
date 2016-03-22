################################################################################
# Copyright © 2016 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os
from util import to_u32, list_all_files

CMP_MAGIC = "\xFC\xAA\x55\xA7"
GX3_MAGIC = "\x47\x58\x33\x00" # GX3\0

def dr_dec_file(filename, out_file = None):
  
  if out_file == None:
    out_file, ext = os.path.splitext(filename)
    out_file = out_file + "-dec" + ext
  
  data = None
  
  with open(filename, "rb") as f:
    
    if not f.read(4) in [CMP_MAGIC, GX3_MAGIC]:
      return False
    
    f.seek(0)
    data = bytearray(f.read())
    
  dec = dr_dec(data)
  
  if not dec:
    return False
  
  # Double compressed.
  if dec[:4] == GX3_MAGIC:
    dec = dr_dec(dec[4:])
    
  try:
    os.makedirs(os.path.dirname(out_file))
  except:
    pass
  
  with open(out_file, "wb") as f:
    f.write(dec)
  
  return True

def dr_dec(data):
  
  magic = data[:4]
  
  if magic == GX3_MAGIC:
    data = data[4:]
    magic = data[:4]
  
  if not magic == CMP_MAGIC:
    return
  
  dec_size = to_u32(data[4:8])
  cmp_size = to_u32(data[8:12])
  
  if len(data) < cmp_size:
    raise Exception("Compressed data not large enough.")

  res      = bytearray()
  p        = 12 # Header
  prev_off = 1
  
  while p < cmp_size:
    
    b = data[p]
    p += 1
    
    bit1 = b & 0b10000000
    bit2 = b & 0b01000000
    bit3 = b & 0b00100000
    
    # Copy data from the output buffer.
    # 1xxyyyyy yyyyyyyy
    # Count  -> x + 4
    # Offset -> y
    if bit1:
      
      b2 = data[p]
      p += 1
      
      count = ((b >> 5) & 0b011) + 4
      offset = ((b & 0b00011111) << 8) + b2
      prev_off = offset
      
      for i in range(count):
        res.append(res[-offset])
    
    # Continue copying data from the output buffer.
    # 011xxxxx
    # Count  -> x
    # Offset -> reused from above
    elif bit2 and bit3:
      
      count = (b & 0b00011111)
      offset = prev_off
      
      for i in range(count):
        res.append(res[-offset])
    
    # Insert multiple copies of the next byte.
    # 0100xxxx yyyyyyyy
    # 0101xxxx xxxxxxxx yyyyyyyy
    # Count -> x + 4
    # Data  -> y
    elif bit2 and not bit3:
      
      count = (b & 0b00001111)
      
      if b & 0b00010000:
        b = data[p]
        p += 1
        count = (count << 8) + b
      
      count += 4
      
      b = data[p]
      p += 1
      
      res += bytearray([b] * count)
    
    # Insert raw bytes from the input stream.
    # 000xxxxx
    # 001xxxxx xxxxxxxx
    # Count -> x
    elif not bit1 and not bit2:
      
      count = b & 0b00011111
      
      if bit3:
        b = data[p]
        p += 1
        count = (count << 8) + b
        
      res += data[p : p + count]
      p += count
    
    else:
      print "???"
  
  if not dec_size == len(res):
    print "Size mismatch!"
    print
    print dec_size, len(res)
    print
  
  return res

if __name__ == "__main__":
  import argparse
  
  print
  print "*****************************************************************"
  print "* Danganronpa PS Vita decompressor, written by BlackDragonHunt.  "
  print "* Special thanks to @FireyFly for helping figure out the format. "
  print "*****************************************************************"
  print
  
  parser = argparse.ArgumentParser(description = "Decompress compressed data in the Danganronpa PS Vita games.")
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
    elif os.path.isfile(in_path):
      out_dir = os.path.join(base_dir, "dec")
    else:
      split = os.path.split(base_dir)
      out_dir = os.path.join(split[0], "dec", split[1])
  
    if out_dir == base_dir:
      print "Input and output directories are the same:"
      print " ", out_dir
      print "Continuing will cause the original data to be overwritten."
      s = raw_input("Continue? y/n: ")
      if not s[:1].lower() == "y":
        continue
      print
  
    for filename in files:
      out_file = os.path.join(out_dir, filename[len(base_dir) + 1:])
      
      try:
        if dr_dec_file(filename, out_file):
          print filename
          print " -->", out_file
      
      except:
        print "Failed to decompress", filename
  
  print
  raw_input("Press Enter to exit.")

### EOF ###