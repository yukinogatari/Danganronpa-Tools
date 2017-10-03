# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

from util import *

RSCT_MAGIC = "RSCT"

def rsct_ex(filename, out_file = None):
  out_file = out_file or os.path.splitext(filename)[0] + ".txt"
  
  f = BinaryFile(filename, "rb")
  strs = rsct_ex_data(f)
  f.close()
  
  if not strs:
    return
  
  out_dir = os.path.dirname(out_file)
  
  try:
    os.makedirs(out_dir)
  except:
    pass
  
  with open(out_file, "wb") as f:
    for i, string in enumerate(strs):
      f.write(string.encode("UTF-8"))
      f.write("\n\n")

def rsct_ex_data(f):
  if not f.read(4) == RSCT_MAGIC:
    return []
  
  f.read(4) # Padding
  count = f.get_u32()
  unk   = f.get_u32() # 0x00000014
  unk2  = f.get_u32() # Table end?
  
  strs = []
  
  for i in range(count):
    f.seek(0x14 + i * 8)
    unk     = f.get_u32()
    str_off = f.get_u32()
    
    f.seek(str_off)
    
    str_len = f.get_u32()
    string  = f.read(str_len).decode("UTF-16LE").strip("\0")
    strs.append(string)
  
  return strs

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
  ]
  
  for dirname in dirs:
    for fn in list_all_files(dirname):
      if not os.path.splitext(fn)[1].lower() == ".rsct":
        continue
      
      out_dir, basename = os.path.split(fn)
      out_dir  = dirname + "-ex" + out_dir[len(dirname):]
      out_file = os.path.join(out_dir, os.path.splitext(basename)[0] + ".txt")
      
      try:
        os.makedirs(out_dir)
      except:
        pass
      
      print fn
      rsct_ex(fn, out_file)

### EOF ###