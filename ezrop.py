#!/usr/bin/python

import sys
import elf
import distorm3
import optparse
import colors

parser = optparse.OptionParser()
parser.set_defaults(dt=distorm3.Decode32Bits)
options, args = parser.parse_args(sys.argv)

myelf = elf.fromfile(sys.argv[1])

text = myelf.section('.text')

def match_disas(disas, match):
	for (offset, size, instruction, hexdump) in disas:
		if instruction.find(match) != -1:
			return True

	return False

def ok_disas(disas):
	for (offset, size, instruction, hexdump) in disas:
		if instruction.find("DB ") != -1:
			return False

		if instruction.find("CALL") != -1:
			return False

	return True


i = 0
while i < len(text['data']):
	if text['data'][i] == "\xc3":
		block_len = 10

		while block_len > 1:
			start = i - block_len
			end   = start + block_len + 1
			disas = distorm3.Decode(text['addr'] + start, text['data'][start:end], options.dt)

			if disas[len(disas)-1][2] == "RET" and match_disas(disas, sys.argv[2]) and ok_disas(disas):
				found_start = False

				for (offset, size, instruction, hexdump) in disas:
					if instruction.find(sys.argv[2]) != -1:
						found_start = True

					if found_start == True:
						out = colors.fg('cyan')
						out += "%.8x: " % (offset)
						out += colors.fg('red')
						out += hexdump
						out += " " * (20-len(hexdump))
						out += colors.fg('green')
						out += instruction + colors.end()
						print out

				print "=" * 50

				i = i + block_len
				break

			block_len = block_len - 1

	i = i + 1
