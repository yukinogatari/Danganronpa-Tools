################################################################################
# Copyright © 2016 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

import os

def to_u32(b):
  return (b[3] << 24) + (b[2] << 16) + (b[1] << 8) + b[0]

def to_u16(b):
  return (b[1] << 8) + b[0]

def from_u32(b):
  return [
    b & 0xFF,
    (b >> 8)  & 0xFF,
    (b >> 16) & 0xFF,
    (b >> 24) & 0xFF,
  ]

def from_u16(b):
  return [
    b & 0xFF,
    (b >> 8) & 0xFF,
  ]

def list_all_files(dir):

  for item in os.listdir(dir):
    full_path = os.path.join(dir, item)
  
    if os.path.isfile(full_path):
      yield full_path
      
    elif os.path.isdir(full_path):
      for filename in list_all_files(full_path):
        yield filename

### EOF ###