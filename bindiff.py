#!/usr/bin/python3 -i
'''
Read in a bunch of small binary files, determine what parts of them are common, do something with all the differences.
Intended to separate SPC engine data from song data
'''

import sys
import traceback


def main(filenames):
  common = []
  uniques = []
  common_str = []

  try:
    files = [open(f, 'rb') for f in filenames]
    data = [f.read() for f in files]
  except BaseException as e:
    traceback.print_exc()
  finally:
    for file in files:
      file.close()

  for vals in zip(*data):
    u = set(vals)
    uniques.append(len(u))
    if len(u) == 1:
      common_str.append(vals[0])
    else:
      if len(common_str)>7:
        common.append('x'+''.join(['{:02x}'.format(b) for b in common_str])+'\n')
      common_str = []
  with open('uniques.bin', 'wb') as out:
    out.write(bytes(uniques))
  with open('common.txt', 'w') as out:
    out.writelines(common)
  print(common)


if __name__ == '__main__':
  main(sys.argv[1:])
