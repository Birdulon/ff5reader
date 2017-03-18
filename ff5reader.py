#!python3 -i
'''
No license for now
'''

import sys
import os
from struct import unpack
from itertools import chain
from array import array
from snestile import generate_glyphs, generate_glyphs_large
import const
import time

pyqt_version = 0
skip_pyqt5 = "PYQT4" in os.environ
filename_en = "Final Fantasy V (Japan) [En by RPGe v1.1].sfc"
filename_jp = "Final Fantasy V (Japan).sfc"

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

bg_color = QColor(0, 0, 128)

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

with open(filename_en, 'rb') as file1:
    ROM_en = file1.read()
print(len(ROM_en), filename_en)
with open(filename_jp, 'rb') as file2:
    ROM_jp = file2.read()
print(len(ROM_jp), filename_jp)

stringlist_headers = ["Address", "ID", "Name"]
imglist_headers = stringlist_headers + ["Img", "Name JP", "Img JP"]


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
        #glyph_sprites_jp_dialogue = {i:v for i, v in chain(enumerate(glyph_sprites_jp_large[0x20:0xEB]), enumerate(glyph_sprites_kanji, 0x1E00))}
        global zone_names
        zone_names = make_string_img_list(0x107000, 2, 0x100, start_str=0x270000, start_jp_str=0x107200, indirect=True, large=True)
        items = make_string_img_list(0x111380, 9, 256)
        magics = make_string_img_list(0x111C80, 6, 87)
        more_magics = make_string_img_list(0x111E8A, 9, 73)
        enemy_names = make_string_img_list(0x200050, 10, 0x180, 0x105C00, 8)
        job_names = make_string_img_list(0x115600, 8, 22)
        dialogue = make_string_img_list(0x2013F0, 3, 0x900, start_jp=0x082220, len_jp=2, start_str=0x0, start_jp_str=0x0A0000, indirect=True, large=True, macros_en=const.Dialogue_Macros_EN, macros_jp=const.Dialogue_Macros_JP)

        zone_structure = [("NPC Layer", 2, None),
                        ("Name", 1, [z[2] for z in zone_names]),
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
        for i in range(const.zone_count):
            zone_data.append([])
            offset = 0x0E9C00 + (i*0x1A)
            zone_data[-1].append("0x{:06X}".format(offset))
            j = 0
            for z in zone_structure:
                val = int.from_bytes(ROM_en[offset+j:offset+j+z[1]],'little')
                if z[2] and val < len(z[2]):
                    zone_data[-1].append(z[2][val])
                else:
                    zone_data[-1].append("0x{:0{}X}".format(val, z[1]*2))
                j += z[1]

        tileset_headers = ("ID", "Offset", "Pointer", "Expected Length")
        tileset_data = []
        for i in range(0x1C):
            offset = 0x0F0000 + (i*2)
            pointer = 0x0F0000 + int.from_bytes(ROM_en[offset:offset+2],'little')
            length = int.from_bytes(ROM_en[offset+2:offset+4],'little') - int.from_bytes(ROM_en[offset:offset+2],'little')
            tileset_data.append(('0x{:02X}'.format(i), '0x{:06X}'.format(offset),
                                 '0x{:06X}'.format(pointer), '0x{:04X}'.format(length)))

        npc_layers = []
        for layer in range(const.npc_layer_count):
            offset = 0x0E59C0
            i = offset + (layer*2)
            start = int.from_bytes(ROM_en[i:i+2],'little') + offset
            next = int.from_bytes(ROM_en[i+2:i+4],'little') + offset
            npcs = (next - start) // 7
            for npc in range(npcs):
                address = start + (npc*7)
                npc_layers.append(["0x{0:06X}".format(address), "0x{0:03X}".format(layer)])
                j = 0
                for z in const.npc_layer_structure:
                    val = int.from_bytes(ROM_en[start+j:start+j+z[1]],'little')
                    if z[2] and val < len(z[2]):
                        npc_layers[-1].append(z[2][val])
                    else:
                        npc_layers[-1].append("0x{:0{}X}".format(val, z[1]*2))
            j += z[1]

        self.tabwidget = QTabWidget()
        strings_tab = QTabWidget()
        structs_tab = QTabWidget()
        sprites_tab = QTabWidget()
        self.tabwidget.addTab(strings_tab, "Strings")
        self.tabwidget.addTab(structs_tab, "Structs")
        self.tabwidget.addTab(sprites_tab, "Images")
        self.enemy_sprites = QFrame()

        sprites_tab.addTab(make_pixmap_table(glyph_sprites_en_small, 4), "Glyphs (EN)")
        sprites_tab.addTab(make_pixmap_table(glyph_sprites_en_large, 2), "Glyphs (Dialogue EN)")
        sprites_tab.addTab(make_pixmap_table(glyph_sprites_jp_small, 4), "Glyphs (JP)")
        sprites_tab.addTab(make_pixmap_table(glyph_sprites_jp_large, 2), "Glyphs (Large JP)")
        sprites_tab.addTab(make_pixmap_table(glyph_sprites_kanji, 2), "Glyphs (Kanji)")
        sprites_tab.addTab(self.enemy_sprites, "Enemy Sprites")

        structs_tab.addTab(make_table(zone_headers, zone_data, True), "Zones")
        structs_tab.addTab(make_table(tileset_headers, tileset_data, True), "Tilesets")
        structs_tab.addTab(make_table(const.npc_layer_headers, npc_layers, True), "NPC Layers")

        strings_tab.addTab(make_table(imglist_headers, items, row_labels=False), "Items")
        strings_tab.addTab(make_table(imglist_headers, magics, row_labels=False), "Magics")
        strings_tab.addTab(make_table(imglist_headers, more_magics, row_labels=False), "More Magics")
        strings_tab.addTab(make_table(imglist_headers, enemy_names, row_labels=False), "Enemy Names")
        strings_tab.addTab(make_table(imglist_headers, job_names, row_labels=False), "Job Names")
        strings_tab.addTab(make_table(imglist_headers, zone_names, True, scale=1), "Zone Names")
        strings_tab.addTab(make_table(imglist_headers+['JP address'], dialogue, scale=1), "Dialogue")

        layout = QHBoxLayout()
        layout.addWidget(self.tabwidget)
        self.main_widget = QWidget(self)
        self.main_widget.setLayout(layout)
        self.setCentralWidget(self.main_widget)
        self.show()


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
    max_height = 512  # I've seen up to 58 rows in EN, 36 in JP. Stay safe.
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
                "0x{:06X}".format(en), "0x{:0{}X}".format(id, id_digits),
                str_en, img_en, str_jp, img_jp, "0x{:06X}".format(jp_start)
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
            stringlist.append(["0x{:06X}".format(j1), "0x{:0{}X}".format(id, id_digits), str_en, img_en, str_jp, img_jp])
    return stringlist

def make_table(headers, items, sortable=False, row_labels=True, scale=2):
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
            lab.setPixmap(item.scaled(item.size() * scale))
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
