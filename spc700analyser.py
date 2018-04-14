#!/usr/bin/python3 -i
'''
No license for now

Search for potential BRR samples in an spc700 file.


SPC-700 info
0x00100 - 0x100FF contains RAM and is all we are interested in at present (64 KiB - 16bit address space)


BRR info
16bit audio samples.
Blocks of 9 bytes.

First byte is a header of form
    rrrr ffle
Where rrrr is "range"/"granularity", rather the amount to leftshift the following samples by (0-12)
ff is filter designation. Might be important later.
l is loop flagbit. Normally 0 except on the last block.
e is last chunk of sample. We'll use l and e to try to find series of chunks.

Trailing 8 bytes are 16 4bit nibbles that make up the compressed samples.
'''
import sys
from midiutil import MIDIFile
from includes.helpers import indirect

def generate_pointer_set(data):
  '''
  Scan through entire dataset and collect everything that could be a pointer.
  '''
  ptr_set = set()
  d_len = len(data)
  for i in range(d_len-1):
    x = int.from_bytes(data[i:i+2], 'little')
    if x < d_len-9:
      ptr_set.add(x)
  return ptr_set


def analyse_sample(data, pointer):
  length = 0
  while data[pointer] & 1 == 0:
    length += 1
    pointer += 9
    if pointer > len(data)-9:
      return 0
  return length


def decode_brr(data):
  range = data[0] >> 4
  filter_designation = (data[0] & 0x0C) >> 2
  loop = bool(data[0] & 0x02)
  end = bool(data[0] & 0x01)
  samples = []
  for i in range(8):
    samples.append((data[1+range] >> 4) << range)
    samples.append((data[1+range] & 0x0F) << range)
  return (samples, loop, end, filter_designation)


def main(filename):
  global RAM, brr_dict
  with open(filename, 'rb') as file1:
    RAM = file1.read()[0x00100:0x10100]
  ptr_set = generate_pointer_set(RAM)
  blacklist = set()  # Avoid re-entering sample chains
  brr_dict = {}
  for ptr in ptr_set:
    if ptr in blacklist:
      continue
    length = analyse_sample(RAM, ptr)
    if length > 49:  # Ignore anything less than 50 blocks (800 samples) long
      brr_dict[ptr] = length
      for i in range(length):
        blacklist.add(ptr+((i+1)*9))
  for k in sorted(brr_dict.keys()):
    print('0x{:04x}: {:4d}'.format(k, brr_dict[k]))


filename_jp = 'Final Fantasy V (Japan).sfc'
def get_song_data(rom, id):
  lookup_offset = 0x043B97 + (id*3)
  offset = indirect(rom, lookup_offset, 3)-0xC00000
  bank = offset & 0xFF0000
  size = indirect(rom, offset)
  track_ptrs = [indirect(rom, offset+i)+bank for i in range(2, 22, 2)]
  if track_ptrs[0] != track_ptrs[1]:
    print('Master is not channel 1, interesting', track_ptrs)
  tracks = [rom[i:j] for i, j in zip(track_ptrs[1:-1], track_ptrs[2:])]
  #data = rom[offset+2:offset+2+size]
  return tracks


class SPCParser:
  notes = [i for i in range(12)]
  durations = [4, 3, 2, 4/3, 1.5, 1, 2/3, 0.75, 0.5, 1/3, 0.25, 0.5/3, 0.125, 0.25/3, 0.0625]
  def __init__(self):
    self.control_codes = [
      (1, self._set_volume),      # 0xD2
      (2, self._slide_volume),    # 0xD3
      (1, self._set_pan),         # 0xD4
      (2, self._slide_pan),       # 0xD5
      (1, 'SomeSlide'),           # 0xD6
      (3, 'Vibrato'),             # 0xD7
      (0, 'VibratoOff'),          # 0xD8
      (3, 'Tremolo'),             # 0xD9
      (0, 'TremoloOff'),          # 0xDA
      (2, 'PanLoop'),             # 0xDB
      (0, 'PanLoopOff'),          # 0xDC
      (1, 'Noise'),               # 0xDD
      (0, 'NoiseOff'),            # 0xDE
      (0, 'unk'),                 # 0xDF
      (0, 'unk'),                 # 0xE0
      (0, 'unk'),                 # 0xE1
      (0, 'EchoOn'),              # 0xE2
      (0, 'EchoOff'),             # 0xE3
      (1, self._set_octave),      # 0xE4
      (0, self._inc_octave),      # 0xE5
      (0, self._dec_octave),      # 0xE6
      (1, self._set_transpose),   # 0xE7
      (1, self._rel_transpose),   # 0xE8
      (1, 'FineTune'),            # 0xE9
      (1, self._set_instrument),  # 0xEA
      (1, 'unk1'),                # 0xEB
      (1, 'unk1'),                # 0xEC
      (0, 'unk'),                 # 0xED
      (1, 'unk1'),                # 0xEE
      (0, 'unk'),                 # 0xEF
      (1, self._start_loop),      # 0xF0
      (0, self._end_loop),        # 0xF1
      (0, self._end_channel),     # 0xF2
      (1, self._set_tempo),       # 0xF3
      (2, self._slide_tempo),     # 0xF4
      (1, 'SetEchoVel'),          # 0xF5
      (2, 'SlideEchoVel'),        # 0xF6
      (2, 'unk2'),                # 0xF7
      (1, 'SetGlobalVel'),        # 0xF8
      (3, 'EndLoop2'),            # 0xF9
      (0, 'unk'),                 # 0xFA
      (0, 'unk'),                 # 0xFB
      (0, self._end_channel),     # 0xFC
      (0, self._end_channel),     # 0xFD
      (0, self._end_channel),     # 0xFE
      (0, self._end_channel),     # 0xFF
      ]

  def _set_instrument(self, instrument):
    self.m.addProgramChange(self.track, 0, self.time, instrument)
  def _set_volume(self, volume):
    self.m.addControllerEvent(self.track, 0, self.time, 7, volume//2)  # 0-255 needs to be 0-127 for MIDI
  def _slide_volume(self, volume, time):
    # TODO slide
    self.m.addControllerEvent(self.track, 0, self.time, 7, volume//2)  # 0-255 needs to be 0-127 for MIDI
  def _set_pan(self, pan):
    self.m.addControllerEvent(self.track, 0, self.time, 7, 127-(pan//2))  # SPC panning is reversed
  def _slide_pan(self, pan, time):
    # TODO slide
    self.m.addControllerEvent(self.track, 0, self.time, 7, 127-(pan//2))
  def _set_octave(self, octave):
    self.octave = octave
  def _inc_octave(self):
    self.octave += 1
  def _dec_octave(self):
    self.octave -= 1
  def _set_transpose(self, transpose):
    self.transpose = transpose
  def _rel_transpose(self, transpose):
    self.transpose += transpose
  def _end_channel(self):
    self.i = 0xFFFFFFFF
  def _set_tempo(self, tempo):
    self.m.addTempo(self.track, self.time, tempo)
  def _slide_tempo(self, time, tempo):
    # TODO slide
    self.m.addTempo(self.track, self.time, tempo)
  def _start_loop(self, repeats):
    print('Starting loop', repeats)
    self.loop_i = self.i
    self.repeats = repeats
  def _end_loop(self):
    print('Ending loop', self.repeats)
    if self.repeats > 0:
      self.i = self.loop_i
    self.repeats -= 1


  def parse(self, tracks):
    print('Parsing')
    self.m = MIDIFile(len(tracks))
    self.velocity = 100
    for track, t in enumerate(tracks):
      print('Creating track', track)
      self.track = track
      self.time = 0
      self.octave = 5
      self.transpose = 0
      self.repeats = 0
      self.loop_i = 0
      self.i = 0
      while self.i < len(t):
        t1 = t[self.i]
        self.i += 1
        if t1 < 0xD2:
          duration = self.durations[t1%15]
          t2 = t1 // 15
          if t2<12:  # Others are rests
            note = self.notes[t2]+(12*self.octave)+self.transpose
            self.m.addNote(track, 0, note, self.time, duration, self.velocity)
          self.time += duration
        else:
          n, callback = self.control_codes[t1-0xD2]
          args = [t[self.i+j] for j in range(n)]
          self.i += n
          if callable(callback):
            callback(*args)
          else:
            print(callback, '0x{:02x}'.format(t1))
    return self.m

def make_midi_file(tracks, filename='test.mid'):
  m = SPCParser().parse(tracks)
  with open(filename, 'wb') as file:
    m.writeFile(file)

def read_rom(filename=filename_jp):
  with open(filename, 'rb') as file:
    f = file.read()
  return f

if __name__ == '__main__':
    main(sys.argv[1])
