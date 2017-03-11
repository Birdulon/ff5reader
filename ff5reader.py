#!python3 -i
'''
No license for now
'''

import sys
import os
import struct
from array import array

pyqt_version = 0
skip_pyqt5 = True  # "PYQT4" in os.environ

if not skip_pyqt5:
    try:
        from PyQt5 import QtGui, QtCore
        from PyQt5.QtGui import QIcon, QPalette, QColor
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
            QValidator
        )
        from PyQt4.QtGui import QStyleOptionProgressBarV2 as QStyleOptionProgressBar
        pyqt_version = 4
    except ImportError:
        print("Couldn't import Qt dependencies. "
              "Make sure you installed the PyQt4 package.")
        sys.exit(-1)


def divceil(numerator, denominator):
    # Reverse floor division for ceil
    return -(-numerator // denominator)

def hex_length(i):
    return divceil(i.bit_length(), 4)

filename = "Final Fantasy V (Japan) [En by RPGe v1.1].sfc"
with open(filename, 'rb') as file1:
    ROM = file1.read()
print(len(ROM))

Glyphs = [' ',' ',' ',' ',    ' ',' ',' ',' ',    ' ',' ',' ',' ',    ' ',' ',' ',' ',      # 0x00
          ' ',' ',' ',' ',    ' ',' ',' ',' ',    ' ',' ',' ',' ',    ' ',' ',' ',' ',       # 0x10
          'A','B','C','D',    'E','F','G','H',    'I','J','K','L',    'M','N','O','P',      # 0x20
          'Q','R','S','T',    'U','V','W','X',    'Y','Z','a','b',    'c','d','e','f',      # 0x30
          'g','h','i','j',    'k','l','m','n',    'o','A','B','C',    'D','E','F','G',      # 0x40
          'H','I','J','0',    '1','2','3','4',    '5','6','7','8',    '9','_m','_H','_P',   # 0x50
          'A','B','C','D',    'E','F','G','H',    'I','J','K','L',    'M','N','O','P',      # 0x60
          'Q','R','S','T',    'U','V','W','X',    'Y','Z','a','b',    'c','d','e','f',      # 0x70
          'g','h','i','j',    'k','l','m','n',    'o','p','q','r',    's','t','u','v',      # 0x80
          'w','x','y','z',    'il','it','','li',  'll','\'','"',':',   ';',',','(',')',     # 0x90
          '/','!','?','0',    'ti','fi','Bl','a', 'pe','l','\'','"',   'if','lt','tl','ir', # 0xA0
          'tt','や','ユ','ゆ', 'ヨ', 'よ', 'ワ', 'わ', 'ン', 'ん', 'ヲ','を', '[key]', '[shoe]', '[diamond?]', '[hammer]',  # 0xB0
          '[tent]', '[ribbon]', '[potion]', '[shirt]', '[song]', '-', '[shuriken]', '・・', '[scroll]', '!', '[claw]', '?', '[glove]', 'pickaxe head??', '/', ':',    # 0xC0
          '「', '」', '0', 'A', 'B', 'X', 'Y', 'L', 'R', 'E', 'H', 'M', 'P', 'S', 'C', 'T',    # 0xD0
          ' ', ' ', '+', '[sword]', '[wh.mag]', '[blk.mag]', '[t.mag]', '[knife]', '[spear]', '[axe]', '[katana]', '[rod]', '[staff]', '[bow]', '[harp]', '[whip]',   # 0xE0
          '[bell]', '[shield]', '[helmet]', '[armor]', '[ring]', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']    # F0

BGM_Tracks = ["Ahead on our way", "The Fierce Battle", "A Presentiment", "Go Go Boko!",
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
              "A New Origin", "Chirping sound"]

def MakeStringList(start, end, length):
    stringlist = []
    id = 0
    ids = (end-start)//length
    id_digits = hex_length(ids-1)
    for i in range(start, end, length):
        stringROM = ROM[i:i+length]
        string = ""
        for j in stringROM:
            string = string + Glyphs[j]
        stringlist.append(("0x{:06X}".format(i), "0x{0:0{1}X}".format(id, id_digits), string))
        id += 1
    return stringlist

items = MakeStringList(0x111380, 0x111C80, 9)
magics = MakeStringList(0x111C80, 0x111E8A, 6)
more_magics = MakeStringList(0x111E8A, 0x11211B, 9)
enemy_names = MakeStringList(0x200050, 0x200F50, 10)
stringlist_headers = ["Address", "ID", "Name"]

zone_names_count = 0x100
zone_names = []
zone_names_full = []
for id in range(zone_names_count):
    i = 0x107000 + (id*2)
    string = ""
    offset = 0x270000
    start = int.from_bytes(ROM[i:i+2],'little') + offset
    next = int.from_bytes(ROM[i+2:i+4],'little') + offset
    if next == offset:
        break
    stringROM = ROM[start:next]
    for j in stringROM:
        string = string + Glyphs[j]
    zone_names.append(string)
    zone_names_full.append("0x{:06X}->0x{:06X}: Zone Name 0x{:02X} - {name}".format(i, start, id, name=string))

zone_count = 0x200
zone_data = []
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
for i in range(zone_count):
    zone_data.append([])
    offset = 0x0E9C00 + (i*0x1A)
    zone_data[-1].append("0x{:06X}".format(offset))
    j = 0
    for z in zone_structure:
        val = int.from_bytes(ROM[offset+j:offset+j+z[1]],'little')
        if z[2] and val < len(z[2]):
            zone_data[-1].append(z[2][val])
        else:
            zone_data[-1].append("0x{0:0{1}X}".format(val, z[1]*2))
        j += z[1]


npc_layer_count = 0x200
npc_layers = []
npc_layer_structure = [("Dialogue/trigger ID", 1, None),
                       ("0x01", 1, None),
                       ("Sprite ID", 1, None),
                       ("X", 1, None),
                       ("Y", 1, None),
                       ("Move Pattern", 1, None),
                       ("Palette", 1, None)]
npc_layer_headers = ["Address", "Layer"] + [x[0] for x in npc_layer_structure]
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


def MakeTable(headers, items, sortable=False, row_labels=True):
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
        table.setItem(row, col, QTableWidgetItem(item))
    table.resizeColumnsToContents()
    if sortable:
        table.setSortingEnabled(True)
        table.sortItems(0)
    return table


class FF5Reader(QMainWindow):
    """
    Main GUI class
    """
    def __init__(self):
        QMainWindow.__init__(self, None)

        self.tabwidget = QTabWidget()
        self.enemy_sprites = QFrame()
        self.tabwidget.addTab(self.enemy_sprites, "Enemy Sprites")
        self.tabwidget.addTab(MakeTable(zone_headers, zone_data, True), "Zones")
        self.tabwidget.addTab(MakeTable(npc_layer_headers, npc_layers, True), "NPC Layers")
        self.tabwidget.addTab(MakeTable(stringlist_headers, items, row_labels=False), "Items")
        self.tabwidget.addTab(MakeTable(stringlist_headers, magics, row_labels=False), "Magics")
        self.tabwidget.addTab(MakeTable(stringlist_headers, more_magics, row_labels=False), "More Magics")
        self.tabwidget.addTab(MakeTable(stringlist_headers, enemy_names, row_labels=False), "Enemy Names")

        layout = QHBoxLayout()
        layout.addWidget(self.tabwidget)
        self.main_widget = QWidget(self)
        self.main_widget.setLayout(layout)
        self.setCentralWidget(self.main_widget)
        self.show()



def main():
    app = QApplication(sys.argv)

    mainwindow = FF5Reader()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
