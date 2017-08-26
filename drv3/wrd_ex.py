# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

from util import *

def wrd_ex(filename, out_file = None):
  out_file = out_file or os.path.splitext(filename)[0] + ".txt"
  
  f = BinaryFile(filename, "rb")
  cmds, strs = wrd_ex_data(f)
  f.close()
  
  if not strs:# and not cmds:
    return
  
  with open(out_file, "wb") as f:
    if strs:
      # f.write("########## Strings ##########\n\n")
      for i, string in enumerate(strs):
        f.write(string.encode("UTF-8"))
        f.write("\n\n")
    
    # if cmds:
    #   f.write("########## Commands ##########\n\n")
    #   for cmd in cmds:
    #     f.write(cmd.encode("UTF-8"))
    #     f.write("\n")
    #   f.write("\n")

def wrd_ex_data(f):
  str_count  = f.get_u16()
  cmd1_count = f.get_u16()
  cmd2_count = f.get_u16()
  cmd3_count = f.get_u16()
  unk        = f.get_u32() # Padding?
  unk_off    = f.get_u32()
  
  # idk
  cmd3_off   = f.get_u32()
  cmd1_off   = f.get_u32()
  cmd2_off   = f.get_u32()
  str_off    = f.get_u32()
  
  # Text is stored externally.
  if str_off == 0:
    return None, None
  
  # Code section.
  code = bytearray(f.read(unk_off - 0x20))
  
  # Code strings.
  cmd_info = [
    (cmd1_off, cmd1_count),
    (cmd2_off, cmd2_count),
    # idk what's going on with cmd3 so I'll just ignore it.
  ]
  
  cmds = []
  
  for off, count in cmd_info:
    f.seek(off)
    for i in range(count):
      str_len = f.get_u8()
      cmd = f.read(str_len).decode("UTF-8")
      f.read(1) # Null byte
      cmds.append(cmd)
  
  # Dialogue strings.
  strs = []
  
  f.seek(str_off)
  for i in range(str_count):
    str_len = f.get_u8()
    
    # ┐(´∀｀)┌
    if str_len >= 0x80:
      str_len += (f.get_u8() - 1) * 0x80
    
    str = f.read(str_len).decode("UTF-16LE")
    f.read(2) # Null byte
    strs.append(str)
  
  return cmds, strs
  
  # The IDs associated with each nametag seem to vary between files,
  # and I'm not sure how they're determined, so I'm leaving this out for now.
  
  # Put it all together.
  # lines = wrd_parse(code)
  # text  = []
  # used  = set()
  
  # for speaker, line in lines:
  #   used.add(line)
  #   line = strs[line]
    
  #   if speaker in NAMETAGS:
  #     speaker = NAMETAGS[speaker]
  #   else:
  #     speaker = "0x%04X" % speaker
    
  #   if speaker:
  #     line = u"[%s]\n%s" % (speaker, line)
    
  #   text.append(line)
  
  # for i in range(len(strs)):
  #   if not i in used:
  #     text.append(u"[UNUSED]\n" + strs[i])

def wrd_parse(data):
  lines   = []
  speaker = -1
  p       = 0
  
  # We need a minimum of four bytes for a nametag or a text display command.
  while p <= len(data) - 4:
    b = data[p]
    p += 1
    
    if not b == 0x70:
      continue
    
    cmd = data[p]
    p += 1
    
    if cmd == 0x46 or cmd == 0x58:
      line = to_u16be(data[p : p + 2])
      lines.append((speaker, line))
      p += 2
    
    elif cmd == 0x1D or cmd == 0x53:
      speaker = to_u16be(data[p : p + 2])
      p += 2
  
  return lines

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
      if not os.path.splitext(fn)[1].lower() == ".wrd":
        continue
      
      out_dir, basename = os.path.split(fn)
      out_dir  = dirname + "-ex" + out_dir[len(dirname):]
      out_file = os.path.join(out_dir, os.path.splitext(basename)[0] + ".txt")
      
      try:
        os.makedirs(out_dir)
      except:
        pass
      
      print fn
      wrd_ex(fn, out_file)

### EOF ###