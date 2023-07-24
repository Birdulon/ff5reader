from struct import unpack, pack
from .strings import Strings
from collections import namedtuple
# Menu Draw Info from LightPhoenix
# 00 () - End of Function
# 01 (u8 Font, u8 Color) - Fill Current Layer
# 02 (u8 Font, u8 Color, u8 X, u8 Y, u8 Width, u8 Height) - Draw Fill Box (fills entirely with font tile)
# 03 (u8 Font, u8 Color, u8 X, u8 Y, u8 Width, u8 Height) - Draw Static Box (font tile is used for top row middle only)
# 04 (u8 String, u8 Color?, u8 X, u8 Y, u8 NULL) - Draw Text
# 05 (u16 Layer) - Change Layer - this can result in weird offsets due to memory placement if used inappropriately
# 06 (u8 Font, u8 Color, u8 X, u8 Y, u8 Width, u8 Height) - Draw Indent Box (font tile is used for top row middle only)

START_OF_MENUS = 0x03AD3F

MENU_STRINGS = Strings.blocks_SNES_RPGe['menu_strings']

def disassemble(rom: bytes, start_address: int = 0):
	i = start_address
	end = len(rom)
	while i < end:
		instruction_id = rom[i]
		i += 1
		match instruction_id:
			case 0:
				print(f'${i-1:06x} - End of Function (0)')
				return i
			case 1:
				font, color = unpack('<BB', rom[i:i+2])
				print(f'${i-1:06x} - Fill Current Layer (font = #{font:02x}, color = #{color:02x})')
				i += 2
			case 2:
				font, color, x, y, w, h = unpack('<BBBBBB', rom[i:i+6])
				print(f'${i-1:06x} - Draw Fill Box   (font = #{font:02x}, color = #{color:02x}, x = #{x:02x}, y = #{y:02x}, width = #{w:02x}, height = #{h:02x})')
				i += 6
			case 3:
				font, color, x, y, w, h = unpack('<BBBBBB', rom[i:i+6])
				print(f'${i-1:06x} - Draw Static Box (font = #{font:02x}, color = #{color:02x}, x = #{x:02x}, y = #{y:02x}, width = #{w:02x}, height = #{h:02x})')
				i += 6
			case 4:
				string, color, x, y, null = unpack('<BBBBB', rom[i:i+5])
				print(f'${i-1:06x} - Draw Text  (string_id = #{string:02x}, color = #{color:02x}, x = #{x:02x}, y = #{y:02x}, null = #{null:02x})')
				print(MENU_STRINGS[0].decoded[string])
				print(MENU_STRINGS[1].decoded[string])
				i += 5
			case 5:
				layer, = unpack('<H', rom[i:i+2])
				print(f'${i-1:06x} - Switch Layer (layer = #{layer:04x})')
				i += 2
			case 6:
				font, color, x, y, w, h = unpack('<BBBBBB', rom[i:i+6])
				print(f'${i-1:06x} - Draw Indent Box (font = #{font:02x}, color = #{color:02x}, x = #{x:02x}, y = #{y:02x}, width = #{w:02x}, height = #{h:02x})')
				i += 6
			case other:
				print(f'${i-1:06x} - Invalid command: {other:02x}')
				raise ValueError(f"Invalid command ({other}), this probably wasn't a menu")


def disassemble_until_fail(rom: bytes, start_address: int = START_OF_MENUS):
	i = start_address
	end = len(rom)
	try:
		while i < end:
			print('====================New Menu Function====================')
			potential_hit = rom.find(pack('<H', i & 0xFFFF))
			if potential_hit < 0:
				print('=================No potential offset hits================')
			else:
				print(f'=============Potential offset hit at ${potential_hit:06x}=============')
			i = disassemble(rom, i)
	except ValueError:
		print('Finished dense scan')


def decode_bgs(rom: bytes, start_address: int) -> list[int]:
	# scanlines is a list of scanlines at which to scroll up 4px, effectively skipping 4 pixel rows
	# this is used to make half-tile rows
	scanlines = []
	i = start_address
	end = len(rom)
	while (i < end) and (value := rom[i]) != 0:
		scanlines.append(value)
	scanlines.pop()  # Last value before terminator appears to do nothing in known programs
	return scanlines

CursorData = namedtuple('CursorData', 'param1 param2 x y idx_up idx_down idx_left idx_right')
def decode_cursor(rom: bytes, start_address: int):
	length = int.from_bytes(rom[start_address:start_address+2], 'little')
	cursors = []
	for i in range(start_address+2, start_address+2+length, 8):
		data = CursorData._make(unpack('<8B', rom[i:i+8]))
		cursors.append(data)
	return cursors

CURSORS = [0x03A300, 0x03A382, 0x03A434, 0x03A4EE, 0x03A598, 0x03A5A2, 0x03A73C, 0x03A856, 0x03AA38, 0x03AA26, 0x03A978, 0x03A9AA, 0x03A9E4]


MenuTable = namedtuple('MenuTable', 'BG1 BG2 BG3 BG4 BGS1 BGS2 BGS3 BGS4 mask1 mask2 cursor_data settings')
def get_menu_table(rom: bytes, id=None, lut_address: int = 0x00F5E7, start_address: int = 0):
	if id is not None:
		start_address = int.from_bytes(rom[lut_address+(id*2):lut_address+((id+1)*2)], 'little')
	return MenuTable._make(unpack('<12H', rom[start_address:start_address+24]))

def get_all_menu_tables(rom: bytes):
	return [get_menu_table(rom, id=i) for i in range(13)]


def execute(rom: bytes, menu_start_addresses: list[int], squish_start_addresses: list[int] = None):
	# color is always 0 in known menus, so don't bother implementing it yet
	# +x is right, +y is down
	layers = {0x4000: None, 0x5000: None, 0x6000: None}  # 0x3000: BG1, 0x4000: BG2, 0x5000: BG3, 0x6000: BG4
	# BG1 is not used by menus
	end = len(rom)
	for layer_id, program_start_address in enumerate(menu_start_addresses):
		if program_start_address is None:
			continue
		i = program_start_address
		layer = (0x3000, 0x4000, 0x5000, 0x6000)[layer_id]
		while i < end:
			instruction_id = rom[i]
			i += 1
			match instruction_id:
				case 0:
					# print(f'${i-1:06x} - End of Function (0)')
					return i
				case 1:
					font, color = unpack('<BB', rom[i:i+2])
					# print(f'${i-1:06x} - Fill Current Layer (font = #{font:02x}, color = #{color:02x})')
					i += 2
				case 2:
					font, color, x, y, w, h = unpack('<BBBBBB', rom[i:i+6])
					# print(f'${i-1:06x} - Draw Fill Box   (font = #{font:02x}, color = #{color:02x}, x = #{x:02x}, y = #{y:02x}, width = #{w:02x}, height = #{h:02x})')
					# Fill entire box with font glyph
					i += 6
				case 3:
					font, color, x, y, w, h = unpack('<BBBBBB', rom[i:i+6])
					# print(f'${i-1:06x} - Draw Static Box (font = #{font:02x}, color = #{color:02x}, x = #{x:02x}, y = #{y:02x}, width = #{w:02x}, height = #{h:02x})')
					# font glyph is middle fill tile of top border. Top corners are either side of it.
					# box will use #04 and #5 for sides, #06, #07, #08 for bottom border, and probably #FF for fill.
					i += 6
				case 4:
					string, color, x, y, null = unpack('<BBBBB', rom[i:i+5])
					# print(f'${i-1:06x} - Draw Text  (string_id = #{string:02x}, color = #{color:02x}, x = #{x:02x}, y = #{y:02x}, null = #{null:02x})')
					i += 5
				case 5:
					layer = unpack('<H', rom[i:i+2])
					# print(f'${i-1:06x} - Switch Layer (layer = #{layer:04x})')
					i += 2
				case 6:
					font, color, x, y, w, h = unpack('<BBBBBB', rom[i:i+6])
					# print(f'${i-1:06x} - Draw Indent Box (font = #{font:02x}, color = #{color:02x}, x = #{x:02x}, y = #{y:02x}, width = #{w:02x}, height = #{h:02x})')
					# font glyph is middle fill tile of top border. Top corners are either side of it.
					# box will use #04 and #5 for sides, #06, #07, #08 for bottom border, and probably #FF for fill.
					i += 6
				case other:
					print(f'${i-1:06x} - Invalid command: {other:02x}')
					raise ValueError(f"Invalid command ({other}), this probably wasn't a menu")
	if squish_start_addresses:
		for layer_id, program_start_address in enumerate(squish_start_addresses):
			i = program_start_address
			scanlines = []
			while i < end:
				value = rom[i]
				if value == 0:
					break
				scanlines.append(value)
			scanlines.pop()  # Last value before terminator appears to do nothing in known programs
			# Now squish the drawn layer
