#!python3 -i
'''
No license for now
'''

import sys
import os
import struct
from array import array
#from heximg import HexImg

pyqt_version = 0
skip_pyqt5 = True  # "PYQT4" in os.environ

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
              "Make sure you installed the PyQt5 package.")
if pyqt_version is 0:
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
              "Make sure you installed the PyQt4 package.")
        sys.exit(-1)

monofont = QFont()
monofont.setStyleHint(QFont.Monospace)
if not monofont.fixedPitch():
    monofont.setStyleHint(QFont.TypeWriter)
if not monofont.fixedPitch():
    monofont.setFamily("Monospace")
                                                 #"Ubuntu Mono",
                                                 #"DejaVu Sans Mono",
                                                 #"Liberation Mono",
                                                 #"courier"])
#monofont.setPixelSize(8)

def divceil(numerator, denominator):
    # Reverse floor division for ceil
    return -(-numerator // denominator)

def hex_length(i):
    return divceil(i.bit_length(), 4)

filename = "Final Fantasy V (Japan) [En by RPGe v1.1].sfc"
with open(filename, 'rb') as file1:
    ROM = file1.read()
print(len(ROM))
filename2 = "Final Fantasy V (Japan).sfc"
with open(filename2, 'rb') as file2:
    ROM2 = file2.read()
print(len(ROM2))

col_palette = [QColor(  0,  0,  0),
               QColor(  0,  0,128,0),
               QColor(128,128,128),
               QColor(255,255,255)]
bg_color = QColor(0, 0, 128)
#for i in range(4, 256):
    #col_palette.append(QColor(i, i, i))

def create_tile(bytes):
    '''
    Creates a QPixmap of a SNES tile. DO NOT USE OUTSIDE OF QApplication CONTEXT
    '''
    planes = len(bytes)//8
    tile = array('B', range(64))
    img = QImage(8, 8, QImage.Format_Indexed8)
    imgbits = img.bits()
    imgbits.setsize(img.byteCount())
    if planes == 0:
        raise ValueError("Empty bytes passed")
    if planes == 1:
        img.setColorTable([0x00000080, 0xFFFFFFFF])
        t_ptr = 0
        for j, x in [(j,x) for j in range(8) for x in reversed(range(8))]:
            tile[t_ptr] = (bytes[j] >> x & 1)
            t_ptr += 1
    else:
        img.setColorTable([c.rgba() for c in col_palette])
        t_ptr = 0
        for j, x in [(j,x) for j in range(0, 16, 2) for x in reversed(range(8))]:
            tile[t_ptr] = (bytes[j] >> x & 1) | ((bytes[j+1] >> x & 1) << 1)
            t_ptr += 1
        t_ptr = 0
        if planes == 3:
            for j, x in [(j,x) for j in range(16, 24, 1) for x in reversed(range(8))]:
                tile[t_ptr] |= ((bytes[j] >> x & 1) << 2)
                t_ptr += 1
        elif planes >= 4:
            for j, x in [(j,x) for j in range(16, 32, 2) for x in reversed(range(8))]:
                tile[t_ptr] |= ((bytes[j] >> x & 1) << 2) | ((bytes[j+1] >> x & 1) << 3)
                t_ptr += 1
        if planes == 8:
            t_ptr = 0
            for j, x in [(j,x) for j in range(32, 48, 2) for x in reversed(range(8))]:
                tile[t_ptr] |= ((bytes[j] >> x & 1) << 4) | ((bytes[j+1] >> x & 1) << 5) \
                    | ((bytes[j+16] >> x & 1) << 6) | ((bytes[j+17] >> x & 1) << 7)
                t_ptr += 1
    imgbits[:64] = tile
    return QPixmap.fromImage(img)

def create_tritile(bytes):
    img = QImage(16, 12, QImage.Format_Indexed8)
    imgbits = img.bits()
    imgbits.setsize(img.byteCount())
    img.setColorTable([0xFF000080, 0xFFFFFFFF])
    tile = array('B', range(192))
    for p, row, b in [(p,j,b) for p in range(2) for j in range(12) for b in reversed(range(8))]:
        tile[(7-b) + (row*16) + (p*8)] = (bytes[row + (p*12)] >> b & 1)
    imgbits[:192] = tile
    return QPixmap.fromImage(img)

def create_quadtile(bytes, ltr=False):
    img = QImage(16, 16, QImage.Format_ARGB32_Premultiplied)
    img.fill(QColor(0,0,0,0))
    painter = QtGui.QPainter(img)
    painter.drawPixmap(0, 0, create_tile(bytes[0:8]))
    painter.drawPixmap(8, 8, create_tile(bytes[24:32]))
    if ltr:
        painter.drawPixmap(8, 0, create_tile(bytes[8:16]))
        painter.drawPixmap(0, 8, create_tile(bytes[16:24]))
    else:
        painter.drawPixmap(0, 8, create_tile(bytes[8:16]))
        painter.drawPixmap(8, 0, create_tile(bytes[16:24]))
    del painter
    return QPixmap.fromImage(img)

glyph_sprites = []
glyph_sprites2 = []
glyph_sprites_large = []
glyph_sprites_kanji = []

Glyphs = (
    ' ',' ',' ',' ',    ' ',' ',' ',' ',    ' ',' ',' ',' ',    ' ',' ',' ',' ',      # 0x00
    ' ',' ',' ',' ',    ' ',' ',' ',' ',    ' ',' ',' ',' ',    ' ',' ',' ',' ',      # 0x10
    'A','B','C','D',    'E','F','G','H',    'I','J','K','L',    'M','N','O','P',      # 0x20
    'Q','R','S','T','U','V','W','X','Y','Z','[stone]','[toad]','[mini]','[float]','[poison]','[KO]',  # 0x30
    '[blind]',' ',' ',' ',' ',' ',' ',' ',  ' ',' ',' ',' ',    ' ',' ',' ',' ',      # 0x40
    ' ',' ',' ','0',    '1','2','3','4',    '5','6','7','8',    '9','_m','_H','_P',   # 0x50
    'A','B','C','D',    'E','F','G','H',    'I','J','K','L',    'M','N','O','P',      # 0x60
    'Q','R','S','T',    'U','V','W','X',    'Y','Z','a','b',    'c','d','e','f',      # 0x70
    'g','h','i','j',    'k','l','m','n',    'o','p','q','r',    's','t','u','v',      # 0x80
    'w','x','y','z',    'il','it',' ','li', 'll','\'','"',':',   ';',',','(',')',     # 0x90
    '/','!','?','.',    'ti','fi','Bl','a', 'pe','l','\'','"',   'if','lt','tl','ir', # 0xA0
    'tt','や','ユ','ゆ', 'ヨ', 'よ', 'ワ', 'わ', 'ン', 'ん', 'ヲ','を', '[key]', '[shoe]', '◆', '[hammer]',  # 0xB0
    '⛺', '[ribbon]', '[potion]', '[shirt]', '♪', '-', '[shuriken]', '‥', '[scroll]', '!', '[claw]', '?', '[glove]', '%', '/', ':',    # 0xC0
    '「', '」', '0', 'A', 'B', 'X', 'Y', 'L', 'R', 'E', 'H', 'M', 'P', 'S', 'C', 'T',    # 0xD0
    '↑', '→', '+', '[sword]', '[wh.mag]', '[blk.mag]', '🕒', '[knife]', '[spear]', '[axe]', '[katana]', '[rod]', '[staff]', '[bow]', '[harp]', '[whip]',   # 0xE0
    '[bell]', '[shield]', '[helmet]', '[armor]', '[ring]', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ')    # F0
Glyphs_JP = list(Glyphs)  # Transcription of the japanese glyph tiles
Glyphs_JP[0x60:0xCD] = [
    'ハ','は','ヒ','ひ',  'フ','ふ','ヘ','へ',  'ホ','ほ','カ','か',  'キ','き','ク','く',  # 0x60
    'ケ','け','コ','こ',  'サ','さ','シ','し',  'ス','す','セ','せ',  'ソ','そ','タ','た',  # 0x70
    'チ','ち','ツ','つ',  'テ','て','ト','と',  'ウ','う','ア','あ',  'イ','い','エ','え',  # 0x80
    'オ','お','ナ','な',  'ニ','に','ヌ','ぬ',  'ネ','ね','ノ','の',  'マ','ま','ミ','み',  # 0x90
    'ム','む','メ','め',  'モ','も','ラ','ら',  'リ','り','ル','る',  'レ','れ','ロ','ろ',  # 0xA0
    'ヤ','や','ユ','ゆ',  'ヨ','よ','ワ','わ',  'ン','ん','ヲ','を',  'ッ','っ','ャ','ゃ',  # 0xB0
    'ュ','ゅ','ョ','ょ',  'ァ','ー','ィ', '‥',  'ぅ','！','ェ','？',  'ォ']              # 0xC0
Glyphs_JP[0xE3] = '[洋剣]'
Glyphs_JP[0xE7:0xF0] = ['[刂]', '[槍]', '[鉞]', '[刀]', '[棒]', '[杖]', '[弓]', '♪', '[鞭]']
Glyphs_JP2 = list(Glyphs_JP)  # Japanese glyphs using the dakuten encoding
Glyphs_JP2[0x20:0x52] = [
    'バ','ば','ビ','び',  'ブ','ぶ','ベ','べ',  'ボ','ぼ','ガ','が',  'ギ','ぎ','グ','ぐ',  # 0x20
    'ゲ','げ','ゴ','ご',  'ザ','ざ','ジ','じ',  'ズ','ず','ゼ','ぜ',  'ゾ','ぞ','ダ','だ',  # 0x30
    'ヂ','ぢ','ヅ','づ',  'デ','で','ド','ど',             # 0x40-0x48
    'パ','ぱ','ピ','ぴ',  'プ','ぷ','ペ','ぺ',  'ポ','ぽ']  # 0x48-0x52
Glyphs_JP_large = list(Glyphs_JP2)  # Large glyphs are subtly different again
Glyphs_JP_large[0xE0:0xEB] = ['←','→','+','、',  '◯', '『', 'Ｆ', '°C',  '・', '（', '）']

Glyphs_Kanji = (
    '王','行','力','様',    '　','　','　','　',    '入','城','　','士',    '　','　','　','父',  # 0x000
    '人','見','　','　',    '大','　','　','何',    '　','　','　','　',    '　','　','　','　',  # 0x010
    '　','心','間','　',    '風','　','　','　',    '　','　','　','　',    '火','　','　','　',  # 0x020
    '　','　','　','　',    '　','　','　','　',    '地','　','　','　',    '　','　','　','　',  # 0x030
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','一','　','　',  # 0x040
    '　','　','神','　',    '　','　','殿','　',    '　','　','　','　',    '　','　','　','　',  # 0x050
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x060
    '　','　','階','　',    '　','　','　','　',    '　','　','土','　',    '　','　','　','　',  # 0x070

    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x080
    '　','　','　','　',    '　','下','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x090
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x0A0
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x0B0
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','少','　','　',  # 0x0C0
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x0D0
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x0E0
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x0F0

    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x100
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x110
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x120
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x130
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x140
    '炎','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x150
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x160
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x170

    '　','　','　','　',    '　','　','　','　',    '　','刀','　','　',    '　','　','　','　',  # 0x180
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x190
    '　','　','　','　',    '　','　','　','　',    '　','　')                                  # 0x1A0

BGM_Tracks = (
    "Ahead on our way", "The Fierce Battle", "A Presentiment", "Go Go Boko!",
    "Pirates Ahoy", "Tenderness in the Air", "Fate in Haze", "Moogle theme",
    "Prelude/Crystal Room", "The Last Battle", "Requiem", "Nostalgia",
    "Cursed Earths", "Lenna's Theme", "Victory's Fanfare", "Deception",
    "The Day Will Come", "Nothing?", "ExDeath's Castle", "My Home, Sweet Home",
    "Waltz Suomi", "Sealed Away", "The Four Warriors of Dawn", "Danger",
    "The Fire Powered Ship", "As I Feel, You Feel", "Mambo de Chocobo!", "Music Box",
    "Intension of the Earth", "The Dragon Spreads its Wings", "Beyond the Deep Blue Sea", "The Prelude of Empty Skies",
    "Searching the Light", "Harvest", "Battle with Gilgamesh", "Four Valiant Hearts",
    "The Book of Sealings", "What?", "Hurry! Hurry!", "Unknown Lands",
    "The Airship", "Fanfare 1", "Fanfare 2", "The Battle",
    "Walking the Snowy Mountains", "The Evil Lord Exdeath", "The Castle of Dawn", "I'm a Dancer",
    "Reminiscence", "Run!", "The Ancient Library", "Royal Palace",
    "Good Night!", "Piano Lesson 1", "Piano Lesson 2", "Piano Lesson 3",
    "Piano Lesson 4", "Piano Lesson 5", "Piano Lesson 6", "Piano Lesson 7",
    "Piano Lesson 8", "Musica Machina", "Meteor falling?", "The Land Unknown",
    "The Decisive Battle", "The Silent Beyond", "Dear Friends", "Final Fantasy",
    "A New Origin", "Chirping sound")

stringlist_headers = ["Address", "ID", "Name"]
imglist_headers = stringlist_headers + ["Img", "Name JP", "Img JP"]



npc_layer_count = 0x200
npc_layer_structure = [("Dialogue/trigger ID", 1, None),
                       ("0x01", 1, None),
                       ("Sprite ID", 1, None),
                       ("X", 1, None),
                       ("Y", 1, None),
                       ("Move Pattern", 1, None),
                       ("Palette", 1, None)]
npc_layer_headers = ["Address", "Layer"] + [x[0] for x in npc_layer_structure]



class FF5Reader(QMainWindow):
    """
    Main GUI class
    """
    def __init__(self):
        QMainWindow.__init__(self, None)
        generate_glyphs(ROM, glyph_sprites, 0x11F000)
        generate_glyphs(ROM2, glyph_sprites2, 0x11F000)
        generate_glyphs_large(ROM2, glyph_sprites_large, 0x03E800)
        generate_glyphs_large(ROM2, glyph_sprites_kanji, 0x1BD000, 0x1AA)
        global zone_names
        zone_names = make_string_img_list(0x107000, 2, 0x100, start_str=0x270000, start_jp_str=0x107200, indirect=True, large=True)
        items = make_string_img_list(0x111380, 9, 256)
        magics = make_string_img_list(0x111C80, 6, 87)
        more_magics = make_string_img_list(0x111E8A, 9, 73)
        enemy_names = make_string_img_list(0x200050, 10, 0x180, 0x105C00, 8)
        zone_count = 0x200
        zone_structure = [("NPC Layer", 2, None),
                        ("Name", 1, zone_names),
                        ("ShadowFlags", 1, None),
                        ("0x04", 1, None),
                        ("0x05",           1, None),
                        ("Flags 0x06",     1, None),
                        ("0x07",           1, None),
                        ("Tileset",        1, None),
                        ("Tileset2",       2, None),
                        #("0x0A",           1, None),
                        ("0x0B",           1, None),
                        ("Collision Layer",1, None),
                        ("0x0D",           1, None),
                        ("0x0E",           1, None),
                        ("0x0F",           1, None),
                        ("0x10",           1, None),
                        ("0x11",           1, None),
                        ("0x12",           1, None),
                        ("0x13",           1, None),
                        ("0x14",           1, None),
                        ("0x15",           1, None),
                        ("Palette",        1, None),
                        ("0x17",           1, None),
                        ("0x18",           1, None),
                        ("Music", 1, BGM_Tracks)]
        zone_headers = ["Address"] + [z[0] for z in zone_structure]

        zone_data = []
        for i in range(zone_count):
            zone_data.append([])
            offset = 0x0E9C00 + (i*0x1A)
            zone_data[-1].append("0x{:06X}".format(offset))
            j = 0
            for z in zone_structure:
                val = int.from_bytes(ROM[offset+j:offset+j+z[1]],'little')
                if z[2] and val < len(z[2]):
                    zone_data[-1].append(z[2][val][2])
                else:
                    zone_data[-1].append("0x{0:0{1}X}".format(val, z[1]*2))
                j += z[1]

        npc_layers = []
        for layer in range(npc_layer_count):
            offset = 0x0E59C0
            i = offset + (layer*2)
            start = int.from_bytes(ROM[i:i+2],'little') + offset
            next = int.from_bytes(ROM[i+2:i+4],'little') + offset
            npcs = (next - start) // 7
            for npc in range(npcs):
                address = start + (npc*7)
                npc_layers.append(["0x{0:06X}".format(address), "0x{0:03X}".format(layer)])
                j = 0
                for z in npc_layer_structure:
                    val = int.from_bytes(ROM[start+j:start+j+z[1]],'little')
                    if z[2] and val < len(z[2]):
                        npc_layers[-1].append(z[2][val])
                    else:
                        npc_layers[-1].append("0x{0:0{1}X}".format(val, z[1]*2))
            j += z[1]

        dialogue = make_string_img_list(0x2013F0, 3, 0x500, start_jp=0x082220, len_jp=2, start_str=0x0, start_jp_str=0x0A0000, indirect=True, large=True)  # start_str=0x210000

        self.tabwidget = QTabWidget()
        self.enemy_sprites = QFrame()
        self.tabwidget.addTab(make_pixmap_table(glyph_sprites, 4), "Glyphs (EN)")
        self.tabwidget.addTab(make_pixmap_table(glyph_sprites2, 4), "Glyphs (JP)")
        self.tabwidget.addTab(make_pixmap_table(glyph_sprites_large, 2), "Glyphs (Large)")
        self.tabwidget.addTab(make_pixmap_table(glyph_sprites_kanji, 2), "Glyphs (Kanji)")
        self.tabwidget.addTab(self.enemy_sprites, "Enemy Sprites")
        self.tabwidget.addTab(make_table(zone_headers, zone_data, True), "Zones")
        self.tabwidget.addTab(make_table(imglist_headers, zone_names, True), "Zone Names")
        self.tabwidget.addTab(make_table(npc_layer_headers, npc_layers, True), "NPC Layers")
        self.tabwidget.addTab(make_table(imglist_headers, items, row_labels=False), "Items")
        self.tabwidget.addTab(make_table(imglist_headers, magics, row_labels=False), "Magics")
        self.tabwidget.addTab(make_table(imglist_headers, more_magics, row_labels=False), "More Magics")
        self.tabwidget.addTab(make_table(imglist_headers, enemy_names, row_labels=False), "Enemy Names")
        self.tabwidget.addTab(make_table(imglist_headers, dialogue), "Dialogue")

        layout = QHBoxLayout()
        layout.addWidget(self.tabwidget)
        self.main_widget = QWidget(self)
        self.main_widget.setLayout(layout)
        self.setCentralWidget(self.main_widget)
        self.show()


def generate_glyphs(rom, spritelist, offset, num=0x100):
    for i in range(num):
        j = offset + (i*16)
        spritelist.append(create_tile(rom[j:j+16]))

def generate_glyphs_large(rom, spritelist, offset, num=0x100):
    for i in range(num):
        j = offset + (i*24)
        spritelist.append(create_tritile(rom[j:j+24]))

def make_string_img(bytestring, jp=False):
    if len(bytestring) < 1:
        raise ValueError('Empty bytestring was passed')
    string = ""
    img = QImage(len(bytestring)*8, 10, QImage.Format_RGB16)
    img.fill(bg_color)
    painter = QtGui.QPainter(img)
    if jp:
        for x, j in enumerate(bytestring):
            string = string + Glyphs_JP2[j]
            if 0x20 <= j < 0x52:
                if j > 0x48:
                    painter.drawPixmap(x*8, 2, glyph_sprites2[j+0x17])
                    painter.drawPixmap(x*8+1,-5, glyph_sprites2[0x52])
                else:
                    painter.drawPixmap(x*8, 2, glyph_sprites2[j+0x40])
                    painter.drawPixmap(x*8+1,-6, glyph_sprites2[0x51])
            else:
                painter.drawPixmap(x*8, 2, glyph_sprites2[j])
    else:
        for x, j in enumerate(bytestring):
            string = string + Glyphs[j]
            painter.drawPixmap(x*8, 1, glyph_sprites[j])
    del painter
    return string, QPixmap.fromImage(img)

def make_string_img_large(bytestring):
    if len(bytestring) < 1:
        raise ValueError('Empty bytestring was passed')
    string = ""
    rows = 20  # This is just for testing
    img = QImage(len(bytestring)*16, 14*rows, QImage.Format_RGB16)
    img.fill(bg_color)
    painter = QtGui.QPainter(img)

    it = iter(range(len(bytestring)))
    x = 0
    xmax = x
    y = 0
    tabstop = 0
    try:
        for i in it:
            j = bytestring[i]
            '''
            There's a lot of dialogue substitutions, this is going to be annoying and/or messy.
            Is 0x00 a wait for input marker?
            0x03 is クリスタル
            0x0A is a speaker tab, perhaps linebreak as well?
            0x0D appears to expand to 風の神殿
            : (0xCF) appears to expand to って
            S (0xDD) to ……
            C (0xDE) to だいじょうぶ
            T (0xDF) to は、
            ◯ (0xE4) appears to expand to して
            F (0xE6) appears to expand to otousan (お父様)
            ・ (0xE8) appears to expand to です
            % (0xCD) to !!
            °C (0xE7) to !?
            '''
            if j == 0x01:
                string = string + '\n[0x01]'
                y += 1
                xmax = x if x > xmax else xmax
                x = 0
                continue
            elif j == 0x09:
                string = string + '\t[0x09]'
                x = tabstop
                continue
            elif j == 0x0A:
                if x != 0:
                    y += 1
                    xmax = x if x > xmax else xmax
                    string = string + '\n'
                string = string + '\t[0x0A]'
                x = tabstop
                continue
            elif j == 0x19:
                # Lenna is speaking
                string = string + "[レナ「]"
                painter.drawPixmap(0*16, (y*14)+1, glyph_sprites_large[0xAC])
                painter.drawPixmap(1*16, (y*14)+1, glyph_sprites_large[0x92])
                painter.drawPixmap(2*16, (y*14)+1, glyph_sprites_large[0xD0])
                x += 3
                tabstop = x
                continue
            elif j == 0x1B:
                # Faris is speaking
                string = string + "[ファリス「]"
                painter.drawPixmap(0*16, (y*14)+1, glyph_sprites_large[0x64])
                painter.drawPixmap(1*16, (y*14)+1, glyph_sprites_large[0xC4])
                painter.drawPixmap(2*16, (y*14)+1, glyph_sprites_large[0xA8])
                painter.drawPixmap(3*16, (y*14)+1, glyph_sprites_large[0x78])
                painter.drawPixmap(4*16, (y*14)+1, glyph_sprites_large[0xD0])
                x += 5
                tabstop = x
                continue
            elif j < 0x1E:
                string = string + '[0x{:02X}]'.format(j)
                continue
            elif j == 0x1E:
                string = string + Glyphs_Kanji[bytestring[i+1]]
                painter.drawPixmap(x*16, (y*14)+1, glyph_sprites_kanji[bytestring[i+1]])
                next(it)
            elif j == 0x1F:
                string = string + Glyphs_Kanji[0x100 + bytestring[i+1]]
                painter.drawPixmap(x*16, (y*14)+1, glyph_sprites_kanji[0x100 + bytestring[i+1]])
                next(it)
            else:
                string = string + Glyphs_JP_large[j]
                painter.drawPixmap(x*16, (y*14)+1, glyph_sprites_large[j])
            x += 1
            if (j == 0xD0) or (j == 0xE5):
                tabstop = x
    except (StopIteration, IndexError):
        pass
    del painter
    xmax = x if x > xmax else xmax
    return string, QPixmap.fromImage(img.copy(0, 0, xmax*16, (y+1)*14))

def make_string_img_list(start, length, num, start_jp=None, len_jp=None, start_str=None, start_jp_str=None, indirect=False, large=False):
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
            en_start = int.from_bytes(ROM[en:en+length],'little') + start_str
            en_end = int.from_bytes(ROM[en+length:en+(length*2)],'little') + start_str
            if en_start >= 0xC00000:
                en_start -= 0xC00000
                en_end -= 0xC00000
            jp_start = int.from_bytes(ROM2[jp:jp+len_jp],'little') + start_jp_str
            jp_end = int.from_bytes(ROM2[jp+len_jp:jp+(len_jp*2)],'little') + start_jp_str
            if (en_end == start_str) or (jp_end == start_jp_str) or (en_end > len(ROM)) or (jp_end > len(ROM2)):
                break
            try:
                if en_end > en_start:
                    string, img = make_string_img(ROM[en_start:en_end])
                else:
                    string = ''
                    img = None

                if jp_end > jp_start:
                    if large:
                        string_JP, img_JP = make_string_img_large(ROM2[jp_start:jp_end])
                    else:
                        string_JP, img_JP = make_string_img(ROM2[jp_start:jp_end], jp=True)
                else:
                    string_JP = ''
                    img_JP = None
            except ValueError:
                print("ID: {} \tRef.0x{:06X} 0x{:06X} \tRange EN: 0x{:06X}-0x{:06X} \tRange JP: 0x{:06X}-0x{:06X}".format(id, en, jp, en_start, en_end, jp_start, jp_end))
                raise
            stringlist.append(["0x{:06X}".format(en), "0x{0:0{1}X}".format(id, id_digits), string, img, string_JP, img_JP, "0x{:06X}".format(jp_start)])
    else:
        for id in range(num):
            j1 = start + (id*length)
            j2 = start_jp + (id*len_jp)
            string, img = make_string_img(ROM[j1:j1+length])
            if large:
                string_JP, img_JP = make_string_img_large(ROM2[j2:j2+len_jp])
            else:
                string_JP, img_JP = make_string_img(ROM2[j2:j2+len_jp], jp=True)
            stringlist.append(["0x{:06X}".format(j1), "0x{0:0{1}X}".format(id, id_digits), string, img, string_JP, img_JP])
    return stringlist

def make_table(headers, items, sortable=False, row_labels=True):
    """
    Helper function to tabulate 2d lists
    """
    table = QTableWidget()
    rows = len(items)
    rd = hex_length(rows-1)
    cols = len(headers)
    table.setRowCount(rows)
    if row_labels:
        table.setVerticalHeaderLabels(['0x{0:0{1}X}'.format(v, rd) for v in range(rows)])
    else:
        table.verticalHeader().setVisible(False)
    table.setColumnCount(cols)
    table.setHorizontalHeaderLabels(headers)
    for row, col, item in [(x,y,items[x][y]) for x in range(rows) for y in range(cols)]:
        if type(item) == type(QPixmap()):
            pixmap_scaled = item.scaled(item.size() * 2)
            lab = QLabel()
            lab.setPixmap(pixmap_scaled)
            table.setCellWidget(row, col, lab)
        elif item is not None:
            q_item = QTableWidgetItem(item)
            if item[:2] == "0x":
                q_item.setFont(monofont)
            table.setItem(row, col, q_item)

    # Stupid hack to get table to size correctly
    table.hide()
    geometry = table.viewport().geometry()
    table.viewport().setGeometry(QtCore.QRect(0, 0, 0x7FFFFFFF, 0x7FFFFFFF))
    table.resizeColumnsToContents()
    table.resizeRowsToContents()
    table.viewport().setGeometry(geometry)
    table.show()

    if sortable:
        table.setSortingEnabled(True)
        table.sortItems(0)
    return table

def make_pixmap_table(items, scale=4):
    table = QTableWidget()
    rows = divceil(len(items), 16)
    rd = hex_length(rows-1)+1
    cols = 16
    table.setRowCount(rows)
    table.setVerticalHeaderLabels(['0x{0:0{1}X}'.format(v*16, rd) for v in range(rows)])
    table.setColumnCount(cols)
    table.setHorizontalHeaderLabels(['0x{:X}'.format(v) for v in range(cols)])
    for i in range(len(items)):
        item = items[i]
        pixmap_scaled = item.scaled(item.size() * scale)
        lab = QLabel()
        lab.setPixmap(pixmap_scaled)
        table.setCellWidget(i // cols, i % cols, lab)
    table.resizeColumnsToContents()
    return table


def main():
    app = QApplication(sys.argv)

    mainwindow = FF5Reader()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
