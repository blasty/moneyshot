#!/usr/bin/python

import sys
import elf
import struct
import colors

def main(args):
	if len(args) != 1 and len(args) != 2:
		print "usage: moneyshot dumpsym <filename> [filter]"
		return

	myelf = elf.fromfile(args[0])

	sym_filter = ""

	if len(args) == 2:
		sym_filter = args[1]

	if myelf.data[0:4] != "\x7F"+"ELF":
		print "[!] '%s' is not a valid ELF file :(" % (file)
		sys.exit(-1)

	if myelf.elfwidth == 64:
		sixtyfour = True
	else:
		sixtyfour = False

	dynsym = myelf.section(".dynsym")

	if dynsym == False:
		print "ERROR: could not retrieve .dynsym section"
		exit()

	dynstr = myelf.section(".dynstr")
	
	if dynstr == False:
		print "ERROR: could not retrieve .dynstr section"
		exit()

	symbol_names = dynstr['data'].split("\x00")
	symbol_info = {}

	i = 0

	while i < len(dynsym['data']):
		if sixtyfour == True:
			# Elf64_Sym
			(
				st_name, st_info, st_other, st_shndx, st_value, st_size
			) = struct.unpack("<LBBHQQ", dynsym['data'][i:(i+24)])

			i = i+24

		else:
			# Elf32_Sym
			(
				st_name, st_value, st_size, st_info, st_other, st_shndx
			) = struct.unpack("<LLLBBH", dynsym['data'][i:(i+16)])

			i = i+16

		name_len = dynstr['data'][(st_name+1):].find("\x00")
		name = dynstr['data'][ st_name : (st_name+name_len+1) ]
		
		if sym_filter != "" and name.find(sym_filter) == -1:
			continue

		fstr  = colors.fg("green") + "[" + colors.bold() + "%08x" + colors.end()
		fstr += colors.fg("green") + "]" + colors.end() 
		fstr += " '" + colors.fg("red") + colors.bold() + "%s" + colors.end() + "'" 

		print fstr % (st_value, name)
