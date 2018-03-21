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


def create_tile(data, palette):
  '''
  Creates a QPixmap of a SNES tile. DO NOT USE OUTSIDE OF QApplication CONTEXT
  '''
  planes = len(data)//8
  tile = array('B', range(64))
  img = QImage(8, 8, QImage.Format_Indexed8)
  imgbits = img.bits()
  imgbits.setsize(img.byteCount())
  if planes == 0:
    raise ValueError("Empty bytes passed")
  if planes == 1:
    img.setColorTable([0x00000080, 0xFFFFFFFF])
    for i, (j, x) in enumerate([(j,x) for j in range(8) for x in reversed(range(8))]):
      tile[i] = (data[j] >> x & 1)
  else:
    img.setColorTable(palette)
    for i, (j, x) in enumerate([(j,x) for j in range(0, 16, 2) for x in reversed(range(8))]):
      tile[i] = (data[j] >> x & 1) | ((data[j+1] >> x & 1) << 1)
    if planes == 3:
      for i, (j, x) in enumerate([(j,x) for j in range(16, 24, 1) for x in reversed(range(8))]):
        tile[i] |= ((data[j] >> x & 1) << 2)
    elif planes >= 4:
      for i, (j, x) in enumerate([(j,x) for j in range(16, 32, 2) for x in reversed(range(8))]):
        tile[i] |= ((data[j] >> x & 1) << 2) | ((data[j+1] >> x & 1) << 3)
    if planes == 8:
      for i, (j, x) in enumerate([(j,x) for j in range(32, 48, 2) for x in reversed(range(8))]):
        tile[i] |= ((data[j] >> x & 1) << 4) | ((data[j+1] >> x & 1) << 5) \
            | ((data[j+16] >> x & 1) << 6) | ((data[j+17] >> x & 1) << 7)
  imgbits[:64] = tile
  return QPixmap.fromImage(img)

def create_tile_mode7(data, palette):
  # Each byte is a pixel. 8bit palette.
  tile = array('B', range(64))
  tile = data[:64]
  img = QImage(8, 8, QImage.Format_Indexed8)
  img.setColorTable(palette)
  imgbits = img.bits()
  imgbits.setsize(img.byteCount())
  imgbits[:64] = tile
  return QPixmap.fromImage(img)

def create_tile_mode7_compressed(data, palette):
  # Each byte is two pixels i.e. 0xEF is Mode 7 0xF 0xE
  # Palette is externally determined by LUT, only send 4bit palette
  newdata = b''.join([bytes([j%16, j//16]) for j in data])
  return create_tile_mode7(newdata, palette)

def create_tile_old(data, palette):
    '''
    Creates a QPixmap of a SNES tile. DO NOT USE OUTSIDE OF QApplication CONTEXT
    '''
    planes = len(data)//8
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
            tile[t_ptr] = (data[j] >> x & 1)
            t_ptr += 1
    else:
        img.setColorTable(palette)
        t_ptr = 0
        for j, x in [(j,x) for j in range(0, 16, 2) for x in reversed(range(8))]:
            tile[t_ptr] = (data[j] >> x & 1) | ((data[j+1] >> x & 1) << 1)
            t_ptr += 1
        t_ptr = 0
        if planes == 3:
            for j, x in [(j,x) for j in range(16, 24, 1) for x in reversed(range(8))]:
                tile[t_ptr] |= ((data[j] >> x & 1) << 2)
                t_ptr += 1
        elif planes >= 4:
            for j, x in [(j,x) for j in range(16, 32, 2) for x in reversed(range(8))]:
                tile[t_ptr] |= ((data[j] >> x & 1) << 2) | ((data[j+1] >> x & 1) << 3)
                t_ptr += 1
        if planes == 8:
            t_ptr = 0
            for j, x in [(j,x) for j in range(32, 48, 2) for x in reversed(range(8))]:
                tile[t_ptr] |= ((data[j] >> x & 1) << 4) | ((data[j+1] >> x & 1) << 5) \
                    | ((data[j+16] >> x & 1) << 6) | ((data[j+17] >> x & 1) << 7)
                t_ptr += 1
    imgbits[:64] = tile
    return QPixmap.fromImage(img)

def create_tritile(data):
  img = QImage(16, 12, QImage.Format_Indexed8)
  imgbits = img.bits()
  imgbits.setsize(img.byteCount())
  img.setColorTable(const.dialogue_palette)
  tile = array('B', range(192))
  for p, row, b in [(p,j,b) for p in range(2) for j in range(12) for b in reversed(range(8))]:
    tile[(7-b) + (row*16) + (p*8)] = (data[row + (p*12)] >> b & 1)
  imgbits[:192] = tile
  return QPixmap.fromImage(img)

def create_quadtile(data, ltr=False):
  img = QImage(16, 16, QImage.Format_ARGB32_Premultiplied)
  img.fill(QColor(0,0,0,0))
  painter = QtGui.QPainter(img)
  painter.drawPixmap(0, 0, create_tile(data[0:8]))
  painter.drawPixmap(8, 8, create_tile(data[24:32]))
  if ltr:
    painter.drawPixmap(8, 0, create_tile(data[8:16]))
    painter.drawPixmap(0, 8, create_tile(data[16:24]))
  else:
    painter.drawPixmap(0, 8, create_tile(data[8:16]))
    painter.drawPixmap(8, 0, create_tile(data[16:24]))
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

def generate_palette(rom, offset, length=32, transparent=False):
  '''
  Length is in bytes not colors (2 bytes per color)
  We need to convert BGR555 to ARGB32 for each 2 bytes
  '''
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
  if transparent:
    palette[0] = 0
  return palette
