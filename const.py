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
    '「', '」', '0', 'A', 'B', 'X', 'Y', 'L', 'R', 'E', 'H', 'M', 'P', 'S', 'C', 'T',    # 0xD0
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
Glyphs_JP[0xE3] = '[洋剣]'
Glyphs_JP[0xE7:0xF0] = ['[刂]', '[槍]', '[鉞]', '[刀]', '[棒]', '[杖]', '[弓]', '♪', '[鞭]']
Glyphs_JP2 = list(Glyphs_JP)  # Japanese glyphs using the dakuten encoding
Glyphs_JP2[0x20:0x52] = [
    'バ','ば','ビ','び',  'ブ','ぶ','ベ','べ',  'ボ','ぼ','ガ','が',  'ギ','ぎ','グ','ぐ',  # 0x20
    'ゲ','げ','ゴ','ご',  'ザ','ざ','ジ','じ',  'ズ','ず','ゼ','ぜ',  'ゾ','ぞ','ダ','だ',  # 0x30
    'ヂ','ぢ','ヅ','づ',  'デ','で','ド','ど',             # 0x40-0x48
    'パ','ぱ','ピ','ぴ',  'プ','ぷ','ペ','ぺ',  'ポ','ぽ']  # 0x48-0x52
Glyphs_JP_large = list(Glyphs_JP2)  # Large glyphs are subtly different again
Glyphs_JP_large[0xE0:0xEB] = ['←','→','+','、',  '◯', '『', 'Ｆ', '°C',  '・', '（', '）']

Glyphs_Kanji = (  # TODO: finish this
    '王','行','力','様',    '　','　','　','　',    '入','城','　','士',    '　','　','　','父',  # 0x000
    '人','見','　','　',    '大','　','　','何',    '　','　','　','　',    '　','　','　','　',  # 0x010
    '　','心','間','　',    '風','　','　','　',    '　','　','　','　',    '火','　','　','　',  # 0x020
    '　','　','　','　',    '　','　','　','　',    '地','　','　','　',    '　','　','　','　',  # 0x030
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','一','　','　',  # 0x040
    '　','　','神','　',    '　','　','殿','　',    '　','　','　','　',    '　','　','　','　',  # 0x050
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x060
    '　','　','階','　',    '　','　','　','　',    '　','　','土','　',    '　','　','　','　',  # 0x070

    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x080
    '　','　','　','　',    '　','下','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x090
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x0A0
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x0B0
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','少','　','　',  # 0x0C0
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x0D0
    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',    '　','　','　','　',  # 0x0E0
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
