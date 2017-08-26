# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

import os
from util import BinaryFile

AWB_MAGIC = "AFS2"

################################################################################

def awb_ex(filename, out_dir = None):
  
  f = BinaryFile(filename, "rb")
  
  out_dir = out_dir or os.path.splitext(filename)[0]
  
  try:
    os.makedirs(out_dir)
  except:
    pass
  
  for id, file_data in awb_ex_data(f):
    out_file = "%06d%s" % (id, guess_ext(file_data))
    out_file = os.path.join(out_dir, out_file)
    print out_file
    with open(out_file, "wb") as out:
      out.write(file_data)
  
  f.close()

################################################################################

def awb_ex_data(data):
  
  if not data.read(4) == AWB_MAGIC:
    print "Invalid AWB file."
    return
  
  unk1        = data.read(4)
  num_entries = data.get_u32()
  alignment   = data.get_u32()
  
  file_ids  = []
  file_ends = []
  
  for i in range(num_entries):
    file_id = data.get_u16()
    file_ids.append(file_id)
  
  header_end = data.get_u32()
  for i in range(num_entries):
    file_end = data.get_u32()
    file_ends.append(file_end)
  
  file_start = 0
  file_end   = header_end
  for i in range(num_entries):
    
    file_start = file_end
    if file_end % alignment > 0:
      file_start += (alignment - (file_end % alignment))
    file_end   = file_ends[i]
    
    data.seek(file_start)
    
    out_data = data.read(file_end - file_start)
    
    yield file_ids[i], out_data

################################################################################

def guess_ext(data):
  if data[:4] == "RIFF":
    return ".at9"
  elif data[:4] == "VAGp":
    return ".vag"
  elif data[:4] == "HCA\0":
    return ".hca"
  elif data[:2] == "\x80\x00":
    return ".adx"
  else:
    return ".dat"

################################################################################

if __name__ == "__main__":
  files = [
    # Retail data.
    "partition_resident_vita/sound/BGM.awb",
    "partition_resident_vita/sound/JINGLE.awb",
    "partition_resident_vita/sound/VOICE.awb",
    "partition_patch101_vita/sound/VOICE.awb",
    
    # Demo data.
    "partition_resident_vita_taiken_ja/sound/BGM.awb",
    "partition_resident_vita_taiken_ja/sound/JINGLE.awb",
    "partition_resident_vita_taiken_ja/sound/VOICE.awb",
  ]
  
  for fn in files:
    if not os.path.isfile(fn):
      continue
    
    out_dir = os.path.join("dec-audio", fn)
    awb_ex(fn, out_dir)

### EOF ###