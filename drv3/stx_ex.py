# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

from util import *

STX_MAGIC = "STXT"

def stx_ex(filename, out_file = None):
  out_file = out_file or os.path.splitext(filename)[0] + ".txt"
  
  f = BinaryFile(filename, "rb")
  strs = stx_ex_data(f)
  f.close()
  
  if not strs:
    return
  
  out_dir = os.path.dirname(out_file)
  
  try:
    os.makedirs(out_dir)
  except:
    pass
  
  with open(out_file, "wb") as f:
    for str_id, string in strs:
      f.write("##### %04d\n\n" % str_id)
      f.write(string.encode("UTF-8"))
      f.write("\n\n")

def stx_ex_data(f):
  if not f.read(4) == STX_MAGIC:
    return []
  
  lang      = f.read(4)   # "JPLL" in the JP version, at least.
  unk       = f.get_u32() # Table count?
  table_off = f.get_u32()
  
  unk2      = f.get_u32()
  count     = f.get_u32()
  
  strs = []
  
  for i in range(count):
    f.seek(table_off + i * 8)
    str_id  = f.get_u32()
    str_off = f.get_u32()
    
    f.seek(str_off)
    
    string = f.get_str(bytes_per_char = 2, encoding = "UTF-16LE")
    strs.append((str_id, string))
  
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
      if not os.path.splitext(fn)[1].lower() == ".stx":
        continue
      
      out_dir, basename = os.path.split(fn)
      out_dir  = dirname + "-ex" + out_dir[len(dirname):]
      out_file = os.path.join(out_dir, os.path.splitext(basename)[0] + ".txt")
      
      try:
        os.makedirs(out_dir)
      except:
        pass
      
      print fn
      stx_ex(fn, out_file)

### EOF ###