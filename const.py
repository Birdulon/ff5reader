'''
No license for now
'''

Glyphs = (
    ' ',' ',' ',' ',    ' ',' ',' ',' ',    ' ',' ',' ',' ',    ' ',' ',' ',' ',      # 0x00
    ' ',' ',' ',' ',    ' ',' ',' ',' ',    ' ',' ',' ',' ',    ' ',' ',' ',' ',      # 0x10
    'A','B','C','D',    'E','F','G','H',    'I','J','K','L',    'M','N','O','P',      # 0x20
    'Q','R','S','T','U','V','W','X','Y','Z','[stone]','[toad]','[mini]','[float]','[poison]','[KO]',  # 0x30
    '[blind]',' ',' ',' ',' ',' ',' ',' ',  ' ',' ',' ',' ',    ' ',' ',' ',' ',      # 0x40
    ' ',' ',' ','0',    '1','2','3','4',    '5','6','7','8',    '9','_m','_H','_P',   # 0x50
    'A','B','C','D',    'E','F','G','H',    'I','J','K','L',    'M','N','O','P',      # 0x60
    'Q','R','S','T',    'U','V','W','X',    'Y','Z','a','b',    'c','d','e','f',      # 0x70
    'g','h','i','j',    'k','l','m','n',    'o','p','q','r',    's','t','u','v',      # 0x80
    'w','x','y','z',    'il','it',' ','li', 'll','\'','"',':',   ';',',','(',')',     # 0x90
    '/','!','?','.',    'ti','fi','Bl','a', 'pe','l','\'','"',   'if','lt','tl','ir', # 0xA0
    'tt','や','ユ','ゆ', 'ヨ', 'よ', 'ワ', 'わ', 'ン', 'ん', 'ヲ','を', '[key]', '[shoe]', '◆', '[hammer]',  # 0xB0
    '⛺', '[ribbon]', '[potion]', '[shirt]', '♪', '-', '[shuriken]', '‥', '[scroll]', '!', '[claw]', '?', '[glove]', '%', '/', ':',    # 0xC0
    '「', '」', '.', 'A', 'B', 'X', 'Y', 'L', 'R', 'E', 'H', 'M', 'P', 'S', 'C', 'T',    # 0xD0
    '↑', '→', '+', '[sword]', '[wh.mag]', '[blk.mag]', '🕒', '[knife]', '[spear]', '[axe]', '[katana]', '[rod]', '[staff]', '[bow]', '[harp]', '[whip]',   # 0xE0
    '[bell]', '[shield]', '[helmet]', '[armor]', '[ring]', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ')    # F0
Glyphs_JP = list(Glyphs)  # Transcription of the japanese glyph tiles
Glyphs_JP[0x60:0xCD] = [
    'ハ','は','ヒ','ひ',  'フ','ふ','ヘ','へ',  'ホ','ほ','カ','か',  'キ','き','ク','く',  # 0x60
    'ケ','け','コ','こ',  'サ','さ','シ','し',  'ス','す','セ','せ',  'ソ','そ','タ','た',  # 0x70
    'チ','ち','ツ','つ',  'テ','て','ト','と',  'ウ','う','ア','あ',  'イ','い','エ','え',  # 0x80
    'オ','お','ナ','な',  'ニ','に','ヌ','ぬ',  'ネ','ね','ノ','の',  'マ','ま','ミ','み',  # 0x90
    'ム','む','メ','め',  'モ','も','ラ','ら',  'リ','り','ル','る',  'レ','れ','ロ','ろ',  # 0xA0
    'ヤ','や','ユ','ゆ',  'ヨ','よ','ワ','わ',  'ン','ん','ヲ','を',  'ッ','っ','ャ','ゃ',  # 0xB0
    'ュ','ゅ','ョ','ょ',  'ァ','ー','ィ', '‥',  'ぅ','！','ェ','？',  'ォ']              # 0xC0
Glyphs_JP[0xD2] = '。'
Glyphs_JP[0xE3] = '[洋剣]'
Glyphs_JP[0xE7:0xF0] = ['[刂]', '[槍]', '[鉞]', '[刀]', '[棒]', '[杖]', '[弓]', '♪', '[鞭]']
Glyphs_JP2 = list(Glyphs_JP)  # Japanese glyphs using the dakuten encoding
Glyphs_JP2[0x20:0x52] = [
    'バ','ば','ビ','び',  'ブ','ぶ','ベ','べ',  'ボ','ぼ','ガ','が',  'ギ','ぎ','グ','ぐ',  # 0x20
    'ゲ','げ','ゴ','ご',  'ザ','ざ','ジ','じ',  'ズ','ず','ゼ','ぜ',  'ゾ','ぞ','ダ','だ',  # 0x30
    'ヂ','ぢ','ヅ','づ',  'デ','で','ド','ど',             # 0x40-0x48
    'パ','ぱ','ピ','ぴ',  'プ','ぷ','ペ','ぺ',  'ポ','ぽ']  # 0x48-0x52
Glyphs_JP_large = list(Glyphs_JP2)  # Large glyphs are subtly different again
Glyphs_JP_large[0xC7] = '⋯'
Glyphs_JP_large[0xE0:0xEB] = ['←','→','+','、',  '◯', '『', 'Ｆ', '°C',  '・', '（', '）']
Glyphs_JP_large[0xFF] = '　'

Glyphs_Kanji1 = (  # TODO: finish this
    '王','行','力','様',    '　','世','界','　',    '入','城','　','士',    '　','　','海','父',  # 0x000
    '人','見','　','　',    '大','　','　','何',    '　','　','　','　',    '言','　','　','　',  # 0x010
    '　','心','間','　',    '風','　','　','　',    '　','　','　','　',    '火','　','　','　',  # 0x020
    '　','　','　','　',    '　','女','　','　',    '地','　','　','　',    '　','　','　','　',  # 0x030
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','一','　','　',  # 0x040
    '　','　','神','　',    '　','　','殿','　',    '　','　','　','　',    '　','子','　','　',  # 0x050
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x060
    '　','　','階','　',    '　','　','　','　',    '　','　','土','　',    '　','　','　','　',  # 0x070

    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x080
    '　','　','　','　',    '　','下','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x090
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x0A0
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','運','河','　',  # 0x0B0
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','少','　','　',  # 0x0C0
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x0D0
    '　','　','　','　',    '　','博','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x0E0
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x0F0

    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x100
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x110
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x120
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x130
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x140
    '炎','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x150
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x160
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x170

    '　','　','　','　',    '　','　','　','　',    '　','刀','　','　',    '　','　','　','　',  # 0x180
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x190
    '　','　','　','　',    '　','　','　','　',    '　','　')                                  # 0x1A0
Glyphs_Kanji = [g if g!='　' else '${:03X}'.format(i) for (i,g) in enumerate(Glyphs_Kanji1)]

Dialogue_Macros = {
    # Is 0x00 a wait for input marker?
    # 0x01 is linebreak
    0x02: [0x20, 0xBC, 0x82], # 0x02 expands to Bartz's name バッツ. Used for his dialogue in EN, only used for other chars in JP.
    0x03: [0x6E, 0xA8, 0x78, 0x7E, 0xAA],       # 0x03 is クリスタル
    0x04: [0x7E, 0x8C, 0x6E, 0xC5, 0xB8],       # expands to タイクーン
    0x06: [0x37, 0xBF],                         # expands to じゃ
    0x07: [0x8D, 0xAB],                         # expands to いる
    0x08: [0xFF, 0xFF, 0xFF, 0xFF],             # 4 spaces
    0x09: [0xFF, 0xFF, 0xFF],                   # 3 spaces
    0x0A: [0xFF, 0xFF],                         # 2 spaces
    # 0x0B - monster? fiend?
    # 0x0C appears to be a pause in delivery
    0x0D: [0x1E24, 0x9B, 0x1E52, 0x1E57],       # expands to 風の神殿
    # 0x0E - hiryuu?
    # 0x0F
    # 0x10 is a gil substitution
    # 0x11 and 0x12 appear to be item (obtained) substitutions

    0x14: [0x76, 0x46, 0xD0],                   # Cid speaking - シド「
    0x15: [0x9E, 0x46, 0xD0],                   # Mid speaking - ミド「
    0x16: [0x1E05, 0x1E06],                     # expands to 世界
    # 0x17 uses the next byte for something

    0x19: [0xAC, 0x92, 0xD0],                   # Lenna speaking - レナ「
    0x1A: [0x2A, 0xA6, 0x64, 0xD0],             # Galuf speaking - ガラフ「
    0x1B: [0x64, 0xC4, 0xA8, 0x78, 0xD0],       # Faris speaking - ファリス「
    0x1C: [0x6E, 0xAA, 0xAA, 0xD0],             # Krile/Kara speaking - クルル「

    # 0x1E-0x1F form kanji with the next byte
    # 0x20-0xCC are standard character set
    0xCD: [0xC9, 0xC9],                         # % (0xCD) to !!
    0xCF: [0xBD, 0x85],                         # : (0xCF) appears to expand to って
    # 0xD0-0xD4 are 「」。ＡＢ
    # 0xD5 is X - or perhaps a 2byte

    0xD9: [0x93, 0x8D],                         # expands to ない
    0xDD: [0xC7, 0xC7],                         # S (0xDD) to ……
    0xDE: [0x3F, 0x8D, 0x37, 0xC3, 0x89, 0x25], # C (0xDE) to だいじょうぶ
    0xDF: [0x61, 0xE3],                         # T (0xDF) to は、
    0xE0: [0xB9, 0x3F],                         # expands to んだ
    0xE1: [0x85, 0x8D],                         # expands to てい
    0xE2: [0x77, 0x7F],                         # expands to した
    # 0xE3 is 、
    0xE4: [0x77, 0x85],                         # ◯ (0xE4) appears to expand to して
    # 0xE5 is used for Bartz speaking in JP. This only appears as 『
    0xE6: [0x91, 0x1E0F, 0x1E03],               # F (0xE6) appears to expand to otousan (お父様)
    0xE7: [0xC9, 0xCB],                         # °C (0xE7) to !? - yes this is the wrong order interrobang
    0xE8: [0x45, 0x79],                         # ・ (0xE8) appears to expand to です
    # 0xE9, 0xEA are （）
    0xEB: [0x73, 0x9B],                         # expands to この
    # 0xEC - used in "power of crystal" context, need to confim wording ingame
    0xEF: [0x1E1C, 0xBD, 0x85],                 # expands to 言って
    # 0xF0 - soldier speaking
    0xF1: [0x6B, 0xA7],                         # expands to から
    # 0xF2 queen? doctor? hakase?
    0xF3: [0x1E0E, 0x3D, 0x6F],                 # expands to 海ぞく

    0xF5: [0x2B, 0xE3],                         # expands to が、
    # 0xF6 see dialogue 0x0A3, 0x0A4, 0x0B6 - almost certainly たち
    0xF7: [0x7F, 0x9B],                         # expands to たの
    0xF8: [0x9D, 0x79],                         # expands to ます
    0xF9: [0x6F, 0x3F, 0x75, 0x8D],             # expands to ください
    0xFA: [0x6B, 0xBD, 0x7F],                   # expands to かった
    # 0xFB - used in received item context, lenna being poisoned - maybe a sound trigger?
    0xFC: [0x95, 0xE3],                         # expands to に、

    # 0xFF is space
    }

Dialogue_Exceptions = [0xDA, 0xDB, 0xDC, 0xE3, 0xE5, 0xE9, 0xEA, 0xFF]

DoubleChars = [0x17, 0x1E, 0x1F]  # 0x1E and 0x1F are kanji, 0x17 is unknown as of yet (invisible)

BGM_Tracks = (
    "Ahead on our way", "The Fierce Battle", "A Presentiment", "Go Go Boko!",
    "Pirates Ahoy", "Tenderness in the Air", "Fate in Haze", "Moogle theme",
    "Prelude/Crystal Room", "The Last Battle", "Requiem", "Nostalgia",
    "Cursed Earths", "Lenna's Theme", "Victory's Fanfare", "Deception",
    "The Day Will Come", "Nothing?", "ExDeath's Castle", "My Home, Sweet Home",
    "Waltz Suomi", "Sealed Away", "The Four Warriors of Dawn", "Danger",
    "The Fire Powered Ship", "As I Feel, You Feel", "Mambo de Chocobo!", "Music Box",
    "Intension of the Earth", "The Dragon Spreads its Wings", "Beyond the Deep Blue Sea", "The Prelude of Empty Skies",
    "Searching the Light", "Harvest", "Battle with Gilgamesh", "Four Valiant Hearts",
    "The Book of Sealings", "What?", "Hurry! Hurry!", "Unknown Lands",
    "The Airship", "Fanfare 1", "Fanfare 2", "The Battle",
    "Walking the Snowy Mountains", "The Evil Lord Exdeath", "The Castle of Dawn", "I'm a Dancer",
    "Reminiscence", "Run!", "The Ancient Library", "Royal Palace",
    "Good Night!", "Piano Lesson 1", "Piano Lesson 2", "Piano Lesson 3",
    "Piano Lesson 4", "Piano Lesson 5", "Piano Lesson 6", "Piano Lesson 7",
    "Piano Lesson 8", "Musica Machina", "Meteor falling?", "The Land Unknown",
    "The Decisive Battle", "The Silent Beyond", "Dear Friends", "Final Fantasy",
    "A New Origin", "Chirping sound")
