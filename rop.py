#!/usr/bin/python

import os
import sys
import elf
import distorm3
import optparse
import colors
import re
import binascii
from distorm3 import Decode, Decode16Bits, Decode32Bits, Decode64Bits

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
		if (m.start() % 2) != 0:
			continue

		ropmatches.append([ m.start() / 2, m.group() ])

	return ropmatches

def assemble_str(code, sixtyfour = False):
	code = code.replace(";","\n")
	code = "_start:\n" + code + "\n"
	f = open("tmp.s", 'w')
	f.write(code)
	f.close()

	if sixtyfour:
		machine = "-m64"
	else:
		machine = "-m32"

	ret = os.system("gcc "+machine+" -s -o tmp.elf tmp.s -nostartfiles -nodefaultlibs 2>/dev/null")

	if ret != 0:
		print ">> Assemble fail :("
		os.system("rm -rf tmp.s tmp.elf tmp.bin")
		exit()

	os.system("objcopy -O binary -j .text tmp.elf tmp.bin")
	pattern = binascii.hexlify(open("tmp.bin").read())
	os.system("rm -rf tmp.s tmp.elf tmp.bin")

	return pattern
	

def disas_str(addr, data, sixtyfour = False):
	parser = optparse.OptionParser()

	if sixtyfour == True:
		parser.set_defaults(dt=distorm3.Decode64Bits)
	else:
		parser.set_defaults(dt=distorm3.Decode32Bits)

	options, args = parser.parse_args(sys.argv)

	out_insn = []

	disas = distorm3.Decode(addr, data, options.dt)

	for (offset, size, instruction, hexdump) in disas:
		out_insn.append(instruction)

	return out_insn
		

def do_ropfind_raw(file, match_string):
	gadgets = []

	sixtyfour = True

	data = open(file).read()

	# figure out parameter
	if re.search("^[0-9a-f\?]+$", match_string) != None:
		pattern = match_string
	else:
		pattern = assemble_str(match_string, sixtyfour)


	print "[!] pattern: '%s'" % pattern

	matches = findstr(data, pattern)

	if len(matches) == 0:
		return

	pstr  = colors.fg('cyan') + ">> section '" + colors.bold() + "RAW" + colors.end()
	pstr += colors.fg('cyan') + "' [" + colors.bold() + str(len(matches)) + colors.end()
	pstr += colors.fg('cyan') + " hits]"

	m = 0

	for match in matches:
		if match[1] in gadgets:
			continue

		if m == 0:
			print pstr
			m = 1

		disas = disas_str(match[0], binascii.unhexlify(match[1]), sixtyfour)
		fstr =  colors.fg('cyan') + " \_ " + colors.fg('green') + "%08x [" + colors.bold() + match[1] + colors.end()
		fstr += colors.fg('green') + "] "+ colors.bold() + "-> " + colors.end()
		fstr += colors.fg('red') + ' ; '.join(disas).lower() + colors.end()
		print fstr % (match[0])

		gadgets.append(match[1])


	if m == 1:
		print ""


def do_ropfind_elf(file, match_string):
	gadgets = []

	myelf = elf.fromfile(file)

	if myelf.data[0:4] != "\x7F"+"ELF":
		print "[!] '%s' is not a valid ELF file :(" % (file)
		sys.exit(-1)

	if myelf.elfwidth == 64:
		print "[+] 64bit ELF"
		sixtyfour = True
	else:
		print "[+] 32bit ELF"
		sixtyfour = False


	# figure out parameter
	if re.search("^[0-9a-f\?]+$", match_string) != None:
		pattern = match_string
	else:
		pattern = assemble_str(match_string, sixtyfour)


	print "[!] pattern: '%s'" % pattern

	for section_name in myelf.strtable:
		if section_name == "":
			continue

		section = myelf.section(section_name)

		# check for PROGBITS type
		if section['type'] != 1:
			continue

		matches = findstr(section['data'], pattern)

		if len(matches) == 0:
			continue

		pstr  = colors.fg('cyan') + ">> section '" + colors.bold() + section_name + colors.end()
		pstr += colors.fg('cyan') + "' [" + colors.bold() + str(len(matches)) + colors.end()
		pstr += colors.fg('cyan') + " hits]"

		m = 0

		for match in matches:
			if match[1] in gadgets:
				continue

			if m == 0:
				print pstr
				m = 1

			disas = disas_str(section['addr'] + match[0], binascii.unhexlify(match[1]), sixtyfour)
			fstr =  colors.fg('cyan') + " \_ " + colors.fg('green') + "%08x [" + colors.bold() + match[1] + colors.end()
			fstr += colors.fg('green') + "] "+ colors.bold() + "-> " + colors.end()
			fstr += colors.fg('red') + ' ; '.join(disas).lower() + colors.end()
			print fstr % (section['addr'] + match[0])

			gadgets.append(match[1])


		if m == 1:
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

def main(args):
	if len(args) < 2:
		print "usage: moneyshot rop <binary> <pattern/code>"
	else:
		head = open(args[0]).read(4)
		if head == "\x7F"+"ELF":
			do_ropfind_elf(args[0], " ".join(args[1:]))
		else:
			do_ropfind_raw(args[0], " ".join(args[1:]))
