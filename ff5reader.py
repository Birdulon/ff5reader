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
import os
from struct import unpack
from itertools import chain
from array import array
import time
import functools

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
import includes.const as const
import includes.ff4 as ff4
import includes.ff6 as ff6

pyqt_version = 0
skip_pyqt5 = 'PYQT4' in os.environ
filename_en = 'Final Fantasy V (Japan) [En by RPGe v1.1].sfc'
filename_jp = 'Final Fantasy V (Japan).sfc'
filename_jp_ff4 = 'Final Fantasy IV (Japan) (Rev A).sfc'
filename_jp_ff6 = 'Final Fantasy VI (Japan).sfc'

if not skip_pyqt5:
    try:
        from PyQt5 import QtGui, QtCore
        from PyQt5.QtGui import QIcon, QPalette, QColor, QFont, QFontInfo, QImage, QPixmap
        from PyQt5.QtWidgets import (
            QApplication, QMainWindow, QFormLayout,
            QGridLayout, QHBoxLayout, QVBoxLayout,
            QAbstractItemView, QHeaderView, QListWidget,
            QListWidgetItem, QTabWidget, QTableWidget,
            QTableWidgetItem, QFrame, QScrollArea,
            QStackedWidget, QWidget, QCheckBox, QComboBox,
            QDoubleSpinBox, QGroupBox, QLineEdit,
            QPushButton, QRadioButton, QSpinBox,
            QStyleOptionButton, QToolButton, QProgressBar,
            QDialog, QColorDialog, QDialogButtonBox,
            QFileDialog, QInputDialog, QMessageBox,
            QAction, QActionGroup, QLabel, QMenu, QStyle,
            QSystemTrayIcon, QStyleOptionProgressBar
        )
        pyqt_version = 5
    except ImportError:
        print("Couldn't import Qt5 dependencies. "
              'Make sure you installed the PyQt5 package.')
if pyqt_version == 0:
    try:
        import sip
        sip.setapi('QVariant', 2)
        from PyQt4 import QtGui, QtCore
        from PyQt4.QtGui import (
            QApplication, QMainWindow, QFormLayout,
            QGridLayout, QHBoxLayout, QVBoxLayout,
            QAbstractItemView, QHeaderView, QListWidget,
            QListWidgetItem, QTabWidget, QTableWidget,
            QTableWidgetItem, QFrame, QScrollArea,
            QStackedWidget, QWidget, QCheckBox,
            QComboBox, QDoubleSpinBox, QGroupBox,
            QLineEdit, QPushButton, QRadioButton,
            QSpinBox, QStyleOptionButton, QToolButton,
            QProgressBar, QDialog, QColorDialog,
            QDialogButtonBox, QFileDialog, QInputDialog,
            QMessageBox, QAction, QActionGroup,
            QLabel, QMenu, QStyle,
            QSystemTrayIcon, QIcon, QPalette, QColor,
            QValidator, QFont, QFontInfo, QImage, QPixmap
        )
        from PyQt4.QtGui import QStyleOptionProgressBarV2 as QStyleOptionProgressBar
        pyqt_version = 4
    except ImportError:
        print("Couldn't import Qt dependencies. "
              'Make sure you installed the PyQt4 package.')
        sys.exit(-1)


class FF5Reader(QMainWindow):
  '''
  Main GUI class
  '''
  def __init__(self):
    QMainWindow.__init__(self, None)
    perfcount()
    print('Reading ROMs')
    with open(filename_en, 'rb') as file:
      ROM_en = file.read()
    print(len(ROM_en), filename_en)
    with open(filename_jp, 'rb') as file:
      ROM_jp = file.read()
    print(len(ROM_jp), filename_jp)
    with open(filename_jp_ff4, 'rb') as file:
      ROM_FF4jp = file.read()
    print(len(ROM_FF4jp), filename_jp_ff4)
    with open(filename_jp_ff6, 'rb') as file:
      ROM_FF6jp = file.read()
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
    make_string_img_list = functools.partial(_make_string_img_list, ROM_en, ROM_jp, **self.glyph_sprites)
    perfcount()

    stringlist_headers = ['Address', 'ID', 'Name']
    imglist_headers = stringlist_headers + ['Img', 'Name JP', 'Img JP']

    print('Generating Strings')
    zone_names = make_string_img_list(0x107000, 2, 0x100, start_str=0x270000, start_jp_str=0x107200, indirect=True, large=True)
    items = make_string_img_list(0x111380, 9, 256)
    magics = make_string_img_list(0x111C80, 6, 87)
    more_magics = make_string_img_list(0x111E8A, 9, 73)
    enemy_names = make_string_img_list(0x200050, 10, 0x180, 0x105C00, 8)
    character_names = make_string_img_list(0x115500, 6, 5)
    job_names = make_string_img_list(0x115600, 8, 22)
    ability_names = make_string_img_list(0x116200, 8, 33)
    battle_commands = make_string_img_list(0x201150, 7, 0x60, 0x115800, 5)
    perfcount()
    dialogue = make_string_img_list(0x2013F0, 3, 0x900, start_jp=0x082220, len_jp=2, start_str=0x0, start_jp_str=0x0A0000, indirect=True, large=True, macros_en=const.Dialogue_Macros_EN, macros_jp=const.Dialogue_Macros_JP)
    perfcount()

    def split_tilesets(data):
      tilesets = [(data & 0x00003F),
                  (data & 0x000FC0) >> 6,
                  (data & 0x03F000) >> 12,
                  (data & 0xFC0000) >> 18]
      return ' '.join([hex(i,2) for i in tilesets])
    def split_blockmaps(data):
      blockmaps = [(data & 0x000003FF) - 1,
                  ((data & 0x000FFC00) >> 10) - 1,
                  ((data & 0x3FF00000) >> 20) - 1]
      return ' '.join([hex(i,3) for i in blockmaps])

    zone_structure = [('NPC Layer',      2, None),  # 00 01
                      ('Name',           1, [z[2] for z in zone_names]),  # 02
                      ('ShadowFlags',    1, None),  # 03
                      ('Graphic maths',  1, None),  # 04  - MSb animation-related, 6 LSbs are ID for table in 0x005BB8 which writes to $2131-$2133 (Color Math Designation, Subscreen BG color)
                      ('Tile properties',        1, None),  # 05
                      ('Flags '+hex(6),  1, None),  # 06
                      (hex(7),           1, None),  # 07
                      ('Blockset',       1, None),  # 08
                      ('Tilesets',       3, split_tilesets),  # 09 0A 0B
                      ('Blockmaps',      4, split_blockmaps),  # 0C 0D 0E 0F
                      (hex(16),          1, None),  # 10
                      (hex(17),          1, None),  # 11
                      (hex(18),          1, None),  # 12
                      (hex(19),          1, None),  # 13
                      (hex(20),          1, None),  # 14
                      (hex(21),          1, None),  # 15
                      ('Palette',        1, None),  # 16
                      (hex(23),          1, None),  # 17
                      (hex(24),          1, None),  # 18
                      ('Music',          1, const.BGM_Tracks)]  # 19
    zone_headers = ['Address'] + [z[0] for z in zone_structure]
    zone_data = [parse_struct(ROM_en, 0x0E9C00 + (i*0x1A), zone_structure) for i in range(const.zone_count)]

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
      enemy_sprite_data.append(parse_struct(ROM_en, address + (i*5), enemy_sprite_structure) + enemy_names[i][2:4])

    perfcount()
    print('Generating map tiles')
    worldmap_palettes = [generate_palette(ROM_jp, 0x0FFCC0+(i*0x100), length=0x160, transparent=True) for i in range(3)]
    world_tiles = [make_worldmap_blocks(ROM_jp, 0x0FF0C0+(i*0x300), 0x1B8000+(i*0x2000), 0x0FF9C0+(i*0x100)) for i in range(3)]
    worldpixmaps = [make_worldmap_pixmap(ROM_jp, i, 0x0FFCC0+(t*0x100), world_tiles[t]) for i, t in enumerate([0, 1, 0, 2, 2])]
    world_blocks_pixmaps = []
    for i, tiles in enumerate(world_tiles):
      a = []
      for t in tiles:
        t.setColorTable(worldmap_palettes[i])
        a.append(QPixmap.fromImage(t))
      world_blocks_pixmaps.append(a)
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
    for z in zones:
      blocks, miniblocks = make_field_map_blocks_px(ROM_jp, z, field_tiles, field_minitiles, field_blocksets, block_cache)
      field_blocks.append(stitch_tileset_px([b.all for b in blocks+miniblocks]))
      zone_pxs += make_zone_pxs(blocks, miniblocks, blockmaps, z, zone_px_cache)
    print('Block cache results: {misses} misses, {p_hits} full hits, {i_hits} palette misses'.format(**block_cache))
    print('Zone pixmap cache results: {misses} misses, {hits} hits'.format(**zone_px_cache))
    perfcount()

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
    backgrounds_tab.addTab(make_px_table(zone_pxs, cols=4, scale=1, large=1), 'Zone')
    backgrounds_tab.addTab(make_px_table(battle_bgs, cols=8, scale=1), 'Battle BGs')

    self.ff4widget.addTab(make_px_table(self.battle_strips_ff4, cols=16, scale=2), 'Character Battle Sprites')
    self.ff4widget.addTab(make_px_table(self.portraits_ff4, cols=14, scale=2), 'Character Portraits')
    self.ff4widget.addTab(make_px_table(self.field_strips_ff4, cols=17, scale=2), 'Character Field Sprites')
    self.ff6widget.addTab(make_px_table(self.battle_strips_ff6, cols=32, scale=2), 'Character Sprites')
    self.ff6widget.addTab(make_px_table(self.portraits_ff6, cols=19, scale=2), 'Character Portraits')


    structs_tab.addTab(make_table(zone_headers, zone_data, True), 'Zones')
    structs_tab.addTab(make_table(tileset_headers, tileset_data, True), 'Tilesets')
    structs_tab.addTab(make_table(battle_bg_headers, battle_bg_data, True), 'BattleBGs')
    structs_tab.addTab(make_table(const.npc_layer_headers, npc_layers, True), 'NPC Layers')
    structs_tab.addTab(make_table(enemy_sprite_headers, enemy_sprite_data, True), 'Enemy Sprites')

    strings_tab.addTab(make_table(imglist_headers, items, row_labels=False), 'Items')
    strings_tab.addTab(make_table(imglist_headers, magics+more_magics, row_labels=False), 'Magics')
    #strings_tab.addTab(make_table(imglist_headers, more_magics, row_labels=False), 'More Magics')
    strings_tab.addTab(make_table(imglist_headers, enemy_names, row_labels=False), 'Enemy Names')
    strings_tab.addTab(make_table(imglist_headers, character_names, row_labels=False), 'Character Names')
    strings_tab.addTab(make_table(imglist_headers, job_names, row_labels=False), 'Job Names')
    strings_tab.addTab(make_table(imglist_headers, ability_names, row_labels=False), 'Ability Names')
    strings_tab.addTab(make_table(imglist_headers, battle_commands, row_labels=False), 'Battle Commands')
    strings_tab.addTab(make_table(imglist_headers, zone_names, True, scale=1), 'Zone Names')
    strings_tab.addTab(make_table(imglist_headers+['JP address'], dialogue, scale=1), 'Dialogue')

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
def make_string_img_small(bytestring, glyphs, jp=False):
  '''
  JP version is not as fancy as this with dakuten, it just puts them on the row above and clips.
  '''
  if len(bytestring) < 1:
    raise ValueError('Empty bytestring was passed')
  string = ''
  img = QImage(len(bytestring)*8, 10, QImage.Format_RGB16)
  img.fill(bg_color)
  painter = QtGui.QPainter(img)
  if jp:
    for x, j in enumerate(bytestring):
      string = string + const.Glyphs_JP2[j]
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
      string = string + const.Glyphs[j]
      painter.drawPixmap(x*8, 1, glyphs[j])
  del painter
  return string, QPixmap.fromImage(img)


def make_string_img_large(bytestring, glyphs, glyphs_kanji, macros=None, jp=False):
  '''
  This is how we decipher dialogue data, which has multiple lines, macro expansions and kanji.
  English characters have varying widths. In the japanese version, everything is fullwidth (16px)
  Kanji aren't used in English dialogue but the cost is likely the same in checking either way.
  '''
  if len(bytestring) < 1:
    raise ValueError('Empty bytestring was passed')

  newstring = []
  bytes = iter(bytestring)
  for b in bytes:
    if b in const.DoubleChars:
      b2 = next(bytes)
      newstring.append((b<<8) + b2)
    elif macros and b in macros:
      newstring.extend(macros[b])
    else:
      newstring.append(b)

  string = ''
  # Because the length of the input has little bearing on the size of the image thanks to linebreaks and macros, we overprovision then clip away.
  max_width = 256  # This seems to check out, but the EN dialogue has linebreaks virtually everywhere anyway
  max_height = 1024  # I've seen up to 58 rows in EN, 36 in JP. Stay safe.
  img = QImage(max_width, max_height, QImage.Format_RGB16)
  img.fill(bg_color)
  painter = QtGui.QPainter(img)

  x = xmax = y = 0
  for j in newstring:
    if x >= max_width:  # Wrap on long line
      string += '[wr]\n'
      xmax = max_width  # Can't go higher than this anyway
      x = 0
      y += 16
    if j == 0x01:  # Line break
      string += '[br]\n'
      xmax = x if x > xmax else xmax
      x = 0
      y += 16
    elif 0x1E00 <= j < 0x1FAA:  # Kanji live in this range
      string += const.Glyphs_Kanji[j-0x1E00]
      painter.drawPixmap(x, y+2, glyphs_kanji[j-0x1E00])
      x += 16
    elif j < 0x13 or j > 0xFF:  # Everything remaining outside this is a control char
      string += '[0x{:02X}]'.format(j)
    else:
      if jp:
        string += const.Glyphs_JP_large[j]
        painter.drawPixmap(x, y+2, glyphs[j])
        x += 16
      else:
        string += const.Glyphs[j]
        painter.drawPixmap(x, y+4, glyphs[j])
        x += const.Dialogue_Width[j]
  del painter
  xmax = x if x > xmax else xmax
  return string, QPixmap.fromImage(img.copy(0, 0, xmax, y+16))


def _make_string_img_list(rom_e, rom_j, start, length, num,
                          start_jp=None, len_jp=None, start_str=None, start_jp_str=None,
                          indirect=False, large=False, macros_en=None, macros_jp=None,
                          glyphs_en_s=None, glyphs_en_l=None,
                          glyphs_jp_s=None, glyphs_jp_l=None, glyphs_kanji=None):
  start_jp = start if start_jp is None else start_jp
  len_jp = length if len_jp is None else len_jp
  start_str = start if start_str is None else start_str
  start_jp_str = start_str if start_jp_str is None else start_jp_str
  stringlist = []
  id_digits = hex_length(num-1)

  if indirect:
    for id in range(num):
      en = start + (id*length)
      jp = start_jp + (id*len_jp)
      en_start = int.from_bytes(rom_e[en:en+length],'little') + start_str
      en_end = int.from_bytes(rom_e[en+length:en+(length*2)],'little') + start_str
      if en_start >= 0xC00000:  # SNES memory space has the ROM starting at 0xC00000 in HiROM mode.
        en_start -= 0xC00000
        en_end -= 0xC00000
      jp_start = int.from_bytes(rom_j[jp:jp+len_jp],'little') + start_jp_str
      jp_end = int.from_bytes(rom_j[jp+len_jp:jp+(len_jp*2)],'little') + start_jp_str
      if jp_start >= 0xC00000:  # SNES memory space has the ROM starting at 0xC00000 in HiROM mode.
        jp_start -= 0xC00000
        jp_end -= 0xC00000
      if (en_end == start_str) or (jp_end == start_jp_str):
        break
      try:  # When dealing with pointer redirection we might end up passing empty strings
        if large:
          str_en, img_en = make_string_img_large(rom_e[en_start:en_end], glyphs_en_l,  glyphs_kanji, macros_en)
        else:
          str_en, img_en = make_string_img_small(rom_e[en_start:en_end], glyphs_en_s)
      except ValueError:
        str_en = ''
        img_en = None
      try:
        if large:
          str_jp, img_jp = make_string_img_large(rom_j[jp_start:jp_end], glyphs_jp_l, glyphs_kanji, macros_jp, jp=True)
        else:
          str_jp, img_jp = make_string_img_small(rom_j[jp_start:jp_end], glyphs_jp_s, jp=True)
      except ValueError:
        str_jp = ''
        img_jp = None
      stringlist.append([
        hex(en, 6), hex(id, id_digits),
        str_en, img_en, str_jp, img_jp, hex(jp_start, 6)
        ])
  else:
    for id in range(num):
      j1 = start + (id*length)
      j2 = start_jp + (id*len_jp)
      if large:
        str_en, img_en = make_string_img_large(rom_e[j1:j1+length], glyphs_en_l, glyphs_kanji, macros_en)
        str_jp, img_jp = make_string_img_large(rom_j[j2:j2+len_jp], glyphs_jp_l, glyphs_kanji, macros_jp, jp=True)
      else:
        str_en, img_en = make_string_img_small(rom_e[j1:j1+length], glyphs_en_s)
        str_jp, img_jp = make_string_img_small(rom_j[j2:j2+len_jp], glyphs_jp_s, jp=True)
      stringlist.append([hex(j1, 6), hex(id, id_digits), str_en, img_en, str_jp, img_jp])
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
