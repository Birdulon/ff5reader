from struct import unpack, pack
from .strings import Strings
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
