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
small_palette = [0xFF000000, 0x00000080, 0xFF808080, 0xFFFFFFFF]
dialogue_palette = [0xFF000080, 0xFFFFFFFF]
mono_palette = [0xFF000000, 0xFFFFFFFF]


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
Glyphs_JP2[0x20:0x53] = [
    'バ','ば','ビ','び',  'ブ','ぶ','ベ','べ',  'ボ','ぼ','ガ','が',  'ギ','ぎ','グ','ぐ',  # 0x20
    'ゲ','げ','ゴ','ご',  'ザ','ざ','ジ','じ',  'ズ','ず','ゼ','ぜ',  'ゾ','ぞ','ダ','だ',  # 0x30
    'ヂ','ぢ','ヅ','づ',  'デ','で','ド','ど',  'ヴ',       # 0x40-0x49
    'パ','ぱ','ピ','ぴ',  'プ','ぷ','ペ','ぺ',  'ポ','ぽ']  # 0x49-0x53
Glyphs_JP_large = list(Glyphs_JP2)  # Large glyphs are subtly different again
Glyphs_JP_large[0xC7] = '⋯'
Glyphs_JP_large[0xE0:0xEB] = ['←','→','+','、',  '◯', '『', 'Ｆ', '°C',  '・', '（', '）']
Glyphs_JP_large[0xFF] = '　'

Glyphs_Kanji = (
    '王', '行', '力', '様',    '飛', '世', '界', '封',  # 0x000
    '入', '城', '竜', '士',    '船', '印', '海', '父',  # 0x008
    '人', '見', '魔', '物',    '大', '者', '本', '何',  # 0x010
    '戦', '出', '気', '手',    '言', '石', '守', '辺',  # 0x018
    '無', '心', '間', '前',    '風', '帰', '私', '生',  # 0x020
    '年', '武', '器', '兵',    '火', '使', '中', '急',  # 0x028
    '時', '森', '来', '砂',    '動', '女', '待', '臣',  # 0x030
    '地', '助', '当', '今',    '上', '悪', '泉', '騎',  # 0x038

    '思', '持', '変', '水',    '塔', '草', '仲', '復',  # 0x040
    '目', '作', '分', '知',    '機', '一', '姫', '最',  # 0x048
    '聞', '械', '神', '流',    '乗', '取', '町', '殿',  # 0x050
    '事', '空', '勇', '村',    '早', '子', '格', '納',  # 0x058
    '伝', '消', '書', '長',    '話', '合', '所', '場',  # 0x060
    '脱', '北', '後', '全',    '忍', '獣', '詩', '吟',  # 0x068
    '落', '自', '階', '説',    '残', '親', '活', '休',  # 0x070
    '姉', '破', '土', '度',    '記', '発', '赤', '侍',  # 0x078

    '死', '国', '旅', '完',    '小', '林', '古', '図',  # 0x080
    '礼', '商', '島', '邪',    '部', '狩', '精', '姿',  # 0x088
    '防', '向', '先', '解',    '板', '下', '台', '賢',  # 0x090
    '対', '木', '成', '命',    '配', '法', '飲', '回',  # 0x098
    '願', '門', '東', '開',    '貸', '増', '危', '舘',  # 0x0A0
    '道', '身', '老', '西',    '近', '層', '第', '青',  # 0x0A8
    '光', '読', '外', '理',    '強', '同', '谷', '負',  # 0x0B0
    '意', '学', '攻', '屋',    '体', '運', '河', '聖',  # 0x0B8

    '必', '南', '方', '黒',    '絶', '食', '艇', '山',  # 0x0C0
    '穴', '名', '受', '暁',    '傷', '少', '鼻', '倉',  # 0x0C8
    '然', '的', '男', '用',    '酒', '安', '現', '代',  # 0x0D0
    '立', '具', '育', '続',    '通', '会', '庫', '飼',  # 0x0D8
    '日', '窟', '砲', '広',    '化', '博', '以', '兄',  # 0x0E0
    '室', '洞', '別', '番',    '昔', '住', '吸', '去',  # 0x0E8
    '宝', '毒', '売', '好',    '枝', '踊', '月', '巣',  # 0x0F0
    '底', '明', '感', '宿',    '召', '喚', '決', '形',  # 0x0F8

    '団', '異', '初', '険',    '家', '息', '連', '集',  # 0x100
    '墓', '著', '跡', '遺',    '内', '悲', '教', '返',  # 0x108
    '頭', '再', '高', '借',    '登', '走', '過', '敵',  # 0x110
    '鏡', '愛', '魚', '燃',    '幅', '音', '血', '滝',  # 0x118
    '次', '閉', '求', '声',    '箱', '軍', '泣', '港',  # 0x120
    '冊', '秒', '憶', '潜',    '爆', '恋', '石', '左',  # 0x128
    '役', '放', '衛', '母',    '建', '角', '信', '師',  # 0x130
    '元', '失', '字', '歩',    '遊', '頂', '震', '収',  # 0x138

    '追', '暗', '橋', '起',    '約', '束', '文', '反',  # 0x140
    '絵', '能', '歌', '弱',    '境', '波', '針', '千',  # 0x148
    '炎', '望', '雨', '金',    '希', '花', '不', '白',  # 0x150
    '剣', '陸', '勝', '烏',    '笛', '究', '三', '探',  # 0x158
    '夜', '病', '半', '美',    '敗', '友', '研', '予',  # 0x160
    '支', '々', '除', '数',    '店', '翼', '充', '填',  # 0x168
    '薬', '弟', '経', '験',    '値', '闘', '得', '闇',  # 0x170
    '混', '乱', '点', '速',    '閃', '射', '斬', '鉄',  # 0x178

    '宣', '告', '電', '磁',    '圧', '昇', '重', '倍',  # 0x180
    '妖', '刀', '拡', '散',    '影', '御', '正', '漠',  # 0x188
    '特', '胸', '永', '遠',    '議', '浮', '眠', '逃',  # 0x190
    '滅', '囗', '極', '湖',    '利', '周', '緑', '切',  # 0x198
    '紙', '胸', '平', '和',    '宇', '宙', '則', '孤',  # 0x1A0
    '溝', '　')                                       # 0x1A8

Dialogue_Macros_EN = {
    0x02: [0x61, 0x7A, 0x8B, 0x8D, 0x93],  # expands to Bartz (or whatever his name is)
    }

Dialogue_Macros_JP = {
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
DoubleChars = set([0x17, 0x1E, 0x1F])  # 0x1E and 0x1F are kanji, 0x17 is a pause marker

Dialogue_Width = [4 for i in range(256)]
Dialogue_Width[0x50:0xB1] = [a+1 for a in [
    5, 2, 6, 6,     5, 6, 6, 6,     6, 6, 6, 6,     6, 8, 8, 8,  # 0x50
    6, 6, 5, 6,     5, 5, 6, 6,     2, 6, 7, 5,     10,7, 6, 6,  # 0x60
    6, 6, 6, 6,     6, 6, 10,6,     6, 6, 6, 6,     5, 6, 6, 5,  # 0x70
    6, 6, 2, 5,     6, 2, 10,6,     6, 6, 6, 5,     5, 4, 6, 6,  # 0x80
    10,6, 6, 6,     5, 7, 6, 5,     5, 2, 5, 2,     2, 2, 3, 3,  # 0x90
    5, 2, 6, 2,     7, 8, 0, 0,     6, 9, 2, 5,     8, 7, 7, 8,  # 0xA0
    9
    ]]

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
    "A New Origin", "Chirping sound"
    )



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
