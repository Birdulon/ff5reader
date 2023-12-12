from ..helpers import get_slices, get_contiguous_address_slices, get_null_terminated_address_slices, load_table, load_tsv
from . import files
from typing import Callable, Iterable
from pathlib import Path
from dataclasses import dataclass


@dataclass
class StringBlock:
	raw: bytes
	glyphs: Iterable[int]
	decoded: str
	string_address: int
	pointer_address: int

	def __len__(self):
		return len(self.raw)


dir = Path(__file__).parent
#print(dir)


# Transcription of RPGe glyph tiles
Glyphs_small_RPGe = load_table(dir/'Glyphs_small_RPGe.txt')
Glyphs_dialog_RPGe = load_table(dir/'Glyphs_dialog_RPGe.txt')
Glyphs_small_SNES = load_table(dir/'Glyphs_small_SNES.txt')
Glyphs_small_dakuten_SNES = load_table(dir/'Glyphs_small_dakuten_SNES.txt')
Glyphs_dialog_SNES = load_table(dir/'Glyphs_dialog_SNES.txt')
Glyphs_dialog_kanji_SNES = load_table(dir/'Glyphs_dialog_kanji_SNES.txt')


class DialogMacros:
	expansions_SNES = {
		# Is 0x00 a wait for input marker?
		# 0x01 is linebreak
		0x02: [0x20, 0xBC, 0x82], # 0x02 expands to Bartz's name バッツ. Used for his dialogue in EN, only used for other chars in JP.
		0x03: [0x6E, 0xA8, 0x78, 0x7E, 0xAA],               # 0x03 is クリスタル
		0x04: [0x7E, 0x8C, 0x6E, 0xC5, 0xB8],               # expands to タイクーン
		0x06: [0x37, 0xBF],                                 # expands to じゃ
		0x07: [0x8D, 0xAB],                                 # expands to いる
		0x08: [0xFF, 0xFF, 0xFF, 0xFF],                     # 4 spaces
		0x09: [0xFF, 0xFF, 0xFF],                           # 3 spaces
		0x0A: [0xFF, 0xFF],                                 # 2 spaces
		0x0B: [0x1E12, 0x1E13],                             # expands to 魔物
		# 0x0C appears to be a pause in delivery - affects previous char
		0x0D: [0x1E24, 0x9B, 0x1E52, 0x1E57],               # expands to 風の神殿
		0x0E: [0x1E04, 0x1E0A],                             # expands to 飛竜
		# 0x0F - unknown (invisible control char)
		# 0x10 is a gil substitution
		# 0x11 and 0x12 appear to be item (obtained) substitutions
		0x13: [0x1E07, 0x1E0D],                             # expands to 封印
		0x14: [0x76, 0x46, 0xD0],                           # Cid speaking - シド「
		0x15: [0x9E, 0x46, 0xD0],                           # Mid speaking - ミド「
		0x16: [0x1E05, 0x1E06],                             # expands to 世界
		# 0x17 uses the next byte for pause duration (seconds?)
		0x18: [0x8E, 0x6E, 0x78, 0x44, 0x78],               # expands to エクスデス
		0x19: [0xAC, 0x92, 0xD0],                           # Lenna speaking - レナ「
		0x1A: [0x2A, 0xA6, 0x64, 0xD0],                     # Galuf speaking - ガラフ「
		0x1B: [0x64, 0xC4, 0xA8, 0x78, 0xD0],               # Faris speaking - ファリス「
		0x1C: [0x6E, 0xAA, 0xAA, 0xD0],                     # Krile/Kara speaking - クルル「
		0x1D: [0x91, 0x37, 0x8D, 0x81, 0xBF, 0xB9],         # expands to おじいちゃん
		# 0x1E-0x1F form kanji with the next byte
		# 0x20-0xCC are standard character set
		0xCD: [0xC9, 0xC9],                                 # % (0xCD) to !!
		# 0xCE is ／
		0xCF: [0xBD, 0x85],                                 # : (0xCF) appears to expand to って
		# 0xD0-0xD4 are 「」。ＡＢ
		0xD5: [0x1E1B, 0x95, 0x1E08, 0xAD],                 # expands to 手に入れ
		# 0xD6, 0xD7, 0xD8 are ＹＬＲ
		0xD9: [0x93, 0x8D],                                 # expands to ない
		# 0xDA-0xDC are ＨＭＰ
		0xDD: [0xC7, 0xC7],                                 # S (0xDD) to ……
		0xDE: [0x3F, 0x8D, 0x37, 0xC3, 0x89, 0x25],         # C (0xDE) to だいじょうぶ
		0xDF: [0x61, 0xE3],                                 # T (0xDF) to は、
		0xE0: [0xB9, 0x3F],                                 # expands to んだ
		0xE1: [0x85, 0x8D],                                 # expands to てい
		0xE2: [0x77, 0x7F],                                 # expands to した
		# 0xE3 is 、
		0xE4: [0x77, 0x85],                                 # ◯ (0xE4) appears to expand to して
		# 0xE5 is used for Bartz speaking in JP. This only appears as 『
		0xE6: [0x91, 0x1E0F, 0x1E03],                       # F (0xE6) appears to expand to otousan (お父様)
		0xE7: [0xC9, 0xCB],                                 # °C (0xE7) to !? - yes this is the wrong order interrobang
		0xE8: [0x45, 0x79],                                 # ・ (0xE8) appears to expand to です
		# 0xE9, 0xEA are （）
		0xEB: [0x73, 0x9B],                                 # expands to この
		0xEC: [0x9B, 0x1E02],                               # expands to の力
		0xED: [0x70, 0xAA, 0x2A, 0xC5],                     # expands to ケルガー
		0xEE: [0x1E86, 0x1ED7, 0x1E87, 0x1E62, 0x1EA7],     # expands to 古代図書舘 (ancient library?)
		0xEF: [0x1E1C, 0xBD, 0x85],                         # expands to 言って
		0xF0: [0x1E2B, 0x1E0B, 0xD0],                       # soldier speaking - 兵士「
		0xF1: [0x6B, 0xA7],                                 # expands to から
		0xF2: [0x1E2C, 0x6A, 0x1E0C],                       # expands to 火カ船
		0xF3: [0x1E0E, 0x3D, 0x6F],                         # expands to 海ぞく
		0xF4: [0x8D, 0x37, 0xC3, 0x89],                     # expands to いじょう
		0xF5: [0x2B, 0xE3],                                 # expands to が、
		0xF6: [0x7F, 0x81],                                 # expands to たち
		0xF7: [0x7F, 0x9B],                                 # expands to たの
		0xF8: [0x9D, 0x79],                                 # expands to ます
		0xF9: [0x6F, 0x3F, 0x75, 0x8D],                     # expands to ください
		0xFA: [0x6B, 0xBD, 0x7F],                           # expands to かった
		0xFB: [0x7F, 0xC9],                                 # expands to た！
		0xFC: [0x95, 0xE3],                                 # expands to に、
		0xFD: [0x8D, 0x93, 0x8D, 0x6B, 0xA7, 0x93, 0xB9, 0x3F], # expands to いないからなんだ
		0xFE: [0x1F20, 0x1F38, 0x9B, 0x61, 0x35, 0x9D],         # expands to 次元のはざま
		# 0xFF is space
	}

	# XX: Maybe convert this to subclasses with the same method signature. Don't care enough yet.
	def expand_RPGe_dialog(raw: bytes) -> list[int]:
		output = []
		it = iter(raw)
		while (n := next(it, None)) is not None:
			if n == 0x02:  # expands to Bartz (or whatever his name is)
				output += [0x61, 0x7A, 0x8B, 0x8D, 0x93]
			elif n == 0x17:  # Pause marker
				pause_duration = next(it, None)  # Consume the duration
				# For now, we just strip these
			output.append(n)
		return output

	@classmethod
	def expand_SNES_dialog(cls, raw: bytes) -> list[int]:
		output = []
		it = iter(raw)
		while (n := next(it, None)) is not None:
			if n == 0x02:  # expands to Bartz (or whatever his name is)
				output += [0x61, 0x7A, 0x8B, 0x8D, 0x93]
			elif n == 0x17:  # Pause marker
				pause_duration = next(it, None)  # Consume the duration
				# For now, we just strip these
			elif n in (0x1E, 0x1F):  # Kanji prefix
				output.append((n<<8) + next(it, 0))  # Convert e.g. 0x1E, 0x2C to 0x1E2C
			else:
				output += cls.expansions_SNES.get(n, [n])
		return output


RPGe_Dialogue_Width = [4 for i in range(256)]
RPGe_Dialogue_Width[0x50:0xB1] = [a+1 for a in [
	 5, 2, 6, 6,     5, 6, 6, 6,     6, 6, 6, 6,     6, 8, 8, 8,  # 0x50
	 6, 6, 5, 6,     5, 5, 6, 6,     2, 6, 7, 5,    10, 7, 6, 6,  # 0x60
	 6, 6, 6, 6,     6, 6,10, 6,     6, 6, 6, 6,     5, 6, 6, 5,  # 0x70
	 6, 6, 2, 5,     6, 2,10, 6,     6, 6, 6, 5,     5, 4, 6, 6,  # 0x80
	10, 6, 6, 6,     5, 7, 6, 5,     5, 2, 5, 2,     2, 2, 3, 3,  # 0x90
	 5, 2, 6, 2,     7, 8, 0, 0,     6, 9, 2, 5,     8, 7, 7, 8,  # 0xA0
	 9
]]


def decode_RPGe_small(glyph: int) -> str:
	return Glyphs_small_RPGe[glyph]


def decode_RPGe_dialog(glyph: int) -> str:
	return Glyphs_dialog_RPGe[glyph]


def decode_SNES_small(glyph: int) -> str:
	return Glyphs_small_SNES[glyph]
	# return Glyphs_small_dakuten_SNES[glyph]


def decode_SNES_small_dakuten(glyph: int) -> str:
	return Glyphs_small_dakuten_SNES[glyph]


def decode_SNES_dialog(glyph: int) -> str:
	if glyph > 0xFF:
		kanji_idx = glyph - 0x1E00
		if kanji_idx < 0x1AA:  # Hardcoded len(Glyphs_dialog_kanji_SNES)
			return Glyphs_dialog_kanji_SNES[kanji_idx]
		return f'[0x{glyph:04x}]'
	return Glyphs_dialog_SNES[glyph]


def decode_glyphs(glyphs: list[str], glyph_decoder: Callable[[int], str]) -> str:
	return ''.join(glyph_decoder(c) for c in glyphs)


def make_snes_jp_en_strings(data: dict[str, object]) -> tuple[StringBlock, StringBlock]:
	# print(data)
	indirect_offset_jp = data.get('snes_ptr_offset')
	indirect_offset_en = data.get('rpge_ptr_offset')
	pointer_slices_jp = get_slices(data.get('snes_address', data['address']), data.get('snes_bytes', data['bytes']), data['num_entries'])
	pointer_slices_en = get_slices(data['address'], data['bytes'], data['num_entries'])

	if indirect_offset_jp is not None:
		if data.get('null_terminated'):
			address_slices_jp = get_null_terminated_address_slices(files.ROM_SNES, pointer_slices_jp, indirect_offset_jp)
		else:
			address_slices_jp = get_contiguous_address_slices(files.ROM_SNES, pointer_slices_jp, indirect_offset_jp)
	else:
		address_slices_jp = pointer_slices_jp
	if indirect_offset_en is not None:
		if data.get('null_terminated'):
			address_slices_en = get_null_terminated_address_slices(files.ROM_RPGe, pointer_slices_en, indirect_offset_en)
		else:
			address_slices_en = get_contiguous_address_slices(files.ROM_RPGe, pointer_slices_en, indirect_offset_en)
	else:
		address_slices_en = pointer_slices_en
	raws_jp = [files.ROM_SNES[s] for s in address_slices_jp]
	raws_en = [files.ROM_RPGe[s] for s in address_slices_en]

	if data.get('dialog'):
		glyphs_jp = [DialogMacros.expand_SNES_dialog(raw) for raw in raws_jp]
		glyphs_en = [DialogMacros.expand_RPGe_dialog(raw) for raw in raws_en]
		strings_jp = [decode_glyphs(glyphs, decode_SNES_dialog) for glyphs in glyphs_jp]
		strings_en = [decode_glyphs(glyphs, decode_RPGe_dialog) for glyphs in glyphs_en]
	else:
		glyphs_jp = raws_jp
		glyphs_en = raws_en
		strings_jp = [decode_glyphs(glyphs, decode_SNES_small) + ' or ' + decode_glyphs(glyphs, decode_SNES_small_dakuten) for glyphs in glyphs_jp]
		strings_en = [decode_glyphs(glyphs, decode_RPGe_small) for glyphs in glyphs_en]
	return StringBlock(raws_jp, glyphs_jp, strings_jp, address_slices_jp, pointer_slices_jp), StringBlock(raws_en, glyphs_en, strings_en, address_slices_en, pointer_slices_en)


class Strings:
	config = load_tsv(dir/'string_blocks.tsv')
	blocks_SNES_RPGe = {k: make_snes_jp_en_strings(v) for k,v in config.items()}
	blocks_SNES = {k:v[0] for k,v in blocks_SNES_RPGe.items()}
	blocks_RPGe = {k:v[1] for k,v in blocks_SNES_RPGe.items()}
