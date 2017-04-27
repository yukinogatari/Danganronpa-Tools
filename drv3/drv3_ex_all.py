# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

import os

from util import list_all_files
from spc_ex import spc_ex
from rsct_ex import rsct_ex
from srd_ex import srd_ex
from stx_ex import stx_ex
from wrd_ex import wrd_ex

OUT_DIR = u"dec"

if __name__ == "__main__":
  import argparse
  
  print
  print "*****************************************************************"
  print "* New Danganronpa V3 extractor, written by BlackDragonHunt.      "
  print "*****************************************************************"
  print
  
  parser = argparse.ArgumentParser(description = "Extracts data used in New Danganronpa V3.")
  parser.add_argument("input", metavar = "<input dir>", nargs = "+", help = "An input directory.")
  parser.add_argument("-o", "--output", metavar = "<output dir>", help = "The output directory.")
  parser.add_argument("--no-crop", dest = "crop", action = "store_false", help = "Don't crop srd textures to their display dimensions.")
  args = parser.parse_args()
  
  for in_path in args.input:
    
    if os.path.isdir(in_path):
      base_dir = os.path.normpath(in_path)
      files = list_all_files(base_dir)
    else:
      continue
    
    if args.output:
      out_dir = os.path.normpath(args.output)
      out_dir = os.path.join(out_dir, os.path.basename(base_dir))
    else:
      split = os.path.split(base_dir)
      out_dir = os.path.join(split[0], OUT_DIR, split[1])
  
    if out_dir == base_dir:
      print "Input and output directories are the same:"
      print " ", out_dir
      print "Continuing will cause the original data to be overwritten."
      s = raw_input("Continue? y/n: ")
      if not s[:1].lower() == "y":
        continue
      print
    
    # Extract the SPC files.
    for filename in files:
      out_file = os.path.join(out_dir, filename[len(base_dir) + 1:])
      
      if not os.path.splitext(filename)[1].lower() == ".spc":
        continue
      
      try:
        print "Extracting", filename
        spc_ex(filename, out_file)
      
      except:
        print "Failed to unpack", filename
    
    # Now extract all the data we know how to from inside the SPC files.
    for filename in list_all_files(out_dir):
      ext = os.path.splitext(filename)[1].lower()
      
      if not ext in [".rsct", ".wrd", ".stx", ".srd"]:
        continue
      
      ex_dir, basename = os.path.split(filename)
      ex_dir   = out_dir + "-ex" + ex_dir[len(out_dir):]
      txt_file = os.path.join(ex_dir, os.path.splitext(basename)[0] + ".txt")
      
      try:
        os.makedirs(ex_dir)
      except:
        pass
      
      print
      print "Extracting", filename
      print
      
      if ext == ".rsct":
        rsct_ex(filename, txt_file)
      
      if ext == ".wrd":
        wrd_ex(filename, txt_file)
      
      if ext == ".stx":
        stx_ex(filename, txt_file)
      
      # Because we have the same extensions used for multiple different formats.
      if ext == ".srd" or ext == ".stx":
        srd_ex(filename, ex_dir, crop = args.crop)
  
  print
  raw_input("Press Enter to exit.")

### EOF ###