# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

from util import *
from awb_ex import *
from query_utf import query_utf

def parse_acb(filename):
  f = BinaryFile(filename, "rb")
  
  awb_file = query_utf(f, 0, 0, "AwbFile")
  cue_name_table = query_utf(f, 0, 0, "CueNameTable")
  
  rows = query_utf(cue_name_table, 0, -1, "")
  
  names = []
  
  for i in range(rows):
    cue_id   = query_utf(cue_name_table, 0, i, "CueIndex")
    cue_name = query_utf(cue_name_table, 0, i, "CueName")
    
    # names.append((cue_id, cue_name))
    names.append(cue_name)
    
    # print i, cue_id, cue_name
  
  f.close()
  return names, awb_file
  
if __name__ == "__main__":
  dirs = [
    # Retail data
    "partition_resident_vita",
    "partition_patch101_vita",
    "partition_patch102_vita",
    
    # Demo data
    "partition_resident_vita_taiken_ja",
    
    # PC demo
    "partition_resident_win_demo",
  ]
  
  for base_dir in dirs:
    dirname = os.path.join("dec", base_dir)
    for fn in list_all_files(dirname):
      if not os.path.splitext(fn)[1].lower() == ".acb":
        continue
      
      print fn
      names, awb_file = parse_acb(fn)
      
      basename = os.path.splitext(os.path.basename(fn))[0]
      awb_path = os.path.join(base_dir, "sound", basename + ".awb")
      
      if os.path.isfile(awb_path):
        out_dir = os.path.join("dec", base_dir + "-ex", "sound", basename + ".awb")
        awb_file = BinaryFile(awb_path, "rb")
      elif awb_file == None:
        continue
      else:
        out_dir = fn[len(dirname) + 1:]
        out_dir = os.path.join(dirname + "-ex", out_dir)
      
      try:
        os.makedirs(out_dir)
      except:
        pass
      
      for id, file_data in awb_ex_data(awb_file):
        name = names[id] + guess_ext(file_data)
        out_file = os.path.join(out_dir, name)
        
        print out_file
        with open(out_file, "wb") as f:
          f.write(file_data)
      
      awb_file.close()

### EOF ###