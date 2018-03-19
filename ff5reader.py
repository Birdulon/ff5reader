#!/usr/bin/python3 -i
'''
No license for now
'''

import sys
import os
from struct import unpack
from itertools import chain
from array import array
from snestile import generate_glyphs, generate_glyphs_large, generate_palette, create_tile
import const
import time

pyqt_version = 0
skip_pyqt5 = 'PYQT4' in os.environ
filename_en = 'Final Fantasy V (Japan) [En by RPGe v1.1].sfc'
filename_jp = 'Final Fantasy V (Japan).sfc'
filename_jp_ff4 = 'Final Fantasy IV (Japan) (Rev A).sfc'

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

bg_color = QColor(0, 0, 128)
bg_trans = QColor(0, 0, 0, 0)

HEX_PREFIX = '#'  # '$' or '0x' are also nice

monofont = QFont()
monofont.setStyleHint(QFont.Monospace)
if not monofont.fixedPitch():
    monofont.setStyleHint(QFont.TypeWriter)
if not monofont.fixedPitch():
    monofont.setFamily('Monospace')

def divceil(numerator, denominator):
    # Reverse floor division for ceil
    return -(-numerator // denominator)

def hex_length(i):
    return divceil(i.bit_length(), 4)

with open(filename_en, 'rb') as file:
    ROM_en = file.read()
print(len(ROM_en), filename_en)
with open(filename_jp, 'rb') as file:
    ROM_jp = file.read()
print(len(ROM_jp), filename_jp)
with open(filename_jp_ff4, 'rb') as file:
    ROM_FF4jp = file.read()
print(len(ROM_jp), filename_jp)

stringlist_headers = ['Address', 'ID', 'Name']
imglist_headers = stringlist_headers + ['Img', 'Name JP', 'Img JP']


class FF5Reader(QMainWindow):
  """
  Main GUI class
  """
  def __init__(self):
    QMainWindow.__init__(self, None)
    global glyph_sprites_en_large, glyph_sprites_en_small, glyph_sprites_jp_small, glyph_sprites_jp_large, glyph_sprites_kanji, glyph_sprites_jp_dialogue
    glyph_sprites_en_small = generate_glyphs(ROM_en, 0x11F000)
    glyph_sprites_en_large = generate_glyphs_large(ROM_en, 0x03E800)
    glyph_sprites_jp_small = generate_glyphs(ROM_jp, 0x11F000)
    glyph_sprites_jp_large = generate_glyphs_large(ROM_jp, 0x03E800)
    glyph_sprites_kanji = generate_glyphs_large(ROM_jp, 0x1BD000, 0x1AA)  # Kanji are unchanged in EN version

    global zone_names
    zone_names = make_string_img_list(0x107000, 2, 0x100, start_str=0x270000, start_jp_str=0x107200, indirect=True, large=True)
    items = make_string_img_list(0x111380, 9, 256)
    magics = make_string_img_list(0x111C80, 6, 87)
    more_magics = make_string_img_list(0x111E8A, 9, 73)
    enemy_names = make_string_img_list(0x200050, 10, 0x180, 0x105C00, 8)
    character_names = make_string_img_list(0x115500, 6, 5)
    job_names = make_string_img_list(0x115600, 8, 22)
    ability_names = make_string_img_list(0x116200, 8, 33)
    battle_commands = make_string_img_list(0x201150, 7, 0x60, 0x115800, 5)
    dialogue = make_string_img_list(0x2013F0, 3, 0x900, start_jp=0x082220, len_jp=2, start_str=0x0, start_jp_str=0x0A0000, indirect=True, large=True, macros_en=const.Dialogue_Macros_EN, macros_jp=const.Dialogue_Macros_JP)

    zone_structure = [('NPC Layer',      2, None),
                      ('Name',           1, [z[2] for z in zone_names]),
                      ('ShadowFlags',    1, None),
                      (hex(4, 2),        1, None),
                      (hex(5, 2),        1, None),
                      ('Flags '+hex(6,2),1, None),
                      (hex(7, 2),        1, None),
                      ('Tileset',        1, None),
                      ('Tileset2',       2, None),
                      #('0x0A',           1, None),
                      (hex(11, 2),       1, None),
                      ('Collision Layer',1, None),
                      (hex(13, 2),       1, None),
                      (hex(14, 2),       1, None),
                      (hex(15, 2),       1, None),
                      (hex(16, 2),       1, None),
                      (hex(17, 2),       1, None),
                      (hex(18, 2),       1, None),
                      (hex(19, 2),       1, None),
                      (hex(20, 2),       1, None),
                      (hex(21, 2),       1, None),
                      ('Palette',        1, None),
                      (hex(23, 2),       1, None),
                      (hex(24, 2),       1, None),
                      ('Music',          1, const.BGM_Tracks)]
    zone_headers = ['Address'] + [z[0] for z in zone_structure]

    zone_data = []
    for i in range(const.zone_count):
        offset = 0x0E9C00 + (i*0x1A)
        zone_data.append(parse_struct(ROM_en, offset, zone_structure))

    tileset_headers = ("ID", "Offset", "Pointer", "Expected Length")
    tileset_data = []
    for i in range(0x1C):
      offset = 0x0F0000 + (i*2)
      pointer = 0x0F0000 + int.from_bytes(ROM_en[offset:offset+2],'little')
      length = int.from_bytes(ROM_en[offset+2:offset+4],'little') - int.from_bytes(ROM_en[offset:offset+2],'little')
      tileset_data.append((hex(i, 2), hex(offset, 6), hex(pointer, 6), hex(length, 4)))

    npc_layers = []
    offset = 0x0E59C0
    for layer in range(const.npc_layer_count):
      i = offset + (layer*2)
      start = int.from_bytes(ROM_en[i:i+2],'little') + offset
      next = int.from_bytes(ROM_en[i+2:i+4],'little') + offset
      npcs = (next - start) // 7
      for npc in range(npcs):
        address = start + (npc*7)
        npc_layers.append([hex(i, 6), hex(layer, 3)] + parse_struct(ROM_en, address, const.npc_layer_structure))

    #enemy_tile_layouts = []
    #address = 0x10D004
    #for i in range(0x66):
      #offset = address + (i*8)
      #img = QImage(8, 8, QImage.Format_Mono)
      #img.setColorTable(const.mono_palette)
      #for i in range(8):
        #ptr = img.scanLine(i)
        #ptr.setsize(32)
        #ptr[0:1] = ROM_en[offset+i:offset+i+1]
      #pixmap = QPixmap.fromImage(img)
      #enemy_tile_layouts.append(pixmap.scaled(16, 16))

    enemy_sprite_data = []
    enemy_sprite_structure = [
      ('Sprite data offset', 2, None),
      ('Multiple things',    2, None),
      ('Tile Layout ID',     1, None)
      ]
    enemy_sprite_headers = ['Address']+[i[0] for i in enemy_sprite_structure]+['EN Name','EN Name']
    address = 0x14B180
    for i in range(0x180):
      enemy_sprite_data.append(parse_struct(ROM_en, address + (i*5), enemy_sprite_structure) + enemy_names[i][2:4])

    self.battle_strips = make_character_battle_sprites(ROM_en)
    status_strips = make_character_status_sprites(ROM_en)
    enemy_sprites = make_enemy_sprites(ROM_en)
    self.battle_strips_ff4 = make_character_battle_sprites_ff4(ROM_FF4jp)

    enemy_sprites_named = [stack_labels(s, d[-2]) for s, d in zip(enemy_sprites, enemy_sprite_data)]

    self.tabwidget = QTabWidget()
    strings_tab = QTabWidget()
    structs_tab = QTabWidget()
    sprites_tab = QTabWidget()
    self.tabwidget.addTab(strings_tab, 'Strings')
    self.tabwidget.addTab(structs_tab, 'Structs')
    self.tabwidget.addTab(sprites_tab, 'Images')

    sprites_tab.addTab(make_pixmap_table(glyph_sprites_en_small, scale=4), 'Glyphs (EN)')
    sprites_tab.addTab(make_pixmap_table(glyph_sprites_en_large, scale=2), 'Glyphs (Dialogue EN)')
    sprites_tab.addTab(make_pixmap_table(glyph_sprites_jp_small, scale=4), 'Glyphs (JP)')
    sprites_tab.addTab(make_pixmap_table(glyph_sprites_jp_large, scale=2), 'Glyphs (Large JP)')
    sprites_tab.addTab(make_pixmap_table(glyph_sprites_kanji, scale=2),    'Glyphs (Kanji)')
    sprites_tab.addTab(make_pixmap_table(self.battle_strips, cols=22, scale=2), 'Character Battle Sprites')
    sprites_tab.addTab(make_pixmap_table(status_strips, cols=22, scale=2), 'Status Sprites')
    #sprites_tab.addTab(make_pixmap_table(enemy_sprites, scale=1), 'Enemy Sprites')
    sprites_tab.addTab(make_pixmap_table(enemy_sprites_named, cols=32, scale=1), 'Enemy Sprites')
    sprites_tab.addTab(make_pixmap_table(self.battle_strips_ff4, cols=16, scale=2), 'FF4 Character Battle Sprites')


    structs_tab.addTab(make_table(zone_headers, zone_data, True), 'Zones')
    structs_tab.addTab(make_table(tileset_headers, tileset_data, True), 'Tilesets')
    structs_tab.addTab(make_table(const.npc_layer_headers, npc_layers, True), 'NPC Layers')
    structs_tab.addTab(make_table(enemy_sprite_headers, enemy_sprite_data, True), 'Enemy Sprites')

    strings_tab.addTab(make_table(imglist_headers, items, row_labels=False), 'Items')
    strings_tab.addTab(make_table(imglist_headers, magics, row_labels=False), 'Magics')
    strings_tab.addTab(make_table(imglist_headers, more_magics, row_labels=False), 'More Magics')
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
    layout.addWidget(self.tabwidget)
    self.main_widget = QWidget(self)
    self.main_widget.setLayout(layout)
    self.main_widget.setMinimumSize(800,600)
    self.setCentralWidget(self.main_widget)
    self.show()

  def _string_decode(self):
    string = ''.join(self.decoder_input.text().split())
    if len(string) % 1:
      string += '0'
    bytelist = [int(string[i:i+2], 16) for i in range(0, len(string), 2)]
    tups = make_string_img_small(bytes(bytelist))
    print(tups[0])
    img = QLabel()
    img.setPixmap(tups[1])
    self.decoder_layout.addWidget(img)
    self.decoder_input.setText('')


class Canvas:
  def __init__(self, cols, rows, color=bg_trans):
    self.image = QImage(8*cols, 8*rows, QImage.Format_ARGB32_Premultiplied)
    self.image.fill(color)
    self.painter = QtGui.QPainter(self.image)
    self.max_x = 1
    self.max_y = 1

  def __del__(self):
    del self.painter

  def draw_pixmap(self, row, column, pixmap):
    self.painter.drawPixmap(row*8, column*8, pixmap)
    if row > self.max_x:
      self.max_x = row
    if column > self.max_y:
      self.max_y = column

  def pixmap(self, trim=False):
    if trim:
      return QPixmap.fromImage(self.image.copy(0, 0, self.max_x*8+8, self.max_y*8+8))
    return QPixmap.fromImage(self.image)


def parse_struct(rom, offset, structure):
  out = [hex(offset, 6)]
  j = 0
  for z in structure:
    val = int.from_bytes(rom[offset+j:offset+j+z[1]],'little')
    if z[2] and val < len(z[2]):
      out.append(z[2][val])
    else:
      out.append(hex(val, z[1]*2))
    j += z[1]
  return out


def make_enemy_sprites(rom):
  sprites = []
  for e_id in range(0, 0x180*5, 5):
    triplane = bool(rom[0x14B180+e_id]&0x80)  # True if 3 planes, False if 4
    bytes_per_tile = 24 if triplane else 32
    tile_offset = ((((rom[0x14B180+e_id]&0x7F)<<8)| rom[0x14B181+e_id]) << 3) + 0x150000  # For whatever reason this is big endian
    pal_offset = ((((rom[0x14B182+e_id]&0x03)<<8)| rom[0x14B183+e_id]) << 4) + 0x0ED000  # For whatever reason this is big endian
    pal_size = 16 if triplane else 32
    palette = generate_palette(rom, pal_offset, pal_size)
    palette[0] = 0
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


def make_battle_strip(rom, palette_address, tile_address, num_tiles):
  palette = generate_palette(rom, palette_address)
  # We don't want the background drawn, so we'll make that colour transparent
  palette[0] = 0
  battle_strip = Canvas(2, divceil(num_tiles, 2))  # KO sprites are here which means more tiles than FFV
  for j in range(num_tiles):
    offset = tile_address+(j*32)
    battle_strip.draw_pixmap(j%2, j//2, create_tile(rom[offset:offset+32], palette))
  return battle_strip.pixmap()


def make_character_battle_sprites_ff4(rom):
  tile_address = 0x0D0000
  pig_tile_address = 0x0D7000
  golbez_tile_address = 0x0D7600
  anna_tile_address = 0x0D7960
  palette_address = 0x0E7D00
  golbez_palette_address = 0x0E7EC0
  anna_palette_address = 0x0E7EE0
  battle_strips = []
  for i in range(0, 14*32, 32):  # 14 regular characters. Pig, Golbez and Anna follow with different tile spacing and palette order.
    battle_strips.append(make_battle_strip(rom, palette_address+i, tile_address+(i*64), 64))  # KO sprites are here which means more tiles per strip than FFV
  battle_strips.append(make_battle_strip(rom, golbez_palette_address, golbez_tile_address, 27))
  battle_strips.append(make_battle_strip(rom, anna_palette_address, anna_tile_address, 14))
  for i in range(0, 16*32, 32):  # 16 pigs.
    battle_strips.append(make_battle_strip(rom, palette_address+i, pig_tile_address, 48))
  return battle_strips


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
    palette = generate_palette(rom, palette_address + (i*22*32))  # Freelance palette per character
    # We don't want the background drawn, so we'll make that colour transparent
    palette[0] = 0
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


def make_string_img_small(bytestring, jp=False):
  if len(bytestring) < 1:
    raise ValueError('Empty bytestring was passed')
  string = ""
  img = QImage(len(bytestring)*8, 10, QImage.Format_RGB16)
  img.fill(bg_color)
  painter = QtGui.QPainter(img)
  if jp:
    for x, j in enumerate(bytestring):
      string = string + const.Glyphs_JP2[j]
      if 0x20 <= j < 0x52:
        if j > 0x48:
          painter.drawPixmap(x*8, 2, glyph_sprites_jp_small[j+0x17])
          painter.drawPixmap(x*8+1,-5, glyph_sprites_jp_small[0x52])
        else:
          painter.drawPixmap(x*8, 2, glyph_sprites_jp_small[j+0x40])
          painter.drawPixmap(x*8+1,-6, glyph_sprites_jp_small[0x51])
      else:
        painter.drawPixmap(x*8, 2, glyph_sprites_jp_small[j])
  else:
    for x, j in enumerate(bytestring):
      string = string + const.Glyphs[j]
      painter.drawPixmap(x*8, 1, glyph_sprites_en_small[j])
  del painter
  return string, QPixmap.fromImage(img)


def make_string_img_large(bytestring, macros=None, jp=False):
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

  string = ""
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
      painter.drawPixmap(x, y+2, glyph_sprites_kanji[j-0x1E00])
      x += 16
    elif j < 0x13 or j > 0xFF:  # Everything remaining outside this is a control char
      string += '[0x{:02X}]'.format(j)
    else:
      if jp:
        string += const.Glyphs_JP_large[j]
        painter.drawPixmap(x, y+2, glyph_sprites_jp_large[j])
        x += 16
      else:
        string += const.Glyphs[j]
        painter.drawPixmap(x, y+4, glyph_sprites_en_large[j])
        x += const.Dialogue_Width[j]
  del painter
  xmax = x if x > xmax else xmax
  return string, QPixmap.fromImage(img.copy(0, 0, xmax, y+16))


def make_string_img_list(start, length, num, start_jp=None, len_jp=None, start_str=None, start_jp_str=None,
                         indirect=False, large=False, macros_en=None, macros_jp=None):
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
      en_start = int.from_bytes(ROM_en[en:en+length],'little') + start_str
      en_end = int.from_bytes(ROM_en[en+length:en+(length*2)],'little') + start_str
      if en_start >= 0xC00000:  # SNES memory space has the ROM starting at 0xC00000 in HiROM mode.
        en_start -= 0xC00000
        en_end -= 0xC00000
      jp_start = int.from_bytes(ROM_jp[jp:jp+len_jp],'little') + start_jp_str
      jp_end = int.from_bytes(ROM_jp[jp+len_jp:jp+(len_jp*2)],'little') + start_jp_str
      if jp_start >= 0xC00000:  # SNES memory space has the ROM starting at 0xC00000 in HiROM mode.
        jp_start -= 0xC00000
        jp_end -= 0xC00000
      if (en_end == start_str) or (jp_end == start_jp_str):
        break
      try:  # When dealing with pointer redirection we might end up passing empty strings
        if large:
          str_en, img_en = make_string_img_large(ROM_en[en_start:en_end], macros_en)
        else:
          str_en, img_en = make_string_img_small(ROM_en[en_start:en_end])
      except ValueError:
        str_en = ''
        img_en = None
      try:
        if large:
          str_jp, img_jp = make_string_img_large(ROM_jp[jp_start:jp_end], macros_jp, jp=True)
        else:
          str_jp, img_jp = make_string_img_small(ROM_jp[jp_start:jp_end], jp=True)
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
        str_en, img_en = make_string_img_large(ROM_en[j1:j1+length], macros_en)
        str_jp, img_jp = make_string_img_large(ROM_jp[j2:j2+len_jp], macros_jp, jp=True)
      else:
        str_en, img_en = make_string_img_small(ROM_en[j1:j1+length])
        str_jp, img_jp = make_string_img_small(ROM_jp[j2:j2+len_jp], jp=True)
      stringlist.append([hex(j1, 6), hex(id, id_digits), str_en, img_en, str_jp, img_jp])
  return stringlist


def table_size_to_contents(table):
    # Stupid hack to get table to size correctly
    table.hide()
    geometry = table.viewport().geometry()
    table.viewport().setGeometry(QtCore.QRect(0, 0, 0x7FFFFFFF, 0x7FFFFFFF))
    table.resizeColumnsToContents()
    table.resizeRowsToContents()
    table.viewport().setGeometry(geometry)
    table.show()


def make_table(headers, items, sortable=False, row_labels=True, scale=2):
  '''
  Helper function to tabulate 2d lists
  '''
  cols = len(headers)
  rows = len(items)
  rd = hex_length(rows-1)
  table = QTableWidget(rows, cols)
  if row_labels:
    table.setVerticalHeaderLabels([hex(v, rd) for v in range(rows)])
  else:
    table.verticalHeader().setVisible(False)
  table.setHorizontalHeaderLabels(headers)
  for row, col, item in [(x,y,items[x][y]) for x in range(rows) for y in range(cols)]:
    if isinstance(item, QWidget):
      table.setCellWidget(row, col, item)
    elif isinstance(item, QPixmap):
      pix = item.scaled(item.size() * scale)
      lab = QLabel()
      lab.setPixmap(pix)
      table.setCellWidget(row, col, lab)
    elif item is not None:
      if item.endswith('₁₆'):
        s = '<tt>{}</tt><sub>16</sub>'.format(item[:-2])
        lab = QLabel(s)
        table.setCellWidget(row, col, lab)
      else:
        q_item = QTableWidgetItem(item)
        if item.startswith(HEX_PREFIX):
          q_item.setFont(monofont)
        table.setItem(row, col, q_item)
  table_size_to_contents(table)
  if sortable:
    table.setSortingEnabled(True)
    table.sortItems(0)
  return table


def make_pixmap_table(items, cols=16, scale=4):
  rows = divceil(len(items), cols)
  rd = hex_length(rows-1)+1
  cd = hex_length(cols-1)
  table = QTableWidget(rows, cols)
  table.setVerticalHeaderLabels([hex(v*cols, rd) for v in range(rows)])
  table.setHorizontalHeaderLabels([hex(v, cd) for v in range(cols)])
  for i, item in enumerate(items):
    if isinstance(item, QWidget):
      table.setCellWidget(i // cols, i % cols, item)
    elif isinstance(item, QPixmap):
      lab = QLabel()
      lab.setPixmap(item.scaled(item.size() * scale))
      lab.setAlignment(QtCore.Qt.AlignCenter)
      table.setCellWidget(i // cols, i % cols, lab)
  table_size_to_contents(table)
  return table


def stack_labels(*items):
  w = QWidget()
  w.setContentsMargins(0, 0, 0, 0)
  l = QVBoxLayout()
  l.setAlignment(QtCore.Qt.AlignCenter)
  l.setSpacing(0)
  l.setContentsMargins(0, 0, 0, 0)
  for item in items:
    lab = QLabel()
    if isinstance(item, QPixmap):
      lab.setPixmap(item)
    else:
      lab.setText(item.strip())
    lab.setAlignment(QtCore.Qt.AlignCenter)
    lab.setMargin(0)
    l.addWidget(lab)
  w.setLayout(l)
  return w


def hex(num, digits):
  # Consolidate formatting for consistency
  #return '{:0{}X}₁₆'.format(num, digits)
  return HEX_PREFIX + '{:0{}X}'.format(num, digits)


def main():
  app = QApplication(sys.argv)
  mainwindow = FF5Reader()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()
