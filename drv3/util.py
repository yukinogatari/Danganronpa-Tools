################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os
import zlib
import StringIO

class BinaryHelper(object):
  
  def get_u32(self):
    return to_u32(self.read(4))
  
  def get_u16(self):
    return to_u16(self.read(2))
  
  def get_u8(self):
    return to_u8(self.read(1))
  
  def get_u32be(self):
    return to_u32be(self.read(4))
  
  def get_u16be(self):
    return to_u16be(self.read(2))
  
  def get_bin(self, length):
    return BinaryString(self.read(length))
  
  def get_str(self, bytes_per_char = 1, encoding = None):
    bytes = []
    
    while True:
      ch = self.read(bytes_per_char)
      if ch == "\x00" * bytes_per_char:
        break
      else:
        bytes.append(ch)
    
    string = "".join(bytes)
    
    if encoding:
      string = string.decode(encoding)
    
    return string

class BinaryFile(file, BinaryHelper):
  pass

class BinaryString(StringIO.StringIO, BinaryHelper):
  pass

def to_u32(b):
  b = bytearray(b)
  return (b[3] << 24) + (b[2] << 16) + (b[1] << 8) + b[0]

def to_u16(b):
  b = bytearray(b)
  return (b[1] << 8) + b[0]

def to_u8(b):
  b = bytearray(b)
  return b[0]

def to_u32be(b):
  b = bytearray(b)
  return (b[0] << 24) + (b[1] << 16) + (b[2] << 8) + b[3]

def to_u16be(b):
  b = bytearray(b)
  return (b[0] << 8) + b[1]

def from_u32(b):
  return bytearray([
    b & 0xFF,
    (b >> 8)  & 0xFF,
    (b >> 16) & 0xFF,
    (b >> 24) & 0xFF,
  ])

def from_u16(b):
  return bytearray([
    b & 0xFF,
    (b >> 8) & 0xFF,
  ])

def from_u8(b):
  return bytearray([b & 0xFF])

def from_u32be(b):
  return bytearray([
    (b >> 24) & 0xFF,
    (b >> 16) & 0xFF,
    (b >> 8)  & 0xFF,
    b & 0xFF,
  ])

def from_u16be(b):
  return bytearray([
    (b >> 8) & 0xFF,
    b & 0xFF,
  ])

def list_all_files(dirname):
  
  if not os.path.isdir(dirname):
    return

  for item in os.listdir(dirname):
    full_path = os.path.join(dirname, item)
  
    if os.path.isfile(full_path):
      yield full_path
      
    elif os.path.isdir(full_path):
      for filename in list_all_files(full_path):
        yield filename

def zlib_inflate(data):
  decompress = zlib.decompressobj(
          # -zlib.MAX_WBITS  # see above
  )
  inflated = decompress.decompress(data)
  inflated += decompress.flush()
  return inflated

def reverse_enum(L):
  for index in reversed(xrange(len(L))):
    yield index, L[index]

### EOF ###