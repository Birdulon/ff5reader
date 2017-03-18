'''
No license for now
'''
import os
from array import array
from struct import unpack
import const

pyqt_version = 0
skip_pyqt5 = "PYQT4" in os.environ

if not skip_pyqt5:
    try:
        from PyQt5 import QtGui
        from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter
        pyqt_version = 5
    except ImportError:
        print("Missing PyQt5, trying PyQt4...")
if pyqt_version == 0:
    try:
        from PyQt4 import QtGui
        from PyQt4.QtGui import QImage, QPixmap, QColor, QPainter
        pyqt_version = 4
    except ImportError:
        print("Missing PyQt4 dependencies")
        raise


def create_tile(bytes, palette):
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
        for i, (j, x) in enumerate([(j,x) for j in range(8) for x in reversed(range(8))]):
            tile[i] = (bytes[j] >> x & 1)
    else:
        img.setColorTable(palette)
        for i, (j, x) in enumerate([(j,x) for j in range(0, 16, 2) for x in reversed(range(8))]):
            tile[i] = (bytes[j] >> x & 1) | ((bytes[j+1] >> x & 1) << 1)
        if planes == 3:
            for i, (j, x) in enumerate([(j,x) for j in range(16, 24, 1) for x in reversed(range(8))]):
                tile[i] |= ((bytes[j] >> x & 1) << 2)
        elif planes >= 4:
            for i, (j, x) in enumerate([(j,x) for j in range(16, 32, 2) for x in reversed(range(8))]):
                tile[i] |= ((bytes[j] >> x & 1) << 2) | ((bytes[j+1] >> x & 1) << 3)
        if planes == 8:
            for i, (j, x) in enumerate([(j,x) for j in range(32, 48, 2) for x in reversed(range(8))]):
                tile[i] |= ((bytes[j] >> x & 1) << 4) | ((bytes[j+1] >> x & 1) << 5) \
                    | ((bytes[j+16] >> x & 1) << 6) | ((bytes[j+17] >> x & 1) << 7)
    imgbits[:64] = tile
    return QPixmap.fromImage(img)

def create_tile_old(bytes, palette):
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
        img.setColorTable(palette)
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
    img.setColorTable(const.dialogue_palette)
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

def generate_glyphs(rom, offset, num=0x100, palette=const.small_palette):
    spritelist = []
    for i in range(num):
        j = offset + (i*16)
        spritelist.append(create_tile(rom[j:j+16], palette))
    return spritelist

def generate_glyphs_large(rom, offset, num=0x100):
    spritelist = []
    for i in range(num):
        j = offset + (i*24)
        spritelist.append(create_tritile(rom[j:j+24]))
    return spritelist

def generate_palette(rom, offset, length=16):
    # Need to convert BGR555 to ARGB32
    palette = []
    for i in range(offset, offset+length, 2):
        if (i+2) < len(rom):
            short = unpack('<H', rom[i:i+2])[0]
            b = (short & 0x7C00) >>  7  # b 0XXXXX00 00000000 -> 00000000 00000000 XXXXX000
            g = (short & 0x03E0) <<  6  # b 000000XX XXX00000 -> 00000000 XXXXX000 00000000
            r = (short & 0x001F) << 19  # b 00000000 000XXXXX -> XXXXX000 00000000 00000000
            color = 0xFF000000|r|g|b
        else:
            color = 0  # Transparent
        palette.append(color)
    return palette
