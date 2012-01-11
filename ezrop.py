#!/usr/bin/python

import sys
import elf
import distorm3
import optparse
import colors
import re
import binascii

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


def findstr(section, matchstring):
	ropmatches = []

	matchstring = matchstring.replace("?", ".")

	p = re.compile(matchstring)
	for m in p.finditer(section.encode("hex")):
		ropmatches.append([ m.start(), m.group() ])

	return ropmatches

def disas_str(addr, data, sixtyfour = False):
	parser = optparse.OptionParser()

	if sixtyfour:
		parser.set_defaults(dt=distorm3.Decode64Bits)
	else:
		parser.set_defaults(dt=distorm3.Decode32Bits)

	options = []

	out_insn = []

	disas = distorm3.Decode(addr, data)
	for (offset, size, instruction, hexdump) in disas:
		out_insn.append(instruction)

	return out_insn
		

def do_ropfind(file, match_string):

	myelf = elf.fromfile(file)

	for section_name in myelf.strtable:
		if section_name == "":
			continue

		section = myelf.section(section_name)
		matches = findstr(section['data'], match_string)

		if len(matches) == 0:
			continue

		#print "[~] [%8d hits] '%s'" % (len(matches), section_name)
		pstr  = colors.fg('cyan') + ">> section '" + colors.bold() + section_name + colors.end()
		pstr += colors.fg('cyan') + "' [" + colors.bold() + str(len(matches)) + colors.end()
		pstr += colors.fg('cyan') + " hits]"
		print pstr

		for match in matches:
			disas = disas_str(section['addr'] + match[0], binascii.unhexlify(match[1]))
			fstr =  colors.fg('cyan') + " \_ " + colors.fg('green') + "%08x [" + colors.bold() + match[1] + colors.end()
			fstr += colors.fg('green') + "] "+ colors.bold() + "-> " + colors.end()
			fstr += colors.fg('red') + ' ; '.join(disas) + colors.end()
			print fstr % (section['addr'] + match[0])

		print ""

def do_ezrop(text):
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
