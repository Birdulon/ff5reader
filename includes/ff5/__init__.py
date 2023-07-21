from . import const, files, strings
from ..helpers import hex, parse_struct

class ZoneData:
	def split_tilesets(data):
		tilesets = [(data & 0x00003F),
		            (data & 0x000FC0) >> 6,
		            (data & 0x03F000) >> 12,
		            (data & 0xFC0000) >> 18]
		return ' '.join([hex(i,2) for i in tilesets])

	def split_blockmaps(data):
		blockmaps = [(data & 0x000003FF) - 1,
		            ((data & 0x000FFC00) >> 10) - 1,
		            ((data & 0x3FF00000) >> 20) - 1]
		return ' '.join([hex(i,3) for i in blockmaps])

	zone_structure = [('NPC Layer',      2, None),  # 00 01
	                  ('Name',           1, strings.Strings.blocks_RPGe['zone_names'].decoded),  # 02
	                  ('ShadowFlags',    1, None),  # 03
	                  ('Graphic maths',  1, None),  # 04  - MSb animation-related, 6 LSbs are ID for table in 0x005BB8 which writes to $2131-$2133 (Color Math Designation, Subscreen BG color)
	                  ('Tile properties',1, None),  # 05
	                  ('Flags '+hex(6),  1, None),  # 06
	                  (hex(7),           1, None),  # 07
	                  ('Blockset',       1, None),  # 08
	                  ('Tilesets',       3, split_tilesets),  # 09 0A 0B
	                  ('Blockmaps',      4, split_blockmaps),  # 0C 0D 0E 0F
	                  (hex(16),          1, None),  # 10
	                  (hex(17),          1, None),  # 11
	                  (hex(18),          1, None),  # 12
	                  (hex(19),          1, None),  # 13
	                  (hex(20),          1, None),  # 14
	                  (hex(21),          1, None),  # 15
	                  ('Palette',        1, None),  # 16
	                  (hex(23),          1, None),  # 17
	                  (hex(24),          1, None),  # 18
	                  ('Music',          1, const.BGM_Tracks)]  # 19
	zone_headers = ['Address'] + [z[0] for z in zone_structure]

	@classmethod
	def get_data(cls):
		return [parse_struct(files.ROM_RPGe, 0x0E9C00 + (i*0x1A), cls.zone_structure) for i in range(const.zone_count)]
