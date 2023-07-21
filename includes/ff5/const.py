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
from ..helpers import load_table
from pathlib import Path

dir = Path(__file__).parent
# print(dir)


# Font palettes (probably move these later)
small_palette = [0xFF000000, 0x00000080, 0xFF808080, 0xFFFFFFFF]
dialogue_palette = [0xFF000080, 0xFFFFFFFF]
mono_palette = [0xFF000000, 0xFFFFFFFF]


BGM_Tracks = load_table(dir/'BGM_Titles.txt')
BGM_Tracks_Safe = [t.replace('/', '-') for t in BGM_Tracks]  # For saving files


npc_layer_count = 0x200
npc_layer_structure = [
	("Dialogue/trigger ID", 1, None),
	("0x01", 1, None),
	("Sprite ID", 1, None),
	("X", 1, None),
	("Y", 1, None),
	("Move Pattern", 1, None),
	("Palette", 1, None)
	]
npc_layer_headers = ["Ptr Address", "Layer", "Data Address"] + [x[0] for x in npc_layer_structure]


zone_count = 0x200
