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
import time
from functools import cached_property
from struct import unpack
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
from includes.ff5.files import ROM_RPGe, ROM_SNES
from includes.ff5.strings import StringBlock, RPGe_Dialogue_Width
from includes.ff5.strings import Strings as FFVStrings
import includes.ff5.structs as FFVStructs
import includes.ff4 as ff4
import includes.ff5 as ff5
import includes.ff6 as ff6

filename_jp_ff4 = 'roms/Final Fantasy IV (Japan) (Rev A).sfc'
filename_jp_ff6 = 'roms/Final Fantasy VI (Japan).sfc'



class FF5Reader(QMainWindow):
  '''
  Main GUI class
  '''

  @cached_property
  def battle_strips_ff4(self):
    return ff4.make_character_battle_sprites(self.ROM_FF4jp)

  @cached_property
  def field_strips_ff4(self):
    return ff4.make_character_field_sprites(self.ROM_FF4jp)

  @cached_property
  def portraits_ff4(self):
    return ff4.make_character_portrait_sprites(self.ROM_FF4jp)

  @cached_property
  def battle_strips_ff6(self):
    return ff6.make_character_battle_sprites(self.ROM_FF6jp)

  @cached_property
  def portraits_ff6(self):
    return ff6.make_character_portrait_sprites(self.ROM_FF6jp)

  @cached_property
  def battle_bgs(self):
    return make_battle_backgrounds(ROM_SNES)

  @cached_property
  def battle_strips(self):
    return make_character_battle_sprites(ROM_RPGe)

  @cached_property
  def status_strips(self):
    return make_character_status_sprites(ROM_RPGe)

  @cached_property
  def enemy_sprites(self):
    return make_enemy_sprites(ROM_RPGe)

  @cached_property
  def enemy_sprite_data(self):
    return FFVStructs.EnemySprite.get_data(ROM_RPGe)

  @cached_property
  def enemy_sprites_named(self):
    return [stack_labels(s, d[-2]) for s, d in zip(self.enemy_sprites, self.enemy_sprite_data)]

  @cached_property
  def field_tiles(self):
    return make_all_field_tiles(ROM_SNES)

  @cached_property
  def field_minitiles(self):
    return make_all_field_minitiles(ROM_SNES)

  @cached_property
  def fieldmap_tiles(self):
    st_field_tiles = [stitch_tileset(ts) for ts in self.field_tiles]
    st_field_minitiles = [stitch_tileset(ts) for ts in self.field_minitiles]
    return [make_field_map_tile_pixmap(ROM_SNES, i, st_field_tiles, st_field_minitiles) for i in range(const.zone_count)]

  @cached_property
  def glyph_sprites(self):
    return {
      'glyphs_en_s': generate_glyphs(ROM_RPGe, 0x11F000),
      'glyphs_en_l': generate_glyphs_large(ROM_RPGe, 0x03E800),
      'glyphs_jp_s': generate_glyphs(ROM_SNES, 0x11F000),
      'glyphs_jp_l': generate_glyphs_large(ROM_SNES, 0x03E800),
      'glyphs_kanji': generate_glyphs_large(ROM_SNES, 0x1BD000, 0x1AA),  # Kanji are unchanged in EN version
    }

  @cached_property
  def worldmap_palettes(self):
    return [generate_palette(ROM_SNES, 0x0FFCC0+(i*0x100), length=0x160, transparent=True) for i in range(3)]

  @cached_property
  def worldmap_tiles(self):
    return make_worldmap_tiles_pixmap(ROM_SNES, 0x1B8000, 0x0FF9C0, 0x0FFCC0) + \
           make_worldmap_tiles_pixmap(ROM_SNES, 0x1BA000, 0x0FFAC0, 0x0FFDC0) + \
           make_worldmap_tiles_pixmap(ROM_SNES, 0x1BC000, 0x0FFBC0, 0x0FFEC0, length=128)

  @cached_property
  def world_tiles(self):
    return [make_worldmap_blocks(ROM_SNES, 0x0FF0C0+(i*0x300), 0x1B8000+(i*0x2000), 0x0FF9C0+(i*0x100)) for i in range(3)]

  @cached_property
  def world_blocks_pixmaps(self):
    output = []
    for i, tiles in enumerate(self.world_tiles):
      a = []
      for t in tiles:
        t.setColorTable(self.worldmap_palettes[i])
        a.append(QPixmap.fromImage(t))
      output.append(a)
    return output

  @cached_property
  def worldpixmaps(self):
    world_tile_stitches = [stitch_tileset_px(t) for t in self.world_blocks_pixmaps]
    return [make_worldmap_pixmap2(ROM_SNES, i, world_tile_stitches[t]) for i, t in enumerate([0, 1, 0, 2, 2])]
    #return [make_worldmap_pixmap(ROM_SNES, i, 0x0FFCC0+(t*0x100), self.world_tiles[t]) for i, t in enumerate([0, 1, 0, 2, 2])]

  @cached_property
  def zone_pxs_and_field_blocks(self):
    perfcount()
    print('Generating field map blocks')
    zones = [parse_zone(ROM_SNES, i) for i in range(const.zone_count)]
    field_blocksets = [get_field_map_block_layouts(ROM_SNES, i) for i in range(28)]
    perfcount()

    blockmaps = get_blockmaps(ROM_SNES)
    field_blocks = []
    zone_pxs = []
    block_cache = {'misses': 0, 'p_hits': 0, 'i_hits': 0}
    zone_px_cache = {'misses': 0, 'hits': 0}

    fm_blocks = [make_field_map_blocks_px(ROM_SNES, z, self.field_tiles, self.field_minitiles, field_blocksets, block_cache) for z in zones]
    #fm_blocks = [make_field_map_blocks_px2(ROM_SNES, z, self.field_tiles, self.field_minitiles, field_blocksets, block_cache) for z in zones]
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
    return zone_pxs, field_blocks

  @cached_property
  def zone_pxs(self):
    return self.zone_pxs_and_field_blocks[0]

  @cached_property
  def field_blocks(self):
    return self.zone_pxs_and_field_blocks[1]

  def __init__(self):
    QMainWindow.__init__(self, None)
    perfcount()
    print('Reading ROMs')
    self.ROM_FF4jp = load_raw(filename_jp_ff4)
    self.ROM_FF6jp = load_raw(filename_jp_ff6)
    print(len(self.ROM_FF4jp), filename_jp_ff4)
    print(len(self.ROM_FF6jp), filename_jp_ff6)
    perfcount()

    print('Generating String Images')
    imglist_headers = ['ID', 'EN Pointer', 'EN Address', 'EN String', 'EN Img', 'JP Pointer', 'JP Address', 'JP String', 'JP Img']
    string_images = {k: _make_string_img_list(*FFVStrings.blocks_SNES_RPGe[k], large=config.get('dialog'), **self.glyph_sprites) for k,config in FFVStrings.config.items()}
    ends_in_digit = re.compile('^([\w_]+)(\d+)')
    for k in sorted(list(string_images.keys())):  # Pre-generate keys as we destructively iterate the dict
      if m := ends_in_digit.match(k):
        k0 = m[1]
        n = int(m[2])
        print(f'Collapsing strings list {k} into {k0}')
        string_images[k0] += string_images.pop(k)
    perfcount()

    print('Generating Tileset and NPC Layer offsets')
    tileset_headers = ("ID", "Offset", "Pointer", "Expected Length")
    tileset_data = []
    for i in range(0x1C):
      offset = 0x0F0000 + (i*2)
      pointer = 0x0F0000 + indirect(ROM_RPGe, offset)
      length = indirect(ROM_RPGe, offset+2) - indirect(ROM_RPGe, offset)
      tileset_data.append((hex(i, 2), hex(offset, 6), hex(pointer, 6), hex(length, 4)))
    npc_layers = []
    offset = 0x0E59C0
    for layer in range(const.npc_layer_count):
      i = offset + (layer*2)
      start = indirect(ROM_RPGe, i) + offset
      next = indirect(ROM_RPGe, i+2) + offset
      npcs = (next - start) // 7
      for npc in range(npcs):
        address = start + (npc*7)
        npc_layers.append([hex(i, 6), hex(layer, 3)] + parse_struct(ROM_RPGe, address, const.npc_layer_structure))
    perfcount()

    print('Creating Qt Widgets')
    self.gamewidget = QTabWidget()
    self.gamewidget.addTab(welcome := QLabel('Welcome to FF5Reader, click one of the game tabs at the top to get started.'), 'Welcome')
    self.gamewidget.addTab(ff5widget := QTabWidget(), 'FFV')
    self.gamewidget.addTab(ff4widget := QTabWidget(), 'FFIV')
    self.gamewidget.addTab(ff6widget := QTabWidget(), 'FFVI')

    ff5widget.addTab(strings_tab := QTabWidget(), 'Strings')
    ff5widget.addTab(glyphs_tab := QTabWidget(), 'Glyphs')
    ff5widget.addTab(structs_tab := QTabWidget(), 'Structs')
    ff5widget.addTab(sprites_tab := QTabWidget(), 'Sprites')
    ff5widget.addTab(backgrounds_tab := QTabWidget(), 'Backgrounds')

    self.string_decoder = QWidget()
    self.decoder_input = QLineEdit()
    self.decoder_input.returnPressed.connect(self._string_decode)
    self.decoder_layout = QVBoxLayout()
    self.decoder_layout.addWidget(self.decoder_input)
    self.string_decoder.setLayout(self.decoder_layout)
    strings_tab.addTab(self.string_decoder, 'String Decoder')

    def load_tab_strings():
      for k, images in string_images.items():
        conf = FFVStrings.config[k]
        scale = 1 if conf.get('dialog') else 2
        caption = ' '.join(f'{w[0].upper()}{w[1:]}' for w in k.split('_'))
        strings_tab.addTab(tab := make_table(imglist_headers, images, row_labels=False, scale=scale), caption)
        tab.setColumnHidden(1, conf.get('rpge_ptr_offset') is None)  # Hide EN Pointer if not indirect
        tab.setColumnHidden(5, conf.get('snes_ptr_offset') is None)  # Hide JP Pointer if not indirect
        tab.resizeColumnsToContents()
        for i in range(len(imglist_headers)):
          if tab.columnWidth(i) > 360:
            tab.setColumnWidth(i, 360)

    def load_tab_glyphs():
      glyphs_tab.addTab(make_px_table(self.glyph_sprites['glyphs_en_s'], scale=3), 'Small EN')
      glyphs_tab.addTab(make_px_table(self.glyph_sprites['glyphs_en_l'], scale=2), 'Dialogue EN')
      glyphs_tab.addTab(make_px_table(self.glyph_sprites['glyphs_jp_s'], scale=3), 'Small JP')
      glyphs_tab.addTab(make_px_table(self.glyph_sprites['glyphs_jp_l'], scale=2), 'Dialogue JP')
      glyphs_tab.addTab(make_px_table(self.glyph_sprites['glyphs_kanji'], scale=2),'Kanji')

    def load_tab_structs():
      structs_tab.addTab(make_table(FFVStructs.ZoneData.get_headers(), FFVStructs.ZoneData.get_data(ROM_RPGe), True), 'Zones')
      structs_tab.addTab(make_table(FFVStructs.BattleBackground.get_headers(), FFVStructs.BattleBackground.get_data(ROM_SNES), True), 'BattleBGs')
      structs_tab.addTab(make_table(FFVStructs.EnemySprite.get_headers(), self.enemy_sprite_data, True), 'Enemy Sprites')
      structs_tab.addTab(make_table(tileset_headers, tileset_data, True), 'Tilesets')
      structs_tab.addTab(make_table(const.npc_layer_headers, npc_layers, True), 'NPC Layers')

    def load_tab_sprites():
      sprites_tab.addTab(make_px_table(self.battle_strips, cols=22, scale=2), 'Character Battle Sprites')
      sprites_tab.addTab(make_px_table(self.status_strips, cols=22, scale=2), 'Status Sprites')
      sprites_tab.addTab(make_px_table(self.enemy_sprites_named, cols=32, scale=1), 'Enemy Sprites')

    def load_tab_backgrounds():
      backgrounds_tab.addTab(make_px_table(self.worldmap_tiles, cols=16, scale=4), 'Worldmap Tiles')
      backgrounds_tab.addTab(make_px_table(self.world_blocks_pixmaps[0], cols=16, scale=3), 'World 1 Blocks')
      backgrounds_tab.addTab(make_px_table(self.world_blocks_pixmaps[1], cols=16, scale=3), 'World 2 Blocks')
      backgrounds_tab.addTab(make_px_table(self.world_blocks_pixmaps[2], cols=16, scale=3), 'Underwater Blocks')
      backgrounds_tab.addTab(make_px_table(self.worldpixmaps, cols=1, scale=1, large=True), 'Worldmaps')
      backgrounds_tab.addTab(make_px_table(self.fieldmap_tiles, cols=16, scale=1), 'Fieldmap Tiles')
      backgrounds_tab.addTab(make_px_table(self.field_blocks, cols=16, scale=1), 'Field Blocks')
      backgrounds_tab.addTab(make_px_table(self.zone_pxs, cols=4, scale=1, large=1, basicrows=True), 'Zone')
      backgrounds_tab.addTab(make_px_table(self.battle_bgs, cols=8, scale=1), 'Battle BGs')

    tab_loaders = [load_tab_strings, load_tab_glyphs, load_tab_structs, load_tab_sprites, load_tab_backgrounds]
    def load_tab(index: int):
      if fn := tab_loaders[index]:
        fn()
        tab_loaders[index] = None
    ff5widget.currentChanged.connect(load_tab)

    def load_ff5():
      load_tab(ff5widget.currentIndex())
      pass

    def load_ff4():
      ff4widget.addTab(make_px_table(self.battle_strips_ff4, cols=16, scale=2), 'Character Battle Sprites')
      ff4widget.addTab(make_px_table(self.portraits_ff4, cols=14, scale=2), 'Character Portraits')
      ff4widget.addTab(make_px_table(self.field_strips_ff4, cols=17, scale=2), 'Character Field Sprites')

    def load_ff6():
      ff6widget.addTab(make_px_table(self.battle_strips_ff6, cols=32, scale=2), 'Character Sprites')
      ff6widget.addTab(make_px_table(self.portraits_ff6, cols=19, scale=2), 'Character Portraits')

    game_tab_loaders = [None, load_ff5, load_ff4, load_ff6]
    def load_game_tab(index: int):
      if fn := game_tab_loaders[index]:
        fn()
        game_tab_loaders[index] = None
    self.gamewidget.currentChanged.connect(load_game_tab)

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
