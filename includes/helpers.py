'''
  This file is part of ff5reader.

  ff5reader is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  ff5reader is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with ff5reader.  If not, see <http://www.gnu.org/licenses/>.
'''

HEX_PREFIX = '#'  # '#' '$' or '0x' are also nice

def divceil(numerator, denominator):
  '''
  Reverse floor division for fast ceil
  '''
  return -(-numerator // denominator)

def hex_length(i):
  '''
  String length of hexadecimal representation of integer
  '''
  return divceil(i.bit_length(), 4)

def hex(num, digits=2):
  '''
  Consolidate hex formatting for consistency
  '''
  #return '{:0{}X}₁₆'.format(num, digits)
  return HEX_PREFIX + '{:0{}X}'.format(num, digits)

def indirect(rom, start, length=2):
  '''
  Read little-endian value at start address in rom
  '''
  return int.from_bytes(rom[start:start+length], 'little')

def parse_struct(rom, offset, structure):
  '''
  Read in a section of rom with a given structure, output a list
  '''
  out = [hex(offset, 6)]
  j = 0
  for title, length, handler in structure:
    val = indirect(rom, offset+j, length=length)
    if callable(handler):
      out.append(handler(val))
    elif handler and val < len(handler):
      out.append(handler[val])
    else:
      out.append(hex(val, length*2))
    j += length
  return out


def decompress_lzss(rom, start, header=False, length=None):
  '''
  Algorithm from http://slickproductions.org/slickwiki/index.php/Noisecross:Final_Fantasy_V_Compression
  '''
  ptr = start
  if length:
    uncompressed_length = length
  else:
    uncompressed_length = indirect(rom, start)
    ptr += 2
  output = []
  buffer = [0 for i in range(0x800)]
  buffer_p = 0x07DE
  while len(output) < uncompressed_length:
    bitmap_byte = rom[ptr]
    ptr += 1
    for i in range(8):
      bit = (bitmap_byte >> i) & 1
      if bit:
        b = rom[ptr]
        ptr += 1
        output.append(b)
        buffer[buffer_p] = b
        buffer_p = (buffer_p+1) % 0x800
      else:
        b1 = rom[ptr]
        b2 = rom[ptr+1]
        ptr += 2
        offset = b1|((b2 & 0xE0)<<3)
        length = b2 & 0x1F
        for j in range(length+3):
          b = buffer[offset]
          output.append(b)
          buffer[buffer_p] = b
          buffer_p = (buffer_p+1) % 0x800
          offset = (offset+1) % 0x800
  return bytes(output[:uncompressed_length])
