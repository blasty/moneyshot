#!/usr/bin/python

from lib.darm import darm

import os
import sys
import elf
import colors
import re
import struct
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
		if (m.start() % 2) != 0:
			continue

		ropmatches.append([ m.start() / 2, m.group() ])

	return ropmatches

def assemble_str(code):
	code = code.replace(";","\n")
	code = "_start:\n" + code + "\n"
	f = open("tmp.s", 'w')
	f.write(code)
	f.close()

	ret = os.system("arm-none-eabi-gcc -s -o tmp.elf tmp.s -nostartfiles -nodefaultlibs 2>/dev/null")

	if ret != 0:
		print ">> Assemble fail :("
		#os.system("rm -rf tmp.s tmp.elf tmp.bin")
		exit()

	os.system("arm-none-eabi-objcopy -O binary -j .text tmp.elf tmp.bin")
	pattern = binascii.hexlify(open("tmp.bin").read())
	os.system("rm -rf tmp.s tmp.elf tmp.bin")

	return pattern
	

def disas_str(addr, data, thumb_mode):
	out_insn = []


	if thumb_mode == True:
		insns = struct.unpack("H"*(len(data)/2), data)

		for insn in insns:
			out_insn.append(str(darm.disasm_thumb(insn)))
	else:
		insns = struct.unpack("I"*(len(data)/4), data)

		for insn in insns:
			out_insn.append(str(darm.disasm_armv7(insn)))

	return out_insn

def do_ropfind(file, match_string):
	gadgets = []

	myelf = elf.fromfile(file)

	if myelf.data[0:4] != "\x7F"+"ELF":
		print "[!] '%s' is not a valid ELF file :(" % (file)
		sys.exit(-1)


	# figure out parameter
	if re.search("^[0-9a-f\?]+$", match_string) != None:
		pattern = match_string
	else:
		pattern = assemble_str(match_string)


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

			disas = disas_str(section['addr'] + match[0], binascii.unhexlify(match[1]), True)
			fstr =  colors.fg('cyan') + " \_ " + colors.fg('green') + "%08x [" + colors.bold() + match[1] + colors.end()
			fstr += colors.fg('green') + "] "+ colors.bold() + "-> " + colors.end()
			fstr += colors.fg('red') + "(THUMB) "  + ' ; '.join(disas).lower() + colors.end()
			print fstr % (section['addr'] + match[0])

			gadgets.append(match[1])
			if (len(binascii.unhexlify(match[1])) % 4) == 0:
				disas = disas_str(section['addr'] + match[0], binascii.unhexlify(match[1]), False)
				fstr =  colors.fg('cyan') + " \_ " + colors.fg('green') + "%08x [" + colors.bold() + match[1] + colors.end()
				fstr += colors.fg('green') + "] "+ colors.bold() + "-> " + colors.end()
				fstr += colors.fg('red') + "(ARM  ) " + ' ; '.join(disas).lower() + colors.end()

				if not (len(disas) == 1 and disas[0] == ""):
					print fstr % (section['addr'] + match[0])

				gadgets.append(match[1])

		if m == 1:
			print ""


def main(args):
	if len(args) < 2:
		print "usage: moneyshot rop-arm <binary> <pattern/code>"
	else:
		do_ropfind(args[0], " ".join(args[1:]))
