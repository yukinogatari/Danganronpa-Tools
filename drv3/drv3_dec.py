# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

from util import *

# Via https://graphics.stanford.edu/~seander/bithacks.html#ReverseByteWith64BitsDiv
def bit_reverse(b):
  return (b * 0x0202020202 & 0x010884422010) % 1023

################################################################################

# This is the compression scheme used for individual files in an spc archive.

def spc_dec(data):
  
  data = bytearray(data)
  res = bytearray()
  
  flag = 1
  p = 0
  
  while p < len(data):
    
    # We use an 8-bit flag to determine whether something's raw data
    # or if we pull from the buffer, going from most to least significant bit.
    # Reverse the bit order to make it easier to work with.
    if flag == 1:
      flag = 0x100 | bit_reverse(data[p])
      p += 1
    
    if p >= len(data):
      break
    
    # Raw byte.
    if flag & 1:
      res.append(data[p])
      p += 1
    
    # Read from the buffer.
    # xxxxxxyy yyyyyyyy
    # Count  -> x + 2
    # Offset -> y (from the beginning of a 1024-byte sliding window)
    else:
      b = (data[p + 1] << 8) | data[p]
      p += 2
      
      count  = (b >> 10) + 2
      offset = b & 0b1111111111
      
      for i in range(count):
        res.append(res[offset - 1024])
    
    flag >>= 1
  
  return res

################################################################################

# This compression scheme is used globally on all the data in the game
# (including spc archives, which are already compressed as above)
# but it's structured like an srd file with the "$XXX" blocks,
# so for lack of a better term I'm just calling it srd compression. ┐(´∀｀)┌

def srd_dec(filename):
  f = BinaryFile(filename, "rb")
  res = srd_dec_data(f)
  f.close()
  return res

def srd_dec_data(f):
  res = bytearray()
  
  f.seek(0)
  magic = f.read(4)
  
  if not magic == "$CMP":
    f.seek(0)
    res = f.read()
    return res
  
  cmp_size  = f.get_u32be()
  f.read(8)
  dec_size  = f.get_u32be()
  cmp_size2 = f.get_u32be()
  f.read(4)
  unk       = f.get_u32be()
  
  while True:
    cmp_mode = f.read(4)
    
    if not cmp_mode.startswith("$CL") and not cmp_mode == "$CR0":
      break
    
    chunk_dec_size = f.get_u32be()
    chunk_cmp_size = f.get_u32be()
    f.read(4)
    
    chunk = f.read(chunk_cmp_size - 0x10)
    
    # CR0 = uncompressed
    if not cmp_mode == "$CR0":
      chunk = srd_dec_chunk(chunk, cmp_mode)
    
    res.extend(chunk)
  
  if not dec_size == len(res):
    raise Exception("%d %d" % (dec_size, len(res)))
  
  return res

def srd_dec_chunk(data, mode):
  
  data = bytearray(data)
  res  = bytearray()
  
  flag = 1
  p = 0
  
  if mode == "$CLN":
    shift = 8
  elif mode == "$CL1":
    shift = 7
  elif mode == "$CL2":
    shift = 6
  
  mask = (1 << shift) - 1
  
  while p < len(data):
    b = data[p]
    p += 1
    
    # Read from buffer.
    if b & 1:
      count = (b & mask) >> 1
      offset = ((b >> shift) << 8) | data[p]
      p += 1
      
      for i in range(count):
        res.append(res[-offset])
    
    # Raw bytes.
    else:
      count = b >> 1
      res.extend(data[p : p + count])
      p += count
  
  return res

### EOF ###