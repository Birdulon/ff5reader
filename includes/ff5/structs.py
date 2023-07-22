from . import const, strings
from ..helpers import hex, parse_struct


class StructBlock:
	structure = None
	block_start = 0
	block_length = 0
	block_count = 0

	@classmethod
	def get_data(cls, rom: bytes):
		start = cls.block_start
		step = cls.block_length
		end = start + (step * cls.block_count)
		return [parse_struct(rom, address, cls.structure) for address in range(start, end, step)]

	@classmethod
	def get_headers(cls):
		return ['Address'] + [z[0] for z in cls.structure]

class BattleBackground(StructBlock):
	structure = (
		('Tileset',     1, None),
		('Palette 1',   1, None),
		('Palette 2',   1, None),
		('Tilemap',     1, None),
		('TilemapFlip', 1, None),
		(hex(5, 1),     1, None),
		('Animation',   1, None),
		('PaletteCycle',1, None),
	)
	block_start = 0x14BA21
	block_length = 8
	block_count = 34


class EnemySprite(StructBlock):
	structure = (
		('Sprite data offset', 2, None),
		('Multiple things',    2, None),
		('Tile Layout ID',     1, None),
	)
	headers = ['Address']+[i[0] for i in structure]
	block_start = 0x14B180
	block_length = 5
	block_count = 0x180


class ZoneData(StructBlock):
	def split_tilesets(data):
		tilesets = [
			(data & 0x00003F),        # 0b00000000_00000000_00111111
			(data & 0x000FC0) >> 6,   # 0b00000000_00001111_11000000
			(data & 0x03F000) >> 12,  # 0b00000011_11110000_00000000
			(data & 0xFC0000) >> 18,  # 0b11111100_00000000_00000000
		]
		return ' '.join([hex(i,2) for i in tilesets])

	def split_blockmaps(data):
		blockmaps = [
			( data & 0x000003FF) - 1,         # 0b00000000_00000000_00000011_11111111
			((data & 0x000FFC00) >> 10) - 1,  # 0b00000000_00001111_11111100_00000000
			((data & 0x3FF00000) >> 20) - 1,  # 0b00111111_11110000_00000000_00000000
		]
		return ' '.join([hex(i,3) for i in blockmaps])

	structure = (
		('NPC Layer',      2, None),  # 00 01
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
		('Music',          1, const.BGM_Tracks),  # 19
	)
	block_start = 0x0E9C00
	block_length = 0x1A
	block_count = const.zone_count
