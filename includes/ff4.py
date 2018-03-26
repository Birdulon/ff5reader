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

from includes.snes import *
from includes.snestile import (
  generate_glyphs, generate_glyphs_large, generate_palette,
  create_tile, create_tile_indexed,
  create_tile_mode7_compressed, create_tile_mode7_compressed_indexed,
  bg_color, bg_trans,
  Canvas, Canvas_Indexed
  )


def make_character_battle_sprites(rom):
  tile_address = 0xD0000
  pig_tile_address = 0xD7000
  golbez_tile_address = 0xD7600
  anna_tile_address = 0xD7960
  palette_address = 0xE7D00
  golbez_palette_address = 0xE7EC0
  anna_palette_address = 0xE7EE0
  battle_strips = []
  for i in range(0, 14*32, 32):  # 14 regular characters. Pig, Golbez and Anna follow with different tile spacing and palette order.
    battle_strips.append(make_battle_strip(rom, palette_address+i, tile_address+(i*64), 64))  # KO sprites are here which means more tiles per strip than FFV
  battle_strips.append(make_battle_strip(rom, golbez_palette_address, golbez_tile_address, 27))
  battle_strips.append(make_battle_strip(rom, anna_palette_address, anna_tile_address, 14))
  for i in range(0, 16*32, 32):  # 16 pigs.
    battle_strips.append(make_battle_strip(rom, palette_address+i, pig_tile_address, 48))
  return battle_strips

def make_character_field_sprites(rom):
  tile_address = 0xD8000
  palette_address = 0x68000
  palettes = [generate_palette(rom, palette_address+i*16, transparent=True) for i in range(8)]
  LUT = [0, 0, 1, 2, 2, 2, 0, 1, 1, 3, 0, 1, 0, 0,  0,0,0]
  strips = []
  for p, i in zip(LUT, range(0, 17*24*32, 24*32)):  # 14 regular characters. Mini, toad, pig.
    strips.append(make_battle_strip(rom, palettes[p], tile_address+(i), 32, bpp=3))
  for palette in palettes:
    for i in range(0, 42*24*16, 24*16):  # 42 others
      strips.append(make_battle_strip(rom, palette, tile_address+(17*24*32)+(i), 16, bpp=3))
  #for i in range(0, 16*24, 24):  # 16 pigs.
    #strips.append(make_battle_strip(rom, palette_address+i, tile_address, 48))
  return strips

def make_character_portrait_sprites(rom):
  # 4x4 tiles per character, all 3bpp
  tile_address = 0xED3C0
  palette_address = 0x686D0
  palettes = [generate_palette(rom, palette_address+i*16, transparent=True) for i in range(14)]
  portrait_images = []
  for t_start in [tile_address+i*16*24 for i in range(17)]:
    canvas = Canvas_Indexed(4, 4)
    for t in range(16):
      offset = t_start+(t*24)
      canvas.draw_tile(t%4, t//4, create_tile_indexed(rom[offset:offset+24]))
    portrait_images.append(canvas)

  portraits = []
  for palette, portrait in zip(palettes, portrait_images):
    portraits.append(portrait.pixmap(palette))
  for portrait in portrait_images[14:]:  # 14, 15, 16 are Pig, Mini, Toad and use character palettes
    for palette in palettes:
      portraits.append(portrait.pixmap(palette))
  for palette in palettes:
    for portrait in portrait_images[:14]:
      portraits.append(portrait.pixmap(palette))
  return portraits
