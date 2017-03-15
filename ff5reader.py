#!python3 -i
'''
No license for now
'''

import sys
import os
import struct
from array import array
from snestile import create_tile, create_tritile
import const
import time

pyqt_version = 0
skip_pyqt5 = "PYQT4" in os.environ

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
              "Make sure you installed the PyQt4 package.")
        sys.exit(-1)

monofont = QFont()
monofont.setStyleHint(QFont.Monospace)
if not monofont.fixedPitch():
    monofont.setStyleHint(QFont.TypeWriter)
if not monofont.fixedPitch():
    monofont.setFamily("Monospace")

def divceil(numerator, denominator):
    # Reverse floor division for ceil
    return -(-numerator // denominator)

def hex_length(i):
    return divceil(i.bit_length(), 4)

filename = "Final Fantasy V (Japan) [En by RPGe v1.1].sfc"
with open(filename, 'rb') as file1:
    ROM = file1.read()
print(len(ROM), filename)
filename2 = "Final Fantasy V (Japan).sfc"
with open(filename2, 'rb') as file2:
    ROM2 = file2.read()
print(len(ROM2), filename2)

col_palette = [QColor(0, 0, 0), QColor(0, 0, 128, 0),
               QColor(128, 128, 128), QColor(255, 255, 255)]
bg_color = QColor(0, 0, 128)

glyph_sprites = []
glyph_sprites_dialogue = []
glyph_sprites_jp = []
glyph_sprites_large = []
glyph_sprites_kanji = []

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
        generate_glyphs_large(ROM, glyph_sprites_dialogue, 0x03E800)
        generate_glyphs(ROM2, glyph_sprites_jp, 0x11F000)
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
                        ("Music", 1, const.BGM_Tracks)]
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
                    zone_data[-1].append("0x{:0{}X}".format(val, z[1]*2))
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
                        npc_layers[-1].append("0x{:0{}X}".format(val, z[1]*2))
            j += z[1]

        dialogue = make_string_img_list(0x2013F0, 3, 0x500, start_jp=0x082220, len_jp=2, start_str=0x0, start_jp_str=0x0A0000, indirect=True, large=True, macros=True)  # start_str=0x210000

        self.tabwidget = QTabWidget()
        self.enemy_sprites = QFrame()
        self.tabwidget.addTab(make_pixmap_table(glyph_sprites, 4), "Glyphs (EN)")
        self.tabwidget.addTab(make_pixmap_table(glyph_sprites_dialogue, 2), "Glyphs (Dialogue EN)")
        self.tabwidget.addTab(make_pixmap_table(glyph_sprites_jp, 4), "Glyphs (JP)")
        self.tabwidget.addTab(make_pixmap_table(glyph_sprites_large, 2), "Glyphs (Large JP)")
        self.tabwidget.addTab(make_pixmap_table(glyph_sprites_kanji, 2), "Glyphs (Kanji)")
        self.tabwidget.addTab(self.enemy_sprites, "Enemy Sprites")
        self.tabwidget.addTab(make_table(zone_headers, zone_data, True), "Zones")
        self.tabwidget.addTab(make_table(imglist_headers, zone_names, True), "Zone Names")
        self.tabwidget.addTab(make_table(npc_layer_headers, npc_layers, True), "NPC Layers")
        self.tabwidget.addTab(make_table(imglist_headers, items, row_labels=False), "Items")
        self.tabwidget.addTab(make_table(imglist_headers, magics, row_labels=False), "Magics")
        self.tabwidget.addTab(make_table(imglist_headers, more_magics, row_labels=False), "More Magics")
        self.tabwidget.addTab(make_table(imglist_headers, enemy_names, row_labels=False), "Enemy Names")
        self.tabwidget.addTab(make_table(imglist_headers+['JP address'], dialogue), "Dialogue")

        layout = QHBoxLayout()
        layout.addWidget(self.tabwidget)
        self.main_widget = QWidget(self)
        self.main_widget.setLayout(layout)
        self.setCentralWidget(self.main_widget)
        self.show()


def generate_glyphs(rom, spritelist, offset, num=0x100, palette=col_palette):
    for i in range(num):
        j = offset + (i*16)
        spritelist.append(create_tile(rom[j:j+16], palette))

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
            string = string + const.Glyphs_JP2[j]
            if 0x20 <= j < 0x52:
                if j > 0x48:
                    painter.drawPixmap(x*8, 2, glyph_sprites_jp[j+0x17])
                    painter.drawPixmap(x*8+1,-5, glyph_sprites_jp[0x52])
                else:
                    painter.drawPixmap(x*8, 2, glyph_sprites_jp[j+0x40])
                    painter.drawPixmap(x*8+1,-6, glyph_sprites_jp[0x51])
            else:
                painter.drawPixmap(x*8, 2, glyph_sprites_jp[j])
    else:
        for x, j in enumerate(bytestring):
            string = string + const.Glyphs[j]
            painter.drawPixmap(x*8, 1, glyph_sprites[j])
    del painter
    return string, QPixmap.fromImage(img)

def dialogue_preprocessor(bytestring, macros=False):
    '''
    This deals with pesky control codes that lump in the following byte.
    Additionally, it can expand the macros used in JP dialogue.
    '''
    out = []
    bytes = iter(bytestring)
    for b in bytes:
        if b in const.DoubleChars:
            b2 = next(bytes)
            out.append((b<<8) + b2)
        elif macros and b in const.Dialogue_Macros:
                out.extend(const.Dialogue_Macros[b])
        else:
            out.append(b)
    return out

def make_string_img_multiline(bytestring):
    '''
    This is basically make_string_img_large() but for english dialogue.
    English characters have varying widths, so instead of x being an index it's a pixel value. Magic, eh?
    '''
    if len(bytestring) < 1:
        raise ValueError('Empty bytestring was passed')

    string = ""
    max_width = 32*8  # I need to confirm this
    rows = 32  # This is just for testing
    img = QImage(max_width, rows*16, QImage.Format_RGB16)
    img.fill(bg_color)
    painter = QtGui.QPainter(img)

    x = xmax = y = 0
    for j in bytestring:
        if x >= max_width:  # Wrap on long line
            string += '[wr]\n'
            xmax = max_width  # Can't go higher than this anyway
            x = 0
            y += 1
        if j == 0x01:  # Line break
            string += '[br]\n'
            xmax = x if x > xmax else xmax
            x = 0
            y += 1
            continue
        elif j < 0x13 or j > 0xFF:  # Everything remaining outside this is a control char
            string += '[0x{:02X}]'.format(j)
            continue
        else:
            string += const.Glyphs[j]
            painter.drawPixmap(x, (y*16)+4, glyph_sprites_dialogue[j])
            x += const.Dialogue_Width[j]
    del painter
    xmax = x if x > xmax else xmax
    return string, QPixmap.fromImage(img.copy(0, 0, xmax, (y+1)*16))

def make_string_img_large(bytestring):
    '''
    This is how we decipher dialogue data, which has multiple lines among other things
    '''
    if len(bytestring) < 1:
        raise ValueError('Empty bytestring was passed')

    string = ""
    cols = 16  # This is the maximum dialogue glyphs per row in JP
    rows = 32  # This is just for testing
    img = QImage(cols*16, rows*16, QImage.Format_RGB16)
    img.fill(bg_color)
    painter = QtGui.QPainter(img)

    x = xmax = y = 0
    for j in bytestring:
        if x >= cols:  # Wrap on long line
            string += '[wr]\n'
            xmax = cols  # Can't go higher than this anyway
            x = 0
            y += 1
        if j == 0x01:  # Line break
            string += '[br]\n'
            xmax = x if x > xmax else xmax
            x = 0
            y += 1
            continue
        elif 0x1E00 <= j < 0x1FAA:  # Kanji live in this range
            string += const.Glyphs_Kanji[j-0x1E00]
            painter.drawPixmap(x*16, (y*16)+2, glyph_sprites_kanji[j-0x1E00])
        elif j < 0x13 or j > 0xFF:  # Everything remaining outside this is a control char
            string += '[0x{:02X}]'.format(j)
            continue
        else:
            string += const.Glyphs_JP_large[j]
            painter.drawPixmap(x*16, (y*16)+2, glyph_sprites_large[j])
        x += 1
    del painter
    xmax = x if x > xmax else xmax
    return string, QPixmap.fromImage(img.copy(0, 0, xmax*16, (y+1)*16))

def make_string_img_list(start, length, num, start_jp=None, len_jp=None, start_str=None, start_jp_str=None, indirect=False, large=False, macros=False):
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
                    if macros:
                        string, img = make_string_img_multiline(dialogue_preprocessor(ROM[en_start:en_end]))
                    else:
                        string, img = make_string_img(ROM[en_start:en_end])
                else:
                    string = ''
                    img = None

                if jp_end > jp_start:
                    bytestring = dialogue_preprocessor(ROM2[jp_start:jp_end], macros)
                    if large:
                        string_JP, img_JP = make_string_img_large(bytestring)
                    else:
                        string_JP, img_JP = make_string_img(bytestring, jp=True)
                else:
                    string_JP = ''
                    img_JP = None
            except ValueError:
                print("ID: {} \tRef.0x{:06X} 0x{:06X} \tRange EN: 0x{:06X}-0x{:06X} \tRange JP: 0x{:06X}-0x{:06X}".format(id, en, jp, en_start, en_end, jp_start, jp_end))
                raise
            stringlist.append(["0x{:06X}".format(en), "0x{:0{}X}".format(id, id_digits), string, img, string_JP, img_JP, "0x{:06X}".format(jp_start)])
    else:
        for id in range(num):
            j1 = start + (id*length)
            j2 = start_jp + (id*len_jp)
            string, img = make_string_img(ROM[j1:j1+length])
            if large:
                string_JP, img_JP = make_string_img_large(ROM2[j2:j2+len_jp])
            else:
                string_JP, img_JP = make_string_img(ROM2[j2:j2+len_jp], jp=True)
            stringlist.append(["0x{:06X}".format(j1), "0x{:0{}X}".format(id, id_digits), string, img, string_JP, img_JP])
    return stringlist

def make_table(headers, items, sortable=False, row_labels=True):
    """
    Helper function to tabulate 2d lists
    """
    cols = len(headers)
    rows = len(items)
    rd = hex_length(rows-1)
    table = QTableWidget(rows, cols)
    if row_labels:
        table.setVerticalHeaderLabels(['0x{:0{}X}'.format(v, rd) for v in range(rows)])
    else:
        table.verticalHeader().setVisible(False)
    table.setHorizontalHeaderLabels(headers)
    for row, col, item in [(x,y,items[x][y]) for x in range(rows) for y in range(cols)]:
        if type(item) == type(QPixmap()):
            lab = QLabel()
            lab.setPixmap(item.scaled(item.size() * 2))
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
    cols = 16
    rows = divceil(len(items), cols)
    rd = hex_length(rows-1)+1
    table = QTableWidget(rows, cols)
    table.setVerticalHeaderLabels(['0x{:0{}X}'.format(v*cols, rd) for v in range(rows)])
    table.setHorizontalHeaderLabels(['0x{:X}'.format(v) for v in range(cols)])
    for i in range(len(items)):
        item = items[i]
        lab = QLabel()
        lab.setPixmap(item.scaled(item.size() * scale))
        table.setCellWidget(i // cols, i % cols, lab)
    table.resizeColumnsToContents()
    return table


def main():
    app = QApplication(sys.argv)
    mainwindow = FF5Reader()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
