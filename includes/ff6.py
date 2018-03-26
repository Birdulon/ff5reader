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
  # Palettes are non-trivial for this, will need a LUT
  tile_address = 0x150000
  palette_address = 0x268000
  battle_strips = []
  for i in range(0, 16*32, 32):  # quite a few characters
    battle_strips.append(make_battle_strip(rom, palette_address+0x80, tile_address+(i*181), 181))
  tile_address += 16*181*32
  for i in range(0, 6*32, 32):  # bonus memes
    battle_strips.append(make_battle_strip(rom, palette_address+0x80, tile_address+(i*171), 171))
  tile_address += 6*171*32
  for i in range(0, 4*32, 32):  # bonus memes
    battle_strips.append(make_battle_strip(rom, palette_address+0x80, tile_address+(i*55), 55))
  tile_address += 4*55*32
  for i in range(0, 40*32, 32):  # bonus memes
    battle_strips.append(make_battle_strip(rom, palette_address+0x80, tile_address+(i*56), 56))
  return battle_strips

def make_character_portrait_sprites(rom):
  # 5x5 tiles per character, annoying arrangement but palettes are good
  tile_address = 0x2D1D00
  palette_address = 0x2D5860
  palettes = [generate_palette(rom, palette_address+i*32, transparent=True) for i in range(19)]
  # Coordinates for each tile
  LUT = [(0,0), (1,0), (2,0), (3,0), (0,2), (1,2), (2,2), (3,2), (4,0), (4,1), (4,2), (4,3), (4,4), (0,4), (1,4), (2,4), (0,1), (1,1), (2,1), (3,1), (0,3), (1,3), (2,3), (3,3), (3,4)]
  portrait_images = []
  for t_start in [tile_address+i*25*32 for i in range(19)]:
    canvas = Canvas_Indexed(5, 5)
    for t in range(25):
      offset = t_start+(t*32)
      canvas.draw_tile(*LUT[t], create_tile_indexed(rom[offset:offset+32]))
    portrait_images.append(canvas)

  portraits = []
  for palette, portrait in zip(palettes, portrait_images):
    portraits.append(portrait.pixmap(palette))
  for palette in palettes:
    for portrait in portrait_images:
      portraits.append(portrait.pixmap(palette))
  return portraits
