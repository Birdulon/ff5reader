#!/usr/bin/python3 -i
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

import sys
import re
from struct import unpack
from itertools import chain
from array import array
import time
import functools
from typing import Iterable

from includes.helpers import *
from includes.qthelpers import *
from includes.snestile import (
  generate_glyphs, generate_glyphs_large, generate_palette,
  create_tile, create_tile_indexed,
  create_tile_mode7_compressed, create_tile_mode7_compressed_indexed,
  bg_color, bg_trans,
  Canvas, Canvas_Indexed
  )
from includes.snes import *
import includes.ff5.const as const
from includes.ff5.strings import StringBlock, RPGe_Dialogue_Width
from includes.ff5.strings import Strings as FFVStrings
import includes.ff4 as ff4
import includes.ff5 as ff5
import includes.ff6 as ff6

filename_jp_ff4 = 'roms/Final Fantasy IV (Japan) (Rev A).sfc'
filename_jp_ff6 = 'roms/Final Fantasy VI (Japan).sfc'



class FF5Reader(QMainWindow):
  '''
  Main GUI class
  '''
  def __init__(self):
    QMainWindow.__init__(self, None)
    perfcount()
    print('Reading ROMs')
    ROM_en = ff5.files.ROM_RPGe
    ROM_jp = ff5.files.ROM_SNES
    ROM_FF4jp = load_raw(filename_jp_ff4)
    ROM_FF6jp = load_raw(filename_jp_ff6)
    print(len(ROM_FF4jp), filename_jp_ff4)
    print(len(ROM_FF6jp), filename_jp_ff6)
    perfcount()

    print('Generating Glyphs')
    self.glyph_sprites = {
      'glyphs_en_s': generate_glyphs(ROM_en, 0x11F000),
      'glyphs_en_l': generate_glyphs_large(ROM_en, 0x03E800),
      'glyphs_jp_s': generate_glyphs(ROM_jp, 0x11F000),
      'glyphs_jp_l': generate_glyphs_large(ROM_jp, 0x03E800),
      'glyphs_kanji': generate_glyphs_large(ROM_jp, 0x1BD000, 0x1AA),  # Kanji are unchanged in EN version
      }
    make_string_img_list = functools.partial(_make_string_img_list, **self.glyph_sprites)
    perfcount()

    imglist_headers = ['ID', 'EN Pointer', 'EN Address', 'EN String', 'EN Img', 'JP Pointer', 'JP Address', 'JP String', 'JP Img']

    print('Generating String Images')
    string_images = {k: make_string_img_list(*FFVStrings.blocks_SNES_RPGe[k], large=config.get('dialog')) for k,config in FFVStrings.config.items()}
    ends_in_digit = re.compile('^([\w_]+)(\d+)')
    for k in sorted(list(string_images.keys())):  # Pre-generate keys as we destructively iterate the dict
      if m := ends_in_digit.match(k):
        k0 = m[1]
        n = int(m[2])
        print(f'Collapsing strings list {k} into {k0}')
        string_images[k0] += string_images.pop(k)
    perfcount()

    battle_bg_structure = [('Tileset',     1, None),
                           ('Palette 1',   1, None),
                           ('Palette 2',   1, None),
                           ('Tilemap',     1, None),
                           ('TilemapFlip', 1, None),
                           (hex(5, 1),     1, None),
                           ('Animation',   1, None),
                           ('PaletteCycle',1, None),]
    battle_bg_headers = ['Address'] + [z[0] for z in battle_bg_structure]
    battle_bg_data = [parse_struct(ROM_jp, 0x14BA21 + (i*8), battle_bg_structure) for i in range(34)]

    tileset_headers = ("ID", "Offset", "Pointer", "Expected Length")
    tileset_data = []
    for i in range(0x1C):
      offset = 0x0F0000 + (i*2)
      pointer = 0x0F0000 + indirect(ROM_en, offset)
      length = indirect(ROM_en, offset+2) - indirect(ROM_en, offset)
      tileset_data.append((hex(i, 2), hex(offset, 6), hex(pointer, 6), hex(length, 4)))

    npc_layers = []
    offset = 0x0E59C0
    for layer in range(const.npc_layer_count):
      i = offset + (layer*2)
      start = indirect(ROM_en, i) + offset
      next = indirect(ROM_en, i+2) + offset
      npcs = (next - start) // 7
      for npc in range(npcs):
        address = start + (npc*7)
        npc_layers.append([hex(i, 6), hex(layer, 3)] + parse_struct(ROM_en, address, const.npc_layer_structure))

    enemy_sprite_data = []
    enemy_sprite_structure = [
      ('Sprite data offset', 2, None),
      ('Multiple things',    2, None),
      ('Tile Layout ID',     1, None),
      ]
    enemy_sprite_headers = ['Address']+[i[0] for i in enemy_sprite_structure]+['EN Name','EN Name']
    address = 0x14B180
    for i in range(0x180):
      enemy_sprite_data.append(parse_struct(ROM_en, address + (i*5), enemy_sprite_structure) + string_images['enemy_names'][i][3:5])

    perfcount()
    print('Generating map tiles')
    worldmap_palettes = [generate_palette(ROM_jp, 0x0FFCC0+(i*0x100), length=0x160, transparent=True) for i in range(3)]
    world_tiles = [make_worldmap_blocks(ROM_jp, 0x0FF0C0+(i*0x300), 0x1B8000+(i*0x2000), 0x0FF9C0+(i*0x100)) for i in range(3)]
    #worldpixmaps = [make_worldmap_pixmap(ROM_jp, i, 0x0FFCC0+(t*0x100), world_tiles[t]) for i, t in enumerate([0, 1, 0, 2, 2])]
    world_blocks_pixmaps = []
    for i, tiles in enumerate(world_tiles):
      a = []
      for t in tiles:
        t.setColorTable(worldmap_palettes[i])
        a.append(QPixmap.fromImage(t))
      world_blocks_pixmaps.append(a)
    world_tile_stitches = [stitch_tileset_px(t) for t in world_blocks_pixmaps]
    worldpixmaps = [make_worldmap_pixmap2(ROM_jp, i, world_tile_stitches[t]) for i, t in enumerate([0, 1, 0, 2, 2])]
    perfcount()
    worldmap_tiles = make_worldmap_tiles_pixmap(ROM_jp, 0x1B8000, 0x0FF9C0, 0x0FFCC0)
    worldmap_tiles += make_worldmap_tiles_pixmap(ROM_jp, 0x1BA000, 0x0FFAC0, 0x0FFDC0)
    worldmap_tiles += make_worldmap_tiles_pixmap(ROM_jp, 0x1BC000, 0x0FFBC0, 0x0FFEC0, length=128)
    perfcount()

    field_tiles = make_all_field_tiles(ROM_jp)
    field_minitiles = make_all_field_minitiles(ROM_jp)
    perfcount()
    st_field_tiles = [stitch_tileset(ts) for ts in field_tiles]
    st_field_minitiles = [stitch_tileset(ts) for ts in field_minitiles]
    perfcount()
    fieldmap_tiles = [make_field_map_tile_pixmap(ROM_jp, i, st_field_tiles, st_field_minitiles) for i in range(const.zone_count)]
    perfcount()
    print('Generating field map blocks')
    zones = [parse_zone(ROM_jp, i) for i in range(const.zone_count)]
    field_blocksets = [get_field_map_block_layouts(ROM_jp, i) for i in range(28)]
    perfcount()
    blockmaps = get_blockmaps(ROM_jp)
    field_blocks = []
    zone_pxs = []
    block_cache = {'misses': 0, 'p_hits': 0, 'i_hits': 0}
    zone_px_cache = {'misses': 0, 'hits': 0}

    fm_blocks = [make_field_map_blocks_px(ROM_jp, z, field_tiles, field_minitiles, field_blocksets, block_cache) for z in zones]
    #fm_blocks = [make_field_map_blocks_px2(ROM_jp, z, field_tiles, field_minitiles, field_blocksets, block_cache) for z in zones]
    print('Block cache results: {misses} misses, {p_hits} full hits, {i_hits} palette misses'.format(**block_cache))
    perfcount()
    for i, z in enumerate(zones):
      blocks, miniblocks = fm_blocks[i]
      field_blocks.append(stitch_tileset_px([b.all for b in blocks+miniblocks]))
      zone_pxs += make_zone_pxs(blocks, miniblocks, blockmaps, z, zone_px_cache)
      #zone_pxs += make_zone_pxs2(blocks, miniblocks, blockmaps, z, zone_px_cache)
    print('Zone pixmap cache results: {misses} misses, {hits} hits'.format(**zone_px_cache))
    perfcount()
    del block_cache
    del zone_px_cache

    print('Generating Battle backgrounds')
    battle_bgs = make_battle_backgrounds(ROM_jp)
    perfcount()
    print('Generating other sprites')
    self.battle_strips = make_character_battle_sprites(ROM_en)
    status_strips = make_character_status_sprites(ROM_en)
    enemy_sprites = make_enemy_sprites(ROM_en)
    enemy_sprites_named = [stack_labels(s, d[-2]) for s, d in zip(enemy_sprites, enemy_sprite_data)]
    perfcount()

    print('Generating FF4 and FF6 stuff')
    self.battle_strips_ff4 = ff4.make_character_battle_sprites(ROM_FF4jp)
    self.field_strips_ff4 = ff4.make_character_field_sprites(ROM_FF4jp)
    self.portraits_ff4 = ff4.make_character_portrait_sprites(ROM_FF4jp)
    self.battle_strips_ff6 = ff6.make_character_battle_sprites(ROM_FF6jp)
    self.portraits_ff6 = ff6.make_character_portrait_sprites(ROM_FF6jp)
    perfcount()


    print('Creating Qt Widgets')
    self.gamewidget = QTabWidget()
    self.ff4widget = QTabWidget()
    self.ff5widget = QTabWidget()
    self.ff6widget = QTabWidget()
    self.gamewidget.addTab(self.ff5widget, 'FFV')
    self.gamewidget.addTab(self.ff4widget, 'FFIV')
    self.gamewidget.addTab(self.ff6widget, 'FFVI')
    strings_tab = QTabWidget()
    structs_tab = QTabWidget()
    sprites_tab = QTabWidget()
    backgrounds_tab = QTabWidget()
    self.ff5widget.addTab(strings_tab, 'Strings')
    self.ff5widget.addTab(structs_tab, 'Structs')
    self.ff5widget.addTab(sprites_tab, 'Images')
    self.ff5widget.addTab(backgrounds_tab, 'Backgrounds')

    sprites_tab.addTab(make_px_table(self.glyph_sprites['glyphs_en_s'], scale=4), 'Glyphs (EN)')
    sprites_tab.addTab(make_px_table(self.glyph_sprites['glyphs_en_l'], scale=2), 'Glyphs (Dialogue EN)')
    sprites_tab.addTab(make_px_table(self.glyph_sprites['glyphs_jp_s'], scale=4), 'Glyphs (JP)')
    sprites_tab.addTab(make_px_table(self.glyph_sprites['glyphs_jp_l'], scale=2), 'Glyphs (Large JP)')
    sprites_tab.addTab(make_px_table(self.glyph_sprites['glyphs_kanji'], scale=2),'Glyphs (Kanji)')
    sprites_tab.addTab(make_px_table(self.battle_strips, cols=22, scale=2), 'Character Battle Sprites')
    sprites_tab.addTab(make_px_table(status_strips, cols=22, scale=2), 'Status Sprites')
    sprites_tab.addTab(make_px_table(enemy_sprites_named, cols=32, scale=1), 'Enemy Sprites')

    backgrounds_tab.addTab(make_px_table(worldmap_tiles, cols=16, scale=4), 'Worldmap Tiles')
    backgrounds_tab.addTab(make_px_table(world_blocks_pixmaps[0], cols=16, scale=4), 'World 1 Blocks')
    backgrounds_tab.addTab(make_px_table(world_blocks_pixmaps[1], cols=16, scale=4), 'World 2 Blocks')
    backgrounds_tab.addTab(make_px_table(world_blocks_pixmaps[2], cols=16, scale=4), 'Underwater Blocks')
    backgrounds_tab.addTab(make_px_table(worldpixmaps, cols=1, scale=1, large=True), 'Worldmaps')
    backgrounds_tab.addTab(make_px_table(fieldmap_tiles, cols=16, scale=1), 'Fieldmap Tiles')
    backgrounds_tab.addTab(make_px_table(field_blocks, cols=16, scale=1), 'Field Blocks')
    backgrounds_tab.addTab(make_px_table(zone_pxs, cols=4, scale=1, large=1, basicrows=True), 'Zone')
    backgrounds_tab.addTab(make_px_table(battle_bgs, cols=8, scale=1), 'Battle BGs')

    self.ff4widget.addTab(make_px_table(self.battle_strips_ff4, cols=16, scale=2), 'Character Battle Sprites')
    self.ff4widget.addTab(make_px_table(self.portraits_ff4, cols=14, scale=2), 'Character Portraits')
    self.ff4widget.addTab(make_px_table(self.field_strips_ff4, cols=17, scale=2), 'Character Field Sprites')
    self.ff6widget.addTab(make_px_table(self.battle_strips_ff6, cols=32, scale=2), 'Character Sprites')
    self.ff6widget.addTab(make_px_table(self.portraits_ff6, cols=19, scale=2), 'Character Portraits')


    structs_tab.addTab(make_table(ff5.ZoneData.zone_headers, ff5.ZoneData.get_data(), True), 'Zones')
    structs_tab.addTab(make_table(tileset_headers, tileset_data, True), 'Tilesets')
    structs_tab.addTab(make_table(battle_bg_headers, battle_bg_data, True), 'BattleBGs')
    structs_tab.addTab(make_table(const.npc_layer_headers, npc_layers, True), 'NPC Layers')
    structs_tab.addTab(make_table(enemy_sprite_headers, enemy_sprite_data, True), 'Enemy Sprites')

    for k, images in string_images.items():
      scale = 1 if FFVStrings.config[k].get('dialog') else 2
      caption = ' '.join(f'{w[0].upper()}{w[1:]}' for w in k.split('_'))
      strings_tab.addTab(make_table(imglist_headers, images, row_labels=False, scale=scale), caption)

    self.string_decoder = QWidget()
    self.decoder_input = QLineEdit()
    self.decoder_input.returnPressed.connect(self._string_decode)
    self.decoder_layout = QVBoxLayout()
    self.decoder_layout.addWidget(self.decoder_input)
    self.string_decoder.setLayout(self.decoder_layout)
    strings_tab.addTab(self.string_decoder, 'String Decoder')

    layout = QHBoxLayout()
    layout.addWidget(self.gamewidget)
    self.main_widget = QWidget(self)
    self.main_widget.setLayout(layout)
    self.main_widget.setMinimumSize(800,600)
    self.setCentralWidget(self.main_widget)
    self.show()
    perfcount()

  def _string_decode(self):
    string = ''.join(self.decoder_input.text().split())
    if len(string) % 1:
      string += '0'
    bytelist = [int(string[i:i+2], 16) for i in range(0, len(string), 2)]
    tups = make_string_img_small(bytes(bytelist), self.glyph_sprites['glyphs_en_s'])
    print(tups[0])
    img = QLabel()
    img.setPixmap(tups[1])
    self.decoder_layout.addWidget(img)
    self.decoder_input.setText('')

'''
The painting logic here needs to be moved into includes.snestile at some point.
Once that is done, these functions will be moved to includes.snes which should not have qt dependencies.
'''
def make_string_img_small(bytestring: Iterable[int], glyphs, handle_dakuten=False):
  '''
  JP version is not as fancy as this with dakuten, it just puts them on the row above and clips.
  '''
  if len(bytestring) < 1:
    return None
  img = QImage(len(bytestring)*8, 10, QImage.Format_RGB16)
  img.fill(bg_color)
  painter = QtGui.QPainter(img)
  if handle_dakuten:
    for x, j in enumerate(bytestring):
      if 0x20 <= j < 0x52:
        if j > 0x48:
          painter.drawPixmap(x*8, 2, glyphs[j+0x17])
          painter.drawPixmap(x*8+1,-5, glyphs[0x52])
        else:
          painter.drawPixmap(x*8, 2, glyphs[j+0x40])
          painter.drawPixmap(x*8+1,-6, glyphs[0x51])
      else:
        painter.drawPixmap(x*8, 2, glyphs[j])
  else:
    for x, j in enumerate(bytestring):
      painter.drawPixmap(x*8, 1, glyphs[j])
  del painter
  return QPixmap.fromImage(img)


def make_string_img_large(glyph_ids: Iterable[int], glyphs, glyphs_kanji=None):
  '''
  This is how we decipher dialogue data, which has multiple lines, macro expansions and kanji.
  English characters have varying widths. In the japanese version, everything is fullwidth (16px)
  Kanji aren't used in English dialogue but the cost is likely the same in checking either way.
  '''
  if len(glyph_ids) < 1:
    return None

  # Because the length of the input has little bearing on the size of the image thanks to linebreaks and macros, we overprovision then clip away.
  max_width = 256  # This seems to check out, but the EN dialogue has linebreaks virtually everywhere anyway
  max_height = 1024  # I've seen up to 58 rows in EN, 36 in JP. Stay safe.
  img = QImage(max_width, max_height, QImage.Format_RGB16)
  img.fill(bg_color)
  painter = QtGui.QPainter(img)

  x = xmax = y = 0
  if glyphs_kanji is not None:  # jp
    for j in glyph_ids:
      if x >= max_width:  # Wrap on long line
        xmax = max_width  # Can't go higher than this anyway
        x = 0
        y += 16

      if j == 0x01:  # Line break
        xmax = x if x > xmax else xmax
        x = 0
        y += 16
      elif 0x1E00 <= j < 0x1FAA:  # Kanji live in this range
        painter.drawPixmap(x, y+2, glyphs_kanji[j-0x1E00])
        x += 16
      elif 0x13 <= j <= 0xFF:  # Everything remaining outside this is a control char
        painter.drawPixmap(x, y+2, glyphs[j])
        x += 16
  else:  # en
    for j in glyph_ids:
      if x >= max_width:  # Wrap on long line
        xmax = max_width  # Can't go higher than this anyway
        x = 0
        y += 16

      if j == 0x01:  # Line break
        xmax = x if x > xmax else xmax
        x = 0
        y += 16
      elif 0x13 <= j <= 0xFF:  # Everything outside this is a control char
        painter.drawPixmap(x, y+4, glyphs[j])
        x += RPGe_Dialogue_Width[j]

  del painter
  xmax = x if x > xmax else xmax
  return QPixmap.fromImage(img.copy(0, 0, xmax, y+16))


def _make_string_img_list(jp: StringBlock, en: StringBlock, large=False,
                          glyphs_en_s=None, glyphs_en_l=None,
                          glyphs_jp_s=None, glyphs_jp_l=None, glyphs_kanji=None):
  num = len(en)
  print(len(en), len(jp))
  stringlist = []
  id_digits = hex_length(num-1)

  for id in range(num):
    str_en = en.decoded[id]
    str_jp = jp.decoded[id]
    if large:
      img_en = make_string_img_large(en.glyphs[id], glyphs_en_l)
      img_jp = make_string_img_large(jp.glyphs[id], glyphs_jp_l, glyphs_kanji)
    else:
      img_en = make_string_img_small(en.glyphs[id], glyphs_en_s)
      img_jp = make_string_img_small(jp.glyphs[id], glyphs_jp_s, handle_dakuten=True)
      # ['ID', 'EN Pointer', 'EN Address', 'EN String', 'EN Img', 'JP Pointer', 'JP Address', 'JP String', 'JP Img']
    stringlist.append([hex(id, id_digits), hex(en.pointer_address[id].start, 6), hex(en.string_address[id].start, 6), str_en, img_en,
                                           hex(jp.pointer_address[id].start, 6), hex(jp.string_address[id].start, 6), str_jp, img_jp])
  return stringlist

last_perfcount = None
def perfcount():
  '''
  Really basic timing for debugging
  '''
  global last_perfcount
  t = time.perf_counter()
  if last_perfcount:
    print(t-last_perfcount)
  else:
    print('perfcount initialised')
  last_perfcount = t


def main():
  app = QApplication(sys.argv)
  mainwindow = FF5Reader()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()
