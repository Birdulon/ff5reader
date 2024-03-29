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
from collections import namedtuple

Zone = namedtuple('Zone', 'npcs name shadowflags blockset tilesets blockmaps pal palette music')
Block = namedtuple('Block', 'priority0 priority1 all')
TileMapping = namedtuple('TileMapping', 'tile palette h_flip v_flip priority')

def parse_zone(rom, id, start_address=0x0E9C00):
  ptr = start_address+(id*0x1A)
  npcs = indirect(rom, ptr)
  name = rom[ptr+2]
  shadowflags = rom[ptr+3]
  blockset = rom[ptr+8]
  tilesets_b = indirect(rom, ptr+9, length=3)
  tilesets = [(tilesets_b & 0x00003F),
              (tilesets_b & 0x000FC0) >> 6,
              (tilesets_b & 0x03F000) >> 12,
              (tilesets_b & 0xFC0000) >> 18]
  blockmaps_b = indirect(rom, ptr+0xC, length=4)
  blockmaps = [(blockmaps_b & 0x000003FF) - 1,
              ((blockmaps_b & 0x000FFC00) >> 10) - 1,
              ((blockmaps_b & 0x3FF00000) >> 20) - 1]
  pal = rom[ptr+0x16]
  pal_address = 0x03BB00 + (pal<<8)
  palettes = [generate_palette(rom, pal_address+i*32, transparent=True) for i in range(8)]
  music = rom[ptr+0x19]
  return Zone(npcs, name, shadowflags, blockset, tilesets, blockmaps, pal, palettes, music)

'''
This is a bit of a mess of pointer chains for now, so generalising it will have to wait.
UPDATE: i2-i7 merely obtain a zone ID. Whoops.
'''
#i2 = indirect(rom, 0x0E2400 + id*2)
#i3 = indirect(rom, 0x0E2402 + i2)*2
#i4 = indirect(rom, 0x18E080 + i3)
#i5 = indirect(rom, 0x18E081 + i4+4)*3
#i6 = indirect(rom, 0x083320 + i5)
#i7 = indirect(rom, 0x080001 + i6) & 0x03FF


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

def make_battle_strip2(rom, palette_address, tile_address, num_tiles, bpp=4):
  '''
  Makes strips using the tile layouts
  '''
  layout_address = 0x14B997
  num_layouts = 11
  if isinstance(palette_address, int):
    palette = generate_palette(rom, palette_address, transparent=True)
  else:
    palette = palette_address
  b = 24 if bpp==3 else 32
  tiles = [create_tile(rom[offset:offset+b], palette) for offset in range(tile_address, tile_address+(b*num_tiles), b)]
  battle_strip = Canvas(2, num_layouts*3)
  for j, offset in enumerate(range(layout_address, layout_address+(num_layouts*6))):
    battle_strip.draw_pixmap(j%2, j//2, tiles[rom[offset]])
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
    #battle_strips.append(make_battle_strip(rom, palette_address+i, tile_address+(i*48), 48))
    battle_strips.append(make_battle_strip2(rom, palette_address+i, tile_address+(i*48), 48))
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


def make_worldmap_tiles(rom, tiles_address, lut_address, length=0x100):
  subtiles = []
  for i in range(length):
    pal_index = rom[lut_address+i]//16
    subtiles.append(create_tile_mode7_compressed_indexed(rom[tiles_address+i*32:tiles_address+i*32+32], pal_index))
  return subtiles

def stitch_worldmap_tiles(rom, tiles, offset=0x0FF0C0):
  blocks = []
  for i in range(0xC0):
    canvas = Canvas_Indexed(2, 2)
    for j in range(4):
      k = indirect(rom, offset+(j*0xC0)+i, length=1)
      canvas.draw_tile(j%2, j//2, tiles[k])
    blocks.append(canvas.image)
  return blocks

def make_worldmap_blocks(rom, blocks_address, tiles_address, lut_address, length=0x100):
  return stitch_worldmap_tiles(rom, make_worldmap_tiles(rom, tiles_address, lut_address, length=length), blocks_address)

def make_worldmap_tiles_pixmap(rom, tiles_address, lut_address, palette_address, length=0x100):
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

def make_worldmap_pixmap(rom, map_id, palette_address, tiles):
  id_offset = map_id*256
  palette = generate_palette(rom, palette_address, length=0x320, transparent=True)
  canvas = Canvas_Indexed(256, 256, tilesize=16)
  for j in range(256):
    chunk = make_worldmap_chunk(rom, j+id_offset)
    for i, c in enumerate(chunk):
      canvas.draw_tile(i, j, tiles[c])
  return canvas.pixmap(palette)

def make_worldmap_pixmap2(rom, map_id, tiles):
  '''
  Batched version using QPainter.drawPixmapFragments
  Tiles is a pixmap tilemap.
  '''
  id_offset = map_id*256
  canvas = Canvas(256, 256, tilesize=16)
  fragments = []
  for j in range(256):
    chunk = make_worldmap_chunk(rom, j+id_offset)
    for i, c in enumerate(chunk):
      fragments.append(make_pixmapfragment(c, i, j))
  canvas.drawPixmapFragments(fragments, tiles)
  return canvas.pixmap()

def make_field_tiles(rom, id):
  tiles_address = indirect(rom, 0x1C2D84 + id*4, length=4) + 0x1C2E24
  return [create_tile_indexed(rom[tiles_address+i*32:tiles_address+(i+1)*32]) for i in range(256)]

def make_field_minitiles(rom, id):
  tiles_address = indirect(rom, 0x1C0000 + id*2) + 0x1C0024
  return [create_tile_indexed(rom[tiles_address+i*16:tiles_address+(i+1)*16]) for i in range(256)]

def make_all_field_tiles(rom):
  return [make_field_tiles(rom, i) for i in range(40)]

def make_all_field_minitiles(rom):
  return [make_field_minitiles(rom, i) for i in range(18)]

def stitch_tileset(tiles):
  canvas = Canvas_Indexed(16, len(tiles)//16, tilesize=tiles[0].width())
  for i, tile in enumerate(tiles):
    canvas.draw_tile(i%16, i//16, tile)
  return canvas

def stitch_set(data):
  '''
  For stitching slabs of VRAM
  '''
  canvas = Canvas_Indexed(1, len(data), tilesize=data[0].width())
  for i, d in enumerate(data):
    canvas.draw_tile(0, i, d)
  return canvas

def stitch_tileset_px(tiles_px):
  canvas = Canvas(16, len(tiles_px)//16, tilesize=tiles_px[0].width())
  for i, tile in enumerate(tiles_px):
    canvas.draw_pixmap(i%16, i//16, tile)
  return canvas.pixmap()

def make_field_map_tile_pixmap(rom, id, st_tiles, st_minitiles):
  #*tiles, minitile, palettes = get_field_map_tiles(rom, id)
  zone = parse_zone(rom, id)
  p = zone.palette[1]
  canvas = Canvas(16, 64)
  for i, ts in enumerate(zone.tilesets[:-1]):
    canvas.draw_pixmap(0, i*16, st_tiles[ts].pixmap(p))
  canvas.draw_pixmap(0, 48, st_minitiles[zone.tilesets[-1]].pixmap(p))
  return canvas.pixmap()

def get_field_map_block_layouts(rom, id, start_address=0x0F0000):
  ptr = indirect(rom, start_address+(id*2)) + start_address
  data = decompress_lzss(rom, ptr)
  output = []
  for i in range(0, 0x200, 2):
    output.append([data[j+i+k] for j in range(0, 0x800, 0x200) for k in range(2)])
  return output

def make_field_map_blocks_px(rom, zone, tilesets, minitilesets, blocksets, cache):
  cache_key_i = '{} {}'.format(' '.join([str(i) for i in zone.tilesets]), zone.blockset)
  cache_key_p = '{} {}'.format(cache_key_i, zone.pal)
  if cache_key_p in cache:
    cache['p_hits'] += 1
    return cache[cache_key_p]
  elif cache_key_i in cache:
    cache['i_hits'] += 1
    blocks, miniblocks = cache[cache_key_i]
  else:
    cache['misses'] += 1
    *i_tiles, i_minitiles = zone.tilesets
    tiles = tilesets[i_tiles[0]] + tilesets[i_tiles[1]] + tilesets[i_tiles[2]]
    minitiles = minitilesets[i_minitiles]
    blockset = blocksets[zone.blockset]
    blockset_parsed = [[parse_tileset_word(tm[i*2:(i+1)*2]) for i in range(len(tm)//2)] for tm in blockset]
    blocks = [Block(*make_block(bs, tiles)) for bs in blockset_parsed]
    miniblocks = [Block(*make_block(bs, minitiles, tile_modulo=len(minitiles))) for bs in blockset_parsed]
    cache[cache_key_i] = (blocks, miniblocks)

  blocks_px = [Block(*[i.pixmap(zone.palette) for i in b]) for b in blocks]
  miniblocks_px = [Block(*[i.pixmap(zone.palette) for i in b]) for b in miniblocks]
  cache[cache_key_p] = (blocks_px, miniblocks_px)
  return blocks_px, miniblocks_px

def make_block(tilemap, tiles, cols=2, rows=2, tile_adjust=0, pal_adjust=0, tile_modulo=0x1000):
  canvases = (Canvas_Indexed(cols, rows), Canvas_Indexed(cols, rows), Canvas_Indexed(cols, rows))
  for i, tm in enumerate(tilemap):
    x = i % cols
    y = i //cols
    try:
      tile = tiles[(tm.tile+tile_adjust)%tile_modulo]
      canvases[tm.priority].draw_tile(x, y, tile, tm.h_flip, tm.v_flip, tm.palette+pal_adjust)
      canvases[2].draw_tile(x, y, tile, tm.h_flip, tm.v_flip, tm.palette+pal_adjust)
    except BaseException as e:
      print(e, tm.palette, hex(tm.tile,2), hex(tile_adjust,2), hex(tm.tile+tile_adjust,2))
  return canvases

def make_field_map_blocks_px2(rom, zone, tilesets, minitilesets, blocksets, cache):
  '''
  Batched version.
  '''
  cache_key_i = '{} {}'.format(' '.join([str(i) for i in zone.tilesets]), zone.blockset)
  cache_key_p = '{} {}'.format(cache_key_i, zone.pal)
  if cache_key_p in cache:
    cache['p_hits'] += 1
    return cache[cache_key_p]
  elif cache_key_i in cache:
    cache['i_hits'] += 1
    blocks, miniblocks = cache[cache_key_i]
  else:
    cache['misses'] += 1
    *i_tiles, i_minitiles = zone.tilesets
    tiles = tilesets[i_tiles[0]] + tilesets[i_tiles[1]] + tilesets[i_tiles[2]]
    minitiles = minitilesets[i_minitiles]
    blockset = blocksets[zone.blockset]
    blockset_parsed = [[parse_tileset_word(tm[i*2:(i+1)*2]) for i in range(len(tm)//2)] for tm in blockset]
    l = len(blockset_parsed)
    blocks_l = [None]*l*3
    for i, bs in enumerate(blockset_parsed):
      blocks_l[i], blocks_l[i+l], blocks_l[i+(2*l)] = [b.image for b in make_block(bs, tiles)]
    miniblocks_l = [None]*l*3
    for i, bs in enumerate(blockset_parsed):
      miniblocks_l[i], miniblocks_l[i+l], miniblocks_l[i+(2*l)] = [b.image for b in make_block(bs, minitiles, tile_modulo=len(minitiles))]
    blocks = stitch_tileset(blocks_l)
    miniblocks = stitch_tileset(miniblocks_l)
    cache[cache_key_i] = (blocks, miniblocks)

  blocks_px = blocks.pixmap(zone.palette)
  miniblocks_px = miniblocks.pixmap(zone.palette)
  cache[cache_key_p] = (blocks_px, miniblocks_px)
  return blocks_px, miniblocks_px

def get_blockmap(rom, address):
  if rom[address] == 0:
    return decompress_lzss(rom, address)
  else:  # Special case - the entire map is one block type (e.g. water layer)
    return [rom[address]]*0x1000

def get_blockmaps(rom, start_address=0x0B0000, num=0x148):
  bank = 0x0B0000
  ptrs = [indirect(rom, start_address)+bank]
  for i in range(1, num):
    ptr = indirect(rom, start_address+(i*2))
    if (ptr+bank) < ptrs[-1]:
      bank += 0x010000
    ptrs.append(ptr+bank)
  blockmaps = [get_blockmap(rom, ptr) for ptr in ptrs]
  return blockmaps

def make_zone_pxs(blocks, miniblocks, blockmaps, zone, cache):
  cache_key = '{} {} {}'.format(' '.join([str(i) for i in zone.blockmaps+zone.tilesets]), zone.blockset, zone.pal)
  if cache_key in cache:
    cache['hits'] += 1
    return cache[cache_key]
  else:
    cache['misses'] += 1
    output = []
    layers = [None, None, None, None, None, None]  # bg1.0 bg1.1 bg2.0 bg2.1 bg3.0 bg3.1
    order = [4, 2, 0, 3, 1, 5]  # Draw order from http://problemkaputt.de/fullsnes.htm#snespictureprocessingunitppu
    for i, i_b in enumerate(zone.blockmaps):
      if i_b == -1:
        output.append(None)
      else:
        canvases = (Canvas(64, 64, tilesize=16), Canvas(64, 64, tilesize=16), Canvas(64, 64, tilesize=16))
        _blocks = blocks if i < 2 else miniblocks
        for j, b in enumerate(blockmaps[i_b]):
          block = _blocks[b]
          canvases[0].draw_pixmap(j%64, j//64, block.priority0)
          canvases[1].draw_pixmap(j%64, j//64, block.priority1)
        canvases[2].draw_pixmap(0, 0, canvases[0].pixmap())
        canvases[2].draw_pixmap(0, 0, canvases[1].pixmap())
        output.append(canvases[2].pixmap())
        layers[i*2:(i+1)*2] = canvases[0:2]
    canvas = Canvas(64, 64, tilesize=16)
    for i in order:
      if layers[i]:
        canvas.draw_pixmap(0, 0, layers[i].pixmap())
    output.append(canvas.pixmap())
    cache[cache_key] = output
    return output

def make_zone_pxs2(blocks, miniblocks, blockmaps, zone, cache):
  '''
  Batched version
  blocks and miniblocks are a single pixmap each
  '''
  cache_key = '{} {} {}'.format(' '.join([str(i) for i in zone.blockmaps+zone.tilesets]), zone.blockset, zone.pal)
  if cache_key in cache:
    cache['hits'] += 1
    return cache[cache_key]
  else:
    cache['misses'] += 1
    output = []
    layers = []  # bg1.0 bg1.1 bg2.0 bg2.1 bg3.0 bg3.1
    order = [4, 2, 0, 3, 1, 5]  # Draw order from http://problemkaputt.de/fullsnes.htm#snespictureprocessingunitppu
    for i, i_b in enumerate(zone.blockmaps):
      if i_b == -1:
        layers += [None, None]
        output.append(None)
      else:
        canvases = (Canvas(64, 128, tilesize=16), Canvas(64, 64, tilesize=16))
        _blocks = blocks if i < 2 else miniblocks
        pxlist = []
        append = pxlist.append
        for j, b in enumerate(blockmaps[i_b]):
          x = j%64
          y = j//64
          #append(make_pixmapfragment(b, x, y))
          #append(make_pixmapfragment(b+0x100, x, y+64))
          append(QtGui.QPainter.PixmapFragment.create(QtCore.QPoint(x*16, y*16), QtCore.QRectF((b%16)*16, (b//16)*16, 16, 16)))
          append(QtGui.QPainter.PixmapFragment.create(QtCore.QPoint(x*16, y*16+1024), QtCore.QRectF((b%16)*16, (b//16)*16+0x100, 16, 16)))
        canvases[0].drawPixmapFragments(pxlist, _blocks)
        _layers = [canvases[0].pixmap(rect=(0, 0, 1024, 1024)), canvases[0].pixmap(rect=(0, 1024, 1024, 1024))]
        canvases[1].draw_pixmap(0, 0, _layers[0])
        canvases[1].draw_pixmap(0, 0, _layers[1])
        output.append(canvases[1].pixmap())
        layers += _layers
    canvas = Canvas(64, 64, tilesize=16)
    for i in order:
      if layers[i]:
        canvas.draw_pixmap(0, 0, layers[i])
    output.append(canvas.pixmap())
    cache[cache_key] = output
    return output

def decompress_battle_tilemap(rom, address):
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

def apply_battle_tilemap_flips(rom, id, tilemap):
  if id==0xFF:
    return tilemap
  ptr = indirect(rom, 0x14C736+(id*2))+0x140000
  length = len(tilemap)//2
  output = list(tilemap)
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

  for i in range(len(tilemap)//2):
    output[i*2+1] |= (buffer[i] << 6)
  return bytes(output)

def parse_OAM_word(data):
  # Note that x has a ninth bit stored in the small OAM table (bits 1,3,5...)
  x, y, a, b = data[:4]
  tile_index = a|((b & 0x01) << 8)
  palette = (b & 0x0E) >> 1
  priority = (b & 0x30) >> 4
  h_flip = (b & 0x40) >> 6
  v_flip = (b & 0x80) >> 7
  return x, y, TileMapping(tile_index, palette, h_flip, v_flip, priority)

def parse_tileset_word(data):
  a, b = data[:2]
  tile_index = a|((b & 0x03) << 8)
  palette = (b & 0x1C) >> 2
  priority = (b & 0x20) >> 5
  h_flip = (b & 0x40) >> 6
  v_flip = (b & 0x80) >> 7
  return TileMapping(tile_index, palette, h_flip, v_flip, priority)

def make_tilemap_canvas(tilemap, tiles, cols=64, rows=64, tile_adjust=0, pal_adjust=-1, tile_modulo=0x80):
  '''
  Battle bg is 64x64 map size, 8x8 tile size
  4bpp tiles
  '''
  canvas = Canvas_Indexed(cols, rows)
  for i in range(len(tilemap)//2):
    tm = parse_tileset_word(tilemap[i*2:(i+1)*2])
    if cols > 32:
      x = (i % 32) + 32*((i//1024) % 2)
      y = (i //32) - 32*((i//1024) % 2)
    else:
      x = i % cols
      y = i //cols
    try:
      tile = tiles[(tm.tile+tile_adjust)%tile_modulo]
      canvas.draw_tile(x, y, tile, tm.h_flip, tm.v_flip, tm.palette+pal_adjust)
    except BaseException as e:
      print(e, tm.palette, hex(tm.tile,2), hex(tile_adjust,2), hex(tm.tile+tile_adjust,2))
  return canvas

def make_tilemap_pixmap(tilemap, tiles, palettes, cols=64, rows=64, tile_adjust=0, pal_adjust=-1):
  '''
  Battle bg is 64x64 map size, 8x8 tile size
  4bpp tiles
  '''
  canvas = Canvas(cols, rows)
  for i in range(len(tilemap)//2):
    tile_index, p, h_flip, v_flip, priority = parse_tileset_word(tilemap[i*2:(i+1)*2])
    if cols > 32:
      x = (i % 32) + 32*((i//1024) % 2)
      y = (i //32) - 32*((i//1024) % 2)
    else:
      x = i % cols
      y = i //cols
    try:
      palette = palettes[p+pal_adjust]
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
  '''
  palettes = [generate_palette(rom, 0x14BB31+(i*0x20)) for i in range(84)]
  battle_bgs = []
  for i in range(34):
    bg = {
      'tileset_id':       rom[0x14BA21+(i*8)],
      'pal1_id':          rom[0x14BA22+(i*8)],
      'pal2_id':          rom[0x14BA23+(i*8)],
      'tilemap_id':       rom[0x14BA24+(i*8)],
      'tilemap_flips_id': rom[0x14BA25+(i*8)],
      'tilecycle_id':     rom[0x14BA27+(i*8)],
      'palcycle_id':      rom[0x14BA28+(i*8)],
      }
    bg['palette'] = palettes[bg['pal1_id']] + palettes[bg['pal2_id']]
    battle_bgs.append(bg)

  tileset_pointer_start = 0x184196
  tileset_RAM_pointer_start = 0x184157
  tileset_pointers = [indirect(rom, tileset_pointer_start+(i*3), length=3)-0xC00000 for i in range(21)]
  tileset_raw = [decompress_lzss(rom, p) for p in tileset_pointers]
  tileset_skips = [indirect(rom, tileset_RAM_pointer_start+(i*3), length=3)-0x7FC000 for i in range(21)]
  tileset = []
  for raw, skip in zip(tileset_raw, tileset_skips):
    r = raw[skip:]
    tileset.append([create_tile_indexed(r[i*32:(i+1)*32]) for i in range(len(r)//32)])

  tilemap_pointer_start = 0x14C86D
  tilemap_pointers = [indirect(rom, tilemap_pointer_start+(i*2))+0x140000 for i in range(28)]
  tilemaps = [decompress_battle_tilemap(rom, p) for p in tilemap_pointers]

  animation_ptr_start = 0x14C5B1
  animation_ptrs = [indirect(rom, animation_ptr_start+(i*2))+0x140000 for i in range(8)]
  animations = []
  for ptr in animation_ptrs:
    a = []
    for i in range(ptr, ptr+200):
      b = rom[i]
      if b == 0xFF:
        break
      a.append(b)
    a = [(i, j) for i, j in zip(a[0::2], a[1::2])]
    animations.append(a)
  animation_time = 8  # Frames before changing

  pal_cycle_ptr_start = 0x14C6CD
  pal_cycle_ptrs = [indirect(rom, pal_cycle_ptr_start+(i*2))+0x140000 for i in range(3)]
  pal_cycles = []
  for ptr in pal_cycle_ptrs:
    a = []
    for i in range(ptr, ptr+100):
      b = rom[i]
      if b == 0xFF:
        break
      a.append(b)
    pal_cycles.append(a)

  def make_pals(bg):
    p_cycle = pal_cycles[bg['palcycle_id']]
    p1 = bg['pal1_id']
    p2 = bg['pal2_id']
    pals = []
    for p in p_cycle:
      if p & 0x80:
        p2 = min(p & 0x7F, len(palettes)-1)
      else:
        p1 = min(p, len(palettes)-1)
      pals.append(palettes[p1] + palettes[p2])
    return pals

  canvases = []
  pixmaps = []
  for bg in battle_bgs:
    tilemap = apply_battle_tilemap_flips(rom, bg['tilemap_flips_id'], tilemaps[bg['tilemap_id']])
    if bg['tilecycle_id'] > 0:
      tss = [[t for t in tileset[bg['tileset_id']]] for i in range(4)]
      for i, tile2 in animations[bg['tilecycle_id']]:
        frame = i >> 6
        tile = i & 0x3F
        tss[frame][tile] = tileset[bg['tileset_id']][tile2]
      canvases.append([make_tilemap_canvas(tilemap, ts) for ts in tss])
      if bg['palcycle_id'] < 3:
        pals = make_pals(bg)
        pl = len(pals)
        cl = (animation_time*4)
        px = [canvases[-1][0].pixmap(pals[0], True)]
        i = 1
        while (i%pl != 0) or (i%cl != 0):
          px.append(canvases[-1][(i//animation_time)%4].pixmap(pals[i%pl], True))
          i += 1
        pixmaps.append(px + [1])
      else:
        pixmaps.append([c.pixmap(bg['palette'], True) for c in canvases[-1]]+[animation_time])
    else:
      canvases.append(make_tilemap_canvas(tilemap, tileset[bg['tileset_id']]))
      if bg['palcycle_id'] < 3:
        pals = make_pals(bg)
        pixmaps.append([canvases[-1].pixmap(p, True) for p in pals]+[1])
      else:
        pixmaps.append(canvases[-1].pixmap(bg['palette'], True))
  return pixmaps

def get_zone_tileset_start(rom, id):
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
