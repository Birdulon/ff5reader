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
from includes.helpers import indirect, hex
from includes.ff5.const import BGM_Tracks_Safe
import struct
import wave

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
  '''
  Decodes a single 9byte BRR packet
  '''
  _range = data[0] >> 4
  filter_designation = (data[0] & 0x0C) >> 2
  loop = bool(data[0] & 0x02)
  end = bool(data[0] & 0x01)
  samples = []
  for i in data[1:]:
    b1 = (i >> 4)
    b2 = (i & 0x0F)
    # Sign-extend
    if b1 >= 8:
      b1 |= 0xFFF0
    if b2 >= 8:
      b2 |= 0xFFF0
    samples.append((b1 << _range) & 0xFFFF)
    samples.append((b2 << _range) & 0xFFFF)
  # For filter arithmetic the samples need to be in signed form.
  sample_bytes = struct.pack('<'+'H'*16, *samples)
  samples = struct.unpack('<'+'h'*16, sample_bytes)
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


class SPCParser:
  slide_resolution = 50
  notes = [i for i in range(12)]
  durations = [4, 3, 2, 4/3, 1.5, 1, 2/3, 0.75, 0.5, 1/3, 0.25, 0.5/3, 0.125, 0.25/3, 0.0625]
  def __init__(self):
    self.control_codes = [
      (1, self._set_volume),      # 0xD2
      (2, self._slide_volume),    # 0xD3
      (1, self._set_pan),         # 0xD4
      (2, self._slide_pan),       # 0xD5
      (2, 'SomeSlide'),           # 0xD6
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
      (3, self._end_loop_jump),   # 0xF9
      (2, self._jump),            # 0xFA
      (0, 'unk'),                 # 0xFB  does not end track
      (0, self._end_channel),     # 0xFC
      (0, self._end_channel),     # 0xFD
      (0, self._end_channel),     # 0xFE
      (0, self._end_channel),     # 0xFF
      ]
  def _add_slide(self, cc, value, time):
    start_value = 0  # TODO: determine the value at this point!!!
    t = 0
    v = 0
    # TODO linearly scale t from 0 to time, v from start_value to value over slide_resolution
    self.m.addControllerEvent(self.track, 0, self.time + t, cc, start_value + v)
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
    print('\tStarting loop level {} - repeat x{}'.format(len(self.loop_i), repeats))
    self.loop_i.append(self.i)
    self.loop_repeats.append(repeats)
    self.loop_passes.append(1)

  def _end_loop(self):
    print('\tEnding loop level {} - pass {} of {}'.format(len(self.loop_i)-1, self.loop_passes[-1], self.loop_repeats[-1]+1))
    if self.loop_passes[-1] < self.loop_repeats[-1]+1:
      self.i = self.loop_i[-1]
      self.loop_passes[-1] += 1
    else:
      self.loop_i.pop()
      self.loop_repeats.pop()
      self.loop_passes.pop()

  def _end_loop_jump(self, loop_pass, *address):
    if self.loop_passes[-1] >= loop_pass:
      print('\tEnding loop level {} with jump - pass {} of {}'.format(len(self.loop_i)-1, self.loop_passes[-1], self.loop_repeats[-1]+1))
      self.loop_i.pop()
      self.loop_repeats.pop()
      self.loop_passes.pop()
      self._jump(*address)

  def _jump(self, *address):
    '''
    In gameplay, this would loop infinitely.
    Since we're making finite MIDI files, we'll just loop track 0 a number of times,
    and loop the other tracks until they match the length of track 0.
    '''
    offset = (address[0] + 256*address[1]) - self.start_address
    if self.track == 0:
      self.full_repeats += 1
      if self.full_repeats < self.max_full_repeats:
        self.i = offset
      else:
        self._end_channel()
    else:
      if self.time < self.track_end[0]-4:
        self.i = offset
      else:
        self._end_channel()


  def parse(self, tracks):
    print('Parsing')
    self.m = MIDIFile(len(tracks))
    self.velocity = 100
    self.max_full_repeats = 4
    self.track_end = []
    for track, (t, address) in enumerate(tracks):
      print('\nCreating track', track, hex(address, 6))
      self.track = track
      self.start_address = address & 0xFFFF
      self.time = 0
      self.octave = 5
      self.transpose = 0
      self.loop_i = []
      self.loop_repeats = []
      self.loop_passes = []
      self.full_repeats = 0
      self.i = 0
      while self.i < len(t):
        add = 'Track {}:  {}\t{:7.3f}\t'.format(self.track, hex(self.i, 4), self.time)
        t1 = t[self.i]
        self.i += 1
        if t1 < 0xD2:
          duration = self.durations[t1%15]
          t2 = t1 // 15
          if t2<12:  # Others are rests
            note = self.notes[t2]+(12*self.octave)+self.transpose
            self.m.addNote(track, 0, note, self.time, duration, self.velocity)
          self.time += duration
          print(add, hex(t1), t2, duration)
        else:
          n, callback = self.control_codes[t1-0xD2]
          args = [t[self.i+j] for j in range(n)]
          self.i += n
          if callable(callback):
            print(add, callback.__name__, [hex(i) for i in [t1]+args])  # Maybe .__doc__ would work better
            callback(*args)
          else:
            print(add, callback, [hex(i) for i in [t1]+args])
      self.track_end.append(self.time)
    return self.m


filename_jp = 'Final Fantasy V (Japan).sfc'
def get_song_data(rom, id):
  lookup_offset = 0x043B97 + (id*3)
  offset = indirect(rom, lookup_offset, 3)-0xC00000
  bank = offset & 0xFF0000
  size = indirect(rom, offset)
  def get_track_ptr(rom, offset, bank, i):
    a = indirect(rom, offset+i) + bank
    if a < offset:
      a += 0x010000  # Bank shift
    return a
  track_ptrs = [get_track_ptr(rom, offset, bank, i) for i in range(2, 22, 2)]
  if track_ptrs[0] != track_ptrs[1]:
    print('Master is not channel 1, interesting', track_ptrs)
  tracks = [(rom[i:j], i) for i, j in zip(track_ptrs[1:-1], track_ptrs[2:])]
  #data = rom[offset+2:offset+2+size]
  return tracks

def get_sample_data(rom, id):
  lookup_offset = 0x043C6F + (id*3)
  offset = indirect(rom, lookup_offset, 3)-0xC00000
  size = indirect(rom, offset)
  data = rom[offset+2:offset+2+size]
  return data

def clamp_short(num):
  return min(max(num, -0x7FFF), 0x7FFF)

def make_sample(rom, id):
  data = get_sample_data(rom, id)
  packets = [data[i:i+9] for i in range(0, len(data), 9)]
  samples = [0, 0]  # Two zero samples for filter purposes, strip them from the actual output
  for p in packets:
    c_samples, loop, end, filter = decode_brr(p)
    samples += c_samples
    if filter == 1:
      for i in range(-8, 0, 1):
        samples[i] = clamp_short(samples[i] + (samples[i-1]*15)//16)
    elif filter == 2:
      for i in range(-8, 0, 1):
        samples[i] = clamp_short(samples[i] + (samples[i-1]*61)//32 - (samples[i-2]*15)//16 )
    elif filter == 3:
      for i in range(-8, 0, 1):
        samples[i] = clamp_short(samples[i] + (samples[i-1]*115)//64 - (samples[i-2]*13)//16 )
    if end:
      break
  return samples[2:]

def make_sample_wav(rom, id):
  samples = make_sample(rom, id)
  filename = 'Sample{}.wav'.format(id)
  with wave.open(filename, 'wb') as file:
    file.setnchannels(1)
    file.setframerate(8000)
    file.setsampwidth(2)
    sample_bytes = struct.pack('<'+'h'*len(samples), *samples)
    file.writeframes(sample_bytes)

def make_midi_file(tracks, filename='test.mid'):
  m = SPCParser().parse(tracks)
  with open(filename, 'wb') as file:
    m.writeFile(file)

def read_rom(filename=filename_jp):
  with open(filename, 'rb') as file:
    f = file.read()
  return f

if __name__ == '__main__':
    #main(sys.argv[1])
    if len(sys.argv) > 1 and sys.argv[1]:
      i = int(sys.argv[1])
      filename = 'test {:02d} - {}.mid'.format(i, BGM_Tracks_Safe[i])
      tracks = get_song_data(read_rom(), i)
      make_midi_file(tracks, filename=filename)
    else:
      for i, t in enumerate(BGM_Tracks_Safe):
        filename = 'test {:02d} - {}.mid'.format(i, t)
        print('Creating MIDI {}'.format(filename))
        tracks = get_song_data(read_rom(), i)
        make_midi_file(tracks, filename=filename)
