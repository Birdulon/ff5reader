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

import sys, os
from includes.helpers import *

pyqt_version = 0
skip_pyqt5 = 'PYQT4' in os.environ

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


monofont = QFont()
monofont.setStyleHint(QFont.Monospace)
if not monofont.fixedPitch():
    monofont.setStyleHint(QFont.TypeWriter)
if not monofont.fixedPitch():
    monofont.setFamily('Monospace')


class Label(QLabel):
  def __init__(self, *kwargs):
    super().__init__(*kwargs)
    self.pixmaps = []
    self.pixmap_index = 0
    self.timer = QtCore.QTimer()
    self.timer.timeout.connect(self._cycle_pixmap)

  def setContent(self, content, scale=1, strip=True):
    if isinstance(content, QPixmap):
      self.setPixmap(content.scaled(content.size() * scale))
    elif isinstance(content, list) and isinstance(content[0], QPixmap):
      self.pixmaps = [c.scaled(c.size() * scale) for c in content[:-1]]
      self.setPixmap(self.pixmaps[0])
      self.timer.start(content[-1]*1000/60)
    else:
      if strip:
        content = content.strip()
      self.setText(content)

  def _cycle_pixmap(self):
    self.pixmap_index = (self.pixmap_index+1)%len(self.pixmaps)
    self.setPixmap(self.pixmaps[self.pixmap_index])


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


def make_pixmap_table(items, cols=16, scale=4, large=False):
  rows = divceil(len(items), cols)
  rd = hex_length(rows-1)+1
  cd = hex_length(cols-1)
  table = QTableWidget(rows, cols)
  if large:
    table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
    table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
  table.setVerticalHeaderLabels([hex(v*cols, rd) for v in range(rows)])
  table.setHorizontalHeaderLabels([hex(v, cd) for v in range(cols)])
  for i, item in enumerate(items):
    if isinstance(item, QWidget):
      table.setCellWidget(i // cols, i % cols, item)
    else:
      lab = Label()
      lab.setContent(item, scale=scale)
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
    lab = Label()
    lab.setContent(item)
    lab.setAlignment(QtCore.Qt.AlignCenter)
    lab.setMargin(0)
    l.addWidget(lab)
  w.setLayout(l)
  return w
