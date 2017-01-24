################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.
################################################################################

# Based on http://aluigi.altervista.org/bms/cpk.bms

from util import *
import struct

############################################################
### CONSTANTS
############################################################

CPK_MAGIC = "CPK "
TOC_MAGIC = "TOC "
UTF_MAGIC = "@UTF"

COLUMN_STORAGE_MASK     = 0xF0
COLUMN_STORAGE_PERROW   = 0x50
COLUMN_STORAGE_CONSTANT = 0x30
COLUMN_STORAGE_ZERO     = 0x10
COLUMN_TYPE_MASK        = 0x0F
COLUMN_TYPE_DATA        = 0x0B
COLUMN_TYPE_STRING      = 0x0A
COLUMN_TYPE_FLOAT       = 0x08
COLUMN_TYPE_8BYTE2      = 0x07
COLUMN_TYPE_8BYTE       = 0x06
COLUMN_TYPE_4BYTE2      = 0x05
COLUMN_TYPE_4BYTE       = 0x04
COLUMN_TYPE_2BYTE2      = 0x03
COLUMN_TYPE_2BYTE       = 0x02
COLUMN_TYPE_1BYTE2      = 0x01
COLUMN_TYPE_1BYTE       = 0x00

############################################################
### FUNCTIONS
############################################################

def query_utf(data, table_offset, index, name):
  
  old_pos = data.tell()
  data.seek(table_offset)
  
  if not data.read(4) == UTF_MAGIC:
    data.seek(old_pos)
    print "Not a @UTF table at %d" % table_offset
    return
  
  table_size        = data.get_u32be()
  schema_offset     = 0x20
  unk               = data.get_u16be()
  rows_offset       = data.get_u16be()
  str_table_offset  = data.get_u32be()
  data_offset       = data.get_u32be()
  table_name_string = data.get_u32be()
  columns           = data.get_u16be()
  row_width         = data.get_u16be()
  rows              = data.get_u32be()
  
  # print table_size, schema_offset, rows_offset, str_table_offset, data_offset, table_name_string, columns, row_width, rows
  
  # This is hacky as fuck, but I need some way to get the number of rows out, lol
  if index == -1:
    data.seek(old_pos)
    return rows
  
  schema_info = []
  
  for i in range(columns):
    schema_type  = data.get_u8()
    col_name     = data.get_u32be()
    const_offset = -1
    
    if schema_type & COLUMN_STORAGE_MASK == COLUMN_STORAGE_CONSTANT:
      const_offset = data.tell()
      
      data_type = schema_type & COLUMN_TYPE_MASK
      if data_type in [COLUMN_TYPE_DATA, COLUMN_TYPE_8BYTE2, COLUMN_TYPE_8BYTE]:
        data.read(8)
      elif data_type in [COLUMN_TYPE_STRING, COLUMN_TYPE_FLOAT, COLUMN_TYPE_4BYTE2, COLUMN_TYPE_4BYTE]:
        data.read(4)
      elif data_type in [COLUMN_TYPE_2BYTE2, COLUMN_TYPE_2BYTE]:
        data.read(2)
      elif data_type in [COLUMN_TYPE_1BYTE2, COLUMN_TYPE_1BYTE]:
        data.read(1)
      else:
        data.seek(old_pos)
        print "Unknown type for constant."
        return
    
    schema_info.append((schema_type, col_name, const_offset))
  
  str_table_start = str_table_offset + 8 + table_offset
  str_table_size  = data_offset - str_table_offset
  str_table_end   = str_table_start + str_table_size
  
  data.seek(str_table_start)
  str_table = data.get_bin(str_table_size)
  
  # print str_table_start, str_table_size
  
  for i in range(index, rows):
    row_offset = table_offset + 8 + rows_offset + (i * row_width)
    # print
    # print "*" * 40
    # print
    
    for j in range(columns):
      schema_type  = schema_info[j][0]
      col_name     = schema_info[j][1]
      const_offset = schema_info[j][2]
      
      str_table.seek(col_name)
      col_name = str_table.get_str()
      # print col_name
      
      if const_offset >= 0:
        col_offset = const_offset
      else:
        col_offset = row_offset
      
      if schema_type & COLUMN_STORAGE_MASK == COLUMN_STORAGE_ZERO:
        value = 0
      else:
        data.seek(col_offset)
        # print data.tell()
        
        type_mask = schema_type & COLUMN_TYPE_MASK
        if type_mask == COLUMN_TYPE_STRING:
          str_offset = data.get_u32be()
          str_table.seek(str_offset)
          value = str_table.get_str()
        
        elif type_mask == COLUMN_TYPE_DATA:
          vardata_offset = data.get_u32be()
          vardata_size   = data.get_u32be()
          
          # print data_offset + 8 + table_offset + vardata_offset, vardata_size
          
          if vardata_size:
            temp_pos = data.tell()
            data.seek(data_offset + 8 + table_offset + vardata_offset)
            value = data.get_bin(vardata_size)
            data.seek(temp_pos)
          
          else:
            value = None
        
        elif type_mask == COLUMN_TYPE_FLOAT:
          value = struct.unpack(">f", data.read(4))[0]
        elif type_mask == COLUMN_TYPE_8BYTE2:
          value = (data.get_u32be() << 32) | data.get_u32be()
        elif type_mask == COLUMN_TYPE_8BYTE:
          value = (data.get_u32be() << 32) | data.get_u32be()
        elif type_mask == COLUMN_TYPE_4BYTE2:
          value = data.get_u32be()
        elif type_mask == COLUMN_TYPE_4BYTE:
          value = data.get_u32be()
        elif type_mask == COLUMN_TYPE_2BYTE2:
          value = data.get_u16be()
        elif type_mask == COLUMN_TYPE_2BYTE:
          value = data.get_u16be()
        elif type_mask == COLUMN_TYPE_1BYTE2:
          value = data.get_u8()
        elif type_mask == COLUMN_TYPE_1BYTE:
          value = data.get_u8()
        else:
          data.seek(old_pos)
          print "Unknown normal type."
          return
        
        if const_offset < 0:
          row_offset = data.tell()
      ### endif ###
      
      # print value
      # print
      
      if col_name == name:
        data.seek(old_pos)
        return value
    
    # break
  
  data.seek(old_pos)
  return None

### EOF ###