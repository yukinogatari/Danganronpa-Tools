import math

# From https://github.com/xdanieldzd/Scarlet/blob/master/Scarlet/Drawing/ImageBinary.cs
# 
# Scarlet License
# 
# The MIT License (MIT)
# 
# Copyright (c) 2016 xdaniel (Daniel R.) / DigitalZero Domain
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

def Compact1By1(x):
  x &= 0x55555555 # x = -f-e -d-c -b-a -9-8 -7-6 -5-4 -3-2 -1-0
  x = (x ^ (x >> 1)) & 0x33333333 # x = --fe --dc --ba --98 --76 --54 --32 --10
  x = (x ^ (x >> 2)) & 0x0f0f0f0f # x = ---- fedc ---- ba98 ---- 7654 ---- 3210
  x = (x ^ (x >> 4)) & 0x00ff00ff # x = ---- ---- fedc ba98 ---- ---- 7654 3210
  x = (x ^ (x >> 8)) & 0x0000ffff # x = ---- ---- ---- ---- fedc ba98 7654 3210
  return x

def DecodeMorton2X(code):
  return Compact1By1(code >> 0)

def DecodeMorton2Y(code):
  return Compact1By1(code >> 1)

def PostProcessMortonUnswizzle(data, width, height, bytespp):
  data = bytearray(data)
  unswizzled = bytearray(len(data))
  
  width = int(width)
  height = int(height)
  
  min = width if width < height else height
  k = int(math.log(min, 2))
  
  for i in range(width * height):
    
    if height < width:
      j = i >> (2 * k) << (2 * k) \
        | (DecodeMorton2Y(i) & (min - 1)) << k \
        | (DecodeMorton2X(i) & (min - 1)) << 0
      
      x = j / height
      y = j % height
    
    else:
      j = i >> (2 * k) << (2 * k) \
        | (DecodeMorton2X(i) & (min - 1)) << k \
        | (DecodeMorton2Y(i) & (min - 1)) << 0
      
      x = j % width
      y = j / width
    
    p = ((y * width) + x) * bytespp
    unswizzled[p : p + bytespp] = data[i * bytespp : (i + 1) * bytespp]
  
  return unswizzled

### EOF ###