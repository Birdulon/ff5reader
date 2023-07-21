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
import os
from array import array
from struct import unpack
import includes.ff5.const as ff5const

pyqt_version = 0
skip_pyqt5 = "PYQT4" in os.environ

if not skip_pyqt5:
    try:
        from PyQt5 import QtGui, QtCore
        from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QTransform
        pyqt_version = 5
    except ImportError:
        print("Missing PyQt5, trying PyQt4...")
if pyqt_version == 0:
    try:
        from PyQt4 import QtGui, QtCore
        from PyQt4.QtGui import QImage, QPixmap, QColor, QPainter, QTransform
        pyqt_version = 4
    except ImportError:
        print("Missing PyQt4 dependencies")
        raise


bg_color = QColor(0, 0, 128)
bg_trans = QColor(0, 0, 0, 0)

def create_tile_indexed(data):
  '''
  Creates a QImage of a SNES tile. Useful for assigning palettes later.
  DO NOT USE OUTSIDE OF QApplication CONTEXT
  '''
  planes = len(data)//8
  tile = array('B', range(64))
  img = QImage(8, 8, QImage.Format_Indexed8)
  imgbits = img.bits()
  imgbits.setsize(img.byteCount())
  if planes == 0:
    raise ValueError("Empty bytes passed")
  if planes == 1:
    for i, (j, x) in enumerate([(j,x) for j in range(8) for x in reversed(range(8))]):
      tile[i] = (data[j] >> x & 1)
  else:
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
  return img

def create_tile_mode7_indexed(data):
  # Each byte is a pixel. 8bit palette.
  tile = array('B', range(64))
  tile = data[:64]
  img = QImage(8, 8, QImage.Format_Indexed8)
  imgbits = img.bits()
  imgbits.setsize(img.byteCount())
  imgbits[:64] = tile
  return img

def create_tile_mode7_compressed_indexed(data, pal_index):
  # Each byte is two pixels i.e. 0xEF is Mode 7 0xF 0xE
  # Palette is externally determined by LUT, to be padded to the first hex digit
  pal = pal_index << 4
  newdata = b''.join([bytes([pal|(j%16), pal|(j//16)]) for j in data])
  return create_tile_mode7_indexed(newdata)

def create_tile(data, palette=[0x00000080, 0xFFFFFFFF]):
  '''
  Creates a QPixmap of a SNES tile. DO NOT USE OUTSIDE OF QApplication CONTEXT
  '''
  img = create_tile_indexed(data)
  img.setColorTable(palette)
  return QPixmap.fromImage(img)

def create_tile_mode7(data, palette):
  # Each byte is a pixel. 8bit palette.
  img = create_tile_mode7_indexed(data)
  img.setColorTable(palette)
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
  img.setColorTable(ff5const.dialogue_palette)
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

def generate_glyphs(rom, offset, num=0x100, palette=ff5const.small_palette):
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

def make_pixmapfragment(id, target_col, target_row, tilesize=16):
  return QtGui.QPainter.PixmapFragment.create(QtCore.QPoint(target_col*tilesize, target_row*tilesize), QtCore.QRectF((id%16)*tilesize, (id//16)*tilesize, tilesize, tilesize))

def make_pixmapfragment2(source_x, source_y, target_x, target_y, tilesize=16):
  return QtGui.QPainter.PixmapFragment.create(QtCore.QPoint(target_x, target_y), QtCore.QRectF(source_x, source_y, tilesize, tilesize))

class Canvas:
  def __init__(self, cols, rows, color=bg_trans, tilesize=8):
    self.image = QImage(tilesize*cols, tilesize*rows, QImage.Format_ARGB32_Premultiplied)
    self.tilesize = tilesize
    self.image.fill(color)
    self.painter = QtGui.QPainter(self.image)
    self.max_col = 1
    self.max_row = 1
    self.batch = []

  def __del__(self):
    del self.painter

  def draw_pixmap(self, col, row, pixmap, h_flip=False, v_flip=False):
    h_s = -1 if h_flip else 1
    v_s = -1 if v_flip else 1
    x = (col+h_flip)*self.tilesize*h_s
    y = (row+v_flip)*self.tilesize*v_s
    self.painter.scale(h_s, v_s)
    self.painter.drawPixmap(x, y, pixmap)
    self.painter.scale(h_s, v_s)  # Invert it again to restore it to normal
    if col > self.max_col:
      self.max_col = col
    if row > self.max_row:
      self.max_row = row

  def drawPixmapFragments(self, *args, **kwargs):
    self.painter.drawPixmapFragments(*args, **kwargs)

  def add_pixmapfragment(self, fragment):
    self.batch.append(fragment)

  def do_batch(self, pixmap):
    self.painter.drawPixmapFragments(self.batch, pixmap)
    self.batch = []

  def pixmap(self, trim=False, rect=None):
    if trim:
      return QPixmap.fromImage(self.image.copy(0, 0, (self.max_col+1)*self.tilesize, (self.max_row+1)*self.tilesize))
    if rect:
      return QPixmap.fromImage(self.image.copy(*rect))
    return QPixmap.fromImage(self.image)


class Canvas_Indexed:
  def __init__(self, cols, rows, color=0, tilesize=8):
    self.image = QImage(tilesize*cols, tilesize*rows, QImage.Format_Indexed8)
    self.width = tilesize*cols
    self.tilesize = tilesize
    self.image.fill(0)
    self.imgbits = self.image.bits()
    self.imgbits.setsize(self.image.byteCount())
    self.max_col = 1
    self.max_row = 1

  def draw_tile(self, col, row, image, h_flip=False, v_flip=False, palette=0, bpp=4):
    image = image.mirrored(h_flip, v_flip)
    imgbits = image.bits()
    imgbits.setsize(image.byteCount())
    if palette:
      p = palette<<bpp
      imgbits[:] = bytes([int(i[0])|p for i in imgbits])
    x = col*self.tilesize
    y = row*self.tilesize
    start = x + y*self.width
    for i in range(self.tilesize):
      offset = i*self.width
      self.imgbits[start+offset:start+offset+self.tilesize] = imgbits[i*self.tilesize:(i+1)*self.tilesize]
    self.max_col = max(col, self.max_col)
    self.max_row = max(row, self.max_row)

  def pixmap(self, palette, trim=False):
    if isinstance(palette[0], list):
      palette = [i for p in palette for i in p]  # Flatten
    if trim:
      img = self.image.copy(0, 0, (self.max_col+1)*self.tilesize, (self.max_row+1)*self.tilesize)
      img.setColorTable(palette)
      return QPixmap.fromImage(img)
    self.image.setColorTable(palette)
    return QPixmap.fromImage(self.image)
