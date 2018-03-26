'''
Functions common to SNES FFs
'''
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

from includes.helpers import *
from includes.snestile import *


def make_battle_strip(rom, palette_address, tile_address, num_tiles, bpp=4):
  if isinstance(palette_address, int):
    palette = generate_palette(rom, palette_address, transparent=True)
  else:
    palette = palette_address
  b = 24 if bpp==3 else 32
  battle_strip = Canvas(2, divceil(num_tiles, 2))
  for j in range(num_tiles):
    offset = tile_address+(j*b)
    battle_strip.draw_pixmap(j%2, j//2, create_tile(rom[offset:offset+b], palette))
  return battle_strip.pixmap()

def make_enemy_sprites(rom):
  sprites = []
  for e_id in range(0, 0x180*5, 5):
    triplane = bool(rom[0x14B180+e_id]&0x80)  # True if 3 planes, False if 4
    bytes_per_tile = 24 if triplane else 32
    tile_offset = ((((rom[0x14B180+e_id]&0x7F)<<8)| rom[0x14B181+e_id]) << 3) + 0x150000  # For whatever reason this is big endian
    pal_offset = ((((rom[0x14B182+e_id]&0x03)<<8)| rom[0x14B183+e_id]) << 4) + 0x0ED000  # For whatever reason this is big endian
    pal_size = 16 if triplane else 32
    palette = generate_palette(rom, pal_offset, pal_size, transparent=True)
    layout_id = rom[0x14B184+e_id]
    boss_layout = bool(rom[0x14B182+e_id]&0x80)
    if boss_layout:
      layout = rom[0x10D334+(layout_id<<5):0x10D334+(layout_id<<5)+32]
      sprite = Canvas(16, 16)
      for x, y in [(x,y) for y in range(16) for x in range(16)]:
        if (int.from_bytes(layout[y*2:y*2+2], 'little') & (0x8000 >> x)):
          sprite.draw_pixmap(x, y, create_tile(rom[tile_offset:tile_offset+bytes_per_tile], palette))
          tile_offset += bytes_per_tile
    else:
      layout = rom[0x10D004+(layout_id<<3):0x10D004+(layout_id<<3)+8]
      sprite = Canvas(8, 8)
      for x, y in [(x,y) for y in range(8) for x in range(8)]:
        if (layout[y] & (0x80 >> x)):
          sprite.draw_pixmap(x, y, create_tile(rom[tile_offset:tile_offset+bytes_per_tile], palette))
          tile_offset += bytes_per_tile

    # TODO: Shadow stuff
    sprites.append(sprite.pixmap(True))
  return sprites

def make_character_battle_sprites(rom):
  tile_address = 0x120000
  palette_address = 0x14A3C0
  battle_strips = []
  for i in range(0, (22*5)*32, 32):  # 22 jobs 5 characters
    battle_strips.append(make_battle_strip(rom, palette_address+i, tile_address+(i*48), 48))
  return battle_strips

def make_character_status_sprites(rom):
  tile_address = 0x149400
  palette_address = 0x14A660
  pixmaps = []
  for i in range(5):
    palette = generate_palette(rom, palette_address + (i*22*32), transparent=True)  # Freelance palette per character
    wounded = Canvas(3, 2)
    for j in range(6):
      offset = tile_address+(i*192)+(j*32)
      wounded.draw_pixmap(j%3, j//3, create_tile(rom[offset:offset+32], palette))
    pixmaps.append(wounded.pixmap())
    mini_strip = Canvas(2, 19)
    for j in range(38):
      offset = tile_address+0x3C0+(j*24)
      mini_strip.draw_pixmap(j%2, j//2, create_tile(rom[offset:offset+24], palette))
    pixmaps.append(mini_strip.pixmap())
    frog_strip = Canvas(2, 15)
    for j in range(30):
      offset = tile_address+0x750+(j*24)
      frog_strip.draw_pixmap(j%2, j//2, create_tile(rom[offset:offset+24], palette))
    pixmaps.append(frog_strip.pixmap())
  return pixmaps


def make_worldmap_subtiles(rom, tiles_address, lut_address, length=0x100):
  subtiles = []
  for i in range(length):
    pal_index = rom[lut_address+i]//16
    subtiles.append(create_tile_mode7_compressed_indexed(rom[tiles_address+i*32:tiles_address+i*32+32], pal_index))
  return subtiles

def stitch_worldmap_tiles(rom, subtiles, offset=0x0FF0C0):
  tiles = []
  for i in range(0xC0):
    canvas = Canvas_Indexed(2, 2)
    for j in range(4):
      k = indirect(rom, offset+(j*0xC0)+i, length=1)
      canvas.draw_tile(j%2, j//2, subtiles[k])
    tiles.append(canvas.image)
  return tiles

def make_worldmap_tiles(rom, tiles_address, subtiles_address, lut_address, length=0x100):
  return stitch_worldmap_tiles(rom, make_worldmap_subtiles(rom, subtiles_address, lut_address, length=length), tiles_address)

def make_worldmap_subtiles_pixmap(rom, tiles_address, lut_address, palette_address, length=0x100):
  tiles = []
  palettes = [generate_palette(rom, palette_address+i*32, transparent=True) for i in range(16)]
  for i in range(length):
    palette = palettes[rom[lut_address+i]//16]
    tiles.append(create_tile_mode7_compressed(rom[tiles_address+i*32:tiles_address+i*32+32], palette))
  return tiles

def make_worldmap_chunk(rom, id, length=256):
  i = indirect(rom, 0x0FE000+(id*2)) + 0x070000
  if id > 0x433:
    i += 0x010000
  mountains = (0x0C, 0x1C, 0x2C)
  chunk = []
  while len(chunk) < length:
    j = indirect(rom, i, 1)
    if j >= 0xC0:
      k = j-0xBF
      i += 1
      j = indirect(rom, i, 1)
      chunk += [j]*k
    elif j in mountains:
      chunk += [j, j+1, j+2]
    else:
      chunk.append(j)
    i += 1
  return chunk

def make_worldmap_chunk_pixmap(rom, id, palette_address, tiles):
  chunk = make_worldmap_chunk(rom, id)
  palette = generate_palette(rom, palette_address, length=0x320, transparent=True)
  canvas = Canvas_Indexed(len(chunk), 1, tilesize=16)
  for i, c in enumerate(chunk):
    canvas.draw_tile(i, 0, tiles[c])
  return canvas.pixmap(palette)

def make_worldmap_pixmap(rom, map_id, palette_address, tiles):
  id_offset = map_id*256
  palette = generate_palette(rom, palette_address, length=0x320, transparent=True)
  canvas = Canvas_Indexed(256, 256, tilesize=16)
  for j in range(256):
    chunk = make_worldmap_chunk(rom, j+id_offset)
    for i, c in enumerate(chunk):
      canvas.draw_tile(i, j, tiles[c])
  return canvas.pixmap(palette)

def make_field_tiles(rom, id):
  tiles_address = indirect(rom, 0x1C2D84 + id*4, length=4) + 0x1C2E24
  return [create_tile_indexed(rom[tiles_address+i*32:tiles_address+i*32+32]) for i in range(256)]

def make_field_minitiles(rom, id):
  tiles_address = indirect(rom, 0x1C0000 + id*2) + 0x1C0024
  return [create_tile_indexed(rom[tiles_address+i*16:tiles_address+i*16+16]) for i in range(256)]

def make_all_field_tiles(rom):
  return [make_field_tiles(rom, i) for i in range(40)]

def make_all_field_minitiles(rom):
  return [make_field_minitiles(rom, i) for i in range(18)]

def stitch_tileset(tiles):
  canvas = Canvas_Indexed(16, len(tiles)//16)
  for i, tile in enumerate(tiles):
    canvas.draw_tile(i%16, i//16, tile)
  return canvas

def get_field_map_tiles(rom, id):
  '''
  This is a bit of a mess of pointer chains for now, so generalising it will have to wait.
  Palette selection is probably determined by the tilemap which is outside the scope of this, so we'll just use #1.
  UPDATE: i2-i7 merely obtain a zone ID. Whoops.
  '''
  #i2 = indirect(rom, 0x0E2400 + id*2)
  #i3 = indirect(rom, 0x0E2402 + i2)*2
  #i4 = indirect(rom, 0x18E080 + i3)
  #i5 = indirect(rom, 0x18E081 + i4+4)*3
  #i6 = indirect(rom, 0x083320 + i5)
  #i7 = indirect(rom, 0x080001 + i6) & 0x03FF
  i8 = id * 0x1A
  tilesets = indirect(rom, 0x0E9C09 + i8, length=3)
  tile_index_0 = (tilesets & 0x00003F)        # (indirect(rom, 0x0E9C09 + i8) & 0x003F)
  tile_index_1 = (tilesets & 0x000FC0) >> 6   # (indirect(rom, 0x0E9C09 + i8) & 0x0FC0)>>6
  tile_index_2 = (tilesets & 0x03F000) >> 12  # (indirect(rom, 0x0E9C0A + i8) & 0x03F0)>>4
  minitile_index = (tilesets & 0xFC0000) >> 18  # (indirect(rom, 0x0E9C0A + i8) & 0x03F0)>>4
  pal_offset = indirect(rom, 0x0E9C16 + i8) * 0x100
  palette_address = 0x03BB00 + pal_offset
  palettes = [generate_palette(rom, palette_address+i*32, transparent=True) for i in range(8)]
  return tile_index_0, tile_index_1, tile_index_2, minitile_index, palettes

def make_field_map_tile_pixmap(rom, id, st_tiles, st_minitiles):
  *tiles, minitile, palettes = get_field_map_tiles(rom, id)
  p = palettes[1]
  canvas = Canvas(16, 64)
  for i, ts in enumerate(tiles):
    canvas.draw_pixmap(0, i*16, st_tiles[ts].pixmap(p))
  canvas.draw_pixmap(0, 48, st_minitiles[minitile].pixmap(p))
  return canvas.pixmap()

def decompress_battle_terrain(rom, address):
  '''
  Decompresses the tilemap for a battle background.
  Battle BGs use a type of RLE with 2byte repeat and 1byte incremental repeat.
  '''
  length = 0x500
  output = [0 for i in range(length)]
  o1 = []
  ptr = address
  while len(o1) < length//2:
    a = rom[ptr]
    ptr += 1
    if a != 0xFF:
      o1.append(a)
    else:
      repeat = rom[ptr]
      ptr += 1
      if repeat & 0x80:  # Repeat 2 tiles
        repeat &= 0x3F
        a, b = rom[ptr:ptr+2]
        ptr += 2
        o1 += [a, b]*repeat
      else:  # Incremental repeat
        a, inc = rom[ptr:ptr+2]
        ptr += 2
        if repeat & 0x40:  # Negative increment
          inc = -inc
        repeat &= 0x3F
        o1 += [a+(i*inc) for i in range(repeat)]
  o2 = [4*(1+(i>>7)) for i in o1]
  output[::2] =  [i|0x80 for i in o1[:length//2]]
  output[1::2] = [i&0xDF for i in o2[:length//2]]
  return bytes(output)

def apply_battle_terrain_flips(rom, id, battle_terrain):
  if id==0xFF:
    return battle_terrain
  ptr = indirect(rom, 0x14C736+(id*2))+0x140000
  length = len(battle_terrain)//2
  output = list(battle_terrain)
  buffer = []

  while len(buffer) < length:
    a = rom[ptr]
    ptr += 1
    if a == 0x00:
      skip = rom[ptr]
      ptr += 1
      buffer += [0]*skip*8
    else:
      for b in reversed(range(0, 8, 1)):
        buffer.append((a>>b)&0x01)

  for i in range(len(battle_terrain)//2):
    output[i*2+1] |= (buffer[i] << 6)
  return bytes(output)

def make_tilemap_pixmap(tilemap, tiles, palettes, tile_adjust=0):
  '''
  Battle bg is 64x64 map size, 8x8 tile size
  4bpp tiles
  '''
  canvas = Canvas(64, 64)
  for i in range(len(tilemap)//2):
    a, b = tilemap[i*2:(i+1)*2]
    tile_index = a|((b & 0x02) << 8)
    p = (b & 0x1C) >> 2
    priority = (b & 0x20) >> 5
    h_flip = (b & 0x40) >> 6
    v_flip = (b & 0x80) >> 7

    x = (i % 32) + 32*((i//1024) % 2)
    y = (i //32) - 32*((i//1024) % 2)
    try:
      palette = palettes[p]
      tile = tiles[(tile_index+tile_adjust)%0x80]
      tile.setColorTable(palette)
      tile_px = QPixmap.fromImage(tile)
      canvas.draw_pixmap(x, y, tile_px, h_flip, v_flip)
    except BaseException as e:
      print(e, p, hex(tile_index,2), hex(tile_adjust,2), hex(tile_index+tile_adjust,2))
  return canvas.pixmap(True)

def make_battle_backgrounds(rom):
  '''
  21 pointers in memory for the compressed data of the tilesets.
  Most of these are not unique, and only a subset of the resulting block is used.
  The block appears to get DMA'd to 0x0400 in VRAM

  Terrain gets DMA'd to 0x2000 (size 0x500) in VRAM from 0x7f0000 in RAM
  '''
  palettes = [generate_palette(rom, 0x14BB31+(i*0x20)) for i in range(84)]
  battle_bgs = []
  for i in range(34):
    bg = {
      'tiles_id':         rom[0x14BA21+(i*8)],
      'pal1_id':          rom[0x14BA22+(i*8)],
      'pal2_id':          rom[0x14BA23+(i*8)],
      'terrain_id':       rom[0x14BA24+(i*8)],
      'terrain_flips_id': rom[0x14BA25+(i*8)],
      }
    bg['palette'] = [palettes[0], palettes[bg['pal1_id']], palettes[bg['pal2_id']]]
    battle_bgs.append(bg)

  tiles_pointer_start = 0x184196
  tiles_RAM_pointer_start = 0x184157
  tiles_pointers = [indirect(rom, tiles_pointer_start+(i*3), length=3)-0xC00000 for i in range(21)]
  tiles_raw = [decompress_lzss(rom, p) for p in tiles_pointers]
  tiles_skips = [indirect(rom, tiles_RAM_pointer_start+(i*3), length=3)-0x7FC000 for i in range(21)]
  tiles = []
  for raw, skip in zip(tiles_raw, tiles_skips):
    r = raw[skip:]
    tiles.append([create_tile_indexed(r[i*32:(i+1)*32]) for i in range(len(r)//32)])

  terrain_pointer_start = 0x14C86D
  terrain_pointers = [indirect(rom, terrain_pointer_start+(i*2))+0x140000 for i in range(28)]
  terrains = [decompress_battle_terrain(rom, p) for p in terrain_pointers]

  pixmaps = []
  for bg in battle_bgs:
    terrain = apply_battle_terrain_flips(rom, bg['terrain_flips_id'], terrains[bg['terrain_id']])
    pixmaps.append(make_tilemap_pixmap(terrain, tiles[bg['tiles_id']], bg['palette']))
  #[make_tilemap_pixmap(terrains[5], tiles[2], palettes)]
  return pixmaps

def get_zone_tiles_start(rom, id):
  i1 = indirect(rom, 0x0E59C0+(id*2))+7
  i2 = indirect(rom, 0x0E59C2+i1, 1)
  # There is a divergent path here based on the value. Other things appear to be affected by this.
  if i2 > 0x67:
    i3 = ((i2 - 0x67) << 11) + 0x1A0000
  elif i2 > 0x52:
    i3 = ((i2 - 0x52) << 9) + 0x1A0000
  elif i2 > 0x4B:
    i3 = ((i2 - 0x4B) << 11) + 0x1AC800
  elif i2 > 0x32:
    i3 = ((i2 - 0x32) << 10) + 0x1A0000
  else:
    i3 = (i2 << 9) + 0x1A0000
  return i3
