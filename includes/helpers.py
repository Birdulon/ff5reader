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
from ast import literal_eval

HEX_PREFIX = '#'  # '#' '$' or '0x' are also nice


def divceil(numerator: int, denominator: int) -> int:
	'''
	Reverse floor division for fast ceil
	'''
	return -(-numerator // denominator)


def hex_length(i: int) -> int:
	'''
	String length of hexadecimal representation of integer
	'''
	return divceil(i.bit_length(), 4)


def hex(num: int, digits: int = 2) -> str:
	'''
	Consolidate hex formatting for consistency
	'''
	#return '{:0{}X}₁₆'.format(num, digits)
	return HEX_PREFIX + '{:0{}X}'.format(num, digits)


def indirect(rom: bytes, start: int, length: int = 2, endian: str = 'little') -> int:
	'''
	Read little-endian value at start address in rom
	'''
	return int.from_bytes(rom[start:start+length], endian)

def indirect2(rom: bytes, slice, endian: str = 'little') -> int:
	return int.from_bytes(rom[slice], endian)

def memory_address_to_rom_address(address: int) -> int:
	# SNES memory space in HiROM Mode:
	# 0xC00000 to 0xFDFFFF are a view of the ROM, i.e. banks $C0 to $FD.
	# Banks $80-$BF mirror banks $00-3F, which have a partial view to the ROM.
	# We don't care about potential RAM addresses at low offsets,
	# so let's just pretend $00-$3F, $40-$7F, $80-$BF and $C0-$FF all map to $00-$3F of the ROM
	return address & 0x3FFFFF


def get_slices(start_address: int, each_length: int, num_strings: int) -> list:
	return [slice(start_address+(each_length*id), start_address+(each_length*(id+1))) for id in range(num_strings)]


def get_contiguous_address_slices(rom: bytes, slices, indirect_offset: int = 0) -> list:
	pointers = [indirect2(rom, s) + indirect_offset for s in slices]
	output = []
	for ptr, ptr_next in zip(pointers[:-1], pointers[1:]):
		if ptr_next < ptr:
			break
		start = memory_address_to_rom_address(ptr)
		end = memory_address_to_rom_address(ptr_next)
		output.append(slice(start, end))
	return output


def get_null_terminated_address_slices(rom: bytes, slices, indirect_offset: int = 0) -> list:
	pointers = [indirect2(rom, s) + indirect_offset for s in slices]
	output = []
	for ptr in pointers:
		start = memory_address_to_rom_address(ptr)
		end = start
		while rom[end] > 0:
			end += 1
		output.append(slice(start, end))
	return output


def get_bytestring_slices(rom: bytes, start_address: int, each_length: int, num_strings: int, indirect_offset=None, indirect_null_terminated=False) -> list:
	if indirect_offset is not None:
		if not indirect_null_terminated:
			pointers = [indirect(rom, address, each_length) + indirect_offset for address in range(start_address, start_address + (each_length * num_strings), each_length)]
			output = []
			for ptr, ptr_next in zip(pointers[:-1], pointers[1:]):
				if ptr_next < ptr:
					break
				start = memory_address_to_rom_address(ptr)
				end = memory_address_to_rom_address(ptr_next)
				output.append(slice(start, end))
			return output
		else:
			def get_indirect(address: int) -> bytes:
				ptr = memory_address_to_rom_address(indirect(rom, address, each_length) + indirect_offset)
				# While previously we used the start address of the next string, this is not necessarily correct.
				# Scan for a zero-byte end-of-string marker and pay the extra cycles.
				end_ptr = ptr
				# print(ptr)
				while rom[end_ptr] > 0:
					end_ptr += 1
				return slice(ptr, end_ptr)
			return [get_indirect(start_address+(each_length*id)) for id in range(num_strings)]
	else:
		return [slice(start_address+(each_length*id), start_address+(each_length*(id+1))) for id in range(num_strings)]


def get_bytestrings(rom: bytes, start_address: int, each_length: int, num_strings: int, indirect_offset=None, indirect_null_terminated=False) -> list[bytes]:
	return [rom[s] for s in get_bytestring_slices(rom, start_address, each_length, num_strings, indirect_offset, indirect_null_terminated)]


def load_table(filename: str) -> tuple[str]:
	with open(filename, 'r') as f:
		return tuple(literal_eval(f'"{line}"') if line.startswith('\\') else line for line in f.read().rstrip('\n').split('\n'))

def __cast_string_to_object(input: str) -> object:
	if len(input) == 0:
		return None
	try:
		return literal_eval(input)
	except:
		return input  # Unescaped string

def load_tsv(filename: str) -> dict[dict[str, str]]:
	with open(filename, 'r') as f:
		header, *lines = f.read().rstrip('\n').split('\n')
	first_column_name, *headers = header.split('\t')
	# Cheeky Py3.8 one-liner
	# return {(s := line.split('\t'))[0]:dict(zip(headers, s[1:])) for line in lines}
	output = {}
	for line in lines:
		name, *values = line.split('\t')
		output[name] = dict((h,__cast_string_to_object(v)) for h,v in zip(headers, values) if len(v) > 0)
	return output


def load_raw(filename: str) -> bytes:
	with open(filename, 'rb') as f:
		return f.read()


def parse_struct(rom: int, offset: int, structure: list[tuple[str, int, object]]):
	'''
	Read in a section of rom with a given structure, output a list
	'''
	out = [hex(offset, 6)]
	j = 0
	for title, length, handler in structure:
		val = indirect(rom, offset+j, length=length)
		if callable(handler):
			out.append(handler(val))
		elif handler and val < len(handler):
			out.append(handler[val])
		else:
			out.append(hex(val, length*2))
		j += length
	return out


def decompress_lzss(rom: bytes, start: int, header: bool = False, length=None) -> bytes:
	'''
	Algorithm from http://slickproductions.org/slickwiki/index.php/Noisecross:Final_Fantasy_V_Compression
	'''
	ptr = start
	if length:
		uncompressed_length = length
	else:
		uncompressed_length = indirect(rom, start)
		ptr += 2
	output = []
	buffer = [0 for i in range(0x800)]
	buffer_p = 0x07DE
	while len(output) < uncompressed_length:
		bitmap_byte = rom[ptr]
		ptr += 1
		for i in range(8):
			bit = (bitmap_byte >> i) & 1
			if bit:
				b = rom[ptr]
				ptr += 1
				output.append(b)
				buffer[buffer_p] = b
				buffer_p = (buffer_p+1) % 0x800
			else:
				b1 = rom[ptr]
				b2 = rom[ptr+1]
				ptr += 2
				offset = b1|((b2 & 0xE0)<<3)
				length = b2 & 0x1F
				for j in range(length+3):
					b = buffer[offset]
					output.append(b)
					buffer[buffer_p] = b
					buffer_p = (buffer_p+1) % 0x800
					offset = (offset+1) % 0x800
	return bytes(output[:uncompressed_length])


def decompress_lzss_FFVa(rom: bytes, start: int, header: bool = False, length=None) -> bytes:
	'''
	Oops, it's just GBA BIOS decompression functions
	see https://web.archive.org/web/20130323133944/http://nocash.emubase.de/gbatek.htm#biosdecompressionfunctions
	'''
	ptr = start
	if length:
		uncompressed_length = length
	else:
		uncompressed_length = indirect(rom, start, endian='big')
		ptr += 2
	output = []
	while len(output) < uncompressed_length:
		bitmap_byte = rom[ptr]
		ptr += 1
		for i in reversed(range(8)):
			bit = (bitmap_byte >> i) & 1
			if not bit:
				b = rom[ptr]
				ptr += 1
				output.append(b)
			else:
				b1 = rom[ptr]
				b2 = rom[ptr+1]
				ptr += 2
				length = ((b1 & 0xF0) >> 4) + 3
				trackback = -1 - (b2 + ((b1 & 0x0F) << 8))
				try:
					for j in range(length):
						output.append(output[trackback])
				except:
					print(len(output), f'0x{ptr:X}', f'0x{b1:02X}{b2:02X}', trackback)
					raise
	print(f'0x{ptr:X}')
	return bytes(output[:uncompressed_length])


def findall(rom: bytes, string: str) -> list[int]:
	results = []
	start = 0
	while True:
		val = rom.find(string, start)
		if val < 0:
			return results
		results.append(val)
		start = val + 1


def parse_ips(data: bytes):
	assert data[:5] == b'PATCH' and data[-3:] == b'EOF', 'File header and footer missing!'
	patches = {}
	ptr = 5
	while ptr < len(data)-6:
		address = int.from_bytes(data[ptr:ptr+3], 'big')
		length = int.from_bytes(data[ptr+3:ptr+5], 'big')
		if length > 0:
			payload = data[ptr+5:ptr+5+length]
			ptr += 5 + length
		else:
			repeats = data[ptr+5:ptr+7]
			payload = data[ptr+7] * repeats
			ptr += 8
		patches[address] = payload
	return patches
