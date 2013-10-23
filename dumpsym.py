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
						sym_entry = struct.unpack("<LQQBBH", dynsym['data'][i:(i+24)])
						i = i+24
		else:
						sym_entry = struct.unpack("<LLLBBH", dynsym['data'][i:(i+16)])
						i = i+16

		name_len = dynstr['data'][(sym_entry[0]+1):].find("\x00")
		name = dynstr['data'][ (sym_entry[0]+1) : (sym_entry[0]+name_len+1) ]

		
		if sym_filter != "" and name.find(sym_filter) == -1:
			continue

		fstr  = colors.fg("green") + "[" + colors.bold() + "%08x" + colors.end() + colors.fg("green") + "]" + colors.end() 
		fstr += " '" + colors.fg("red") + colors.bold() + "%s" + colors.end() + "'" 

		print fstr % (sym_entry[1], name)

		#print "ST_NAME:%08x (%30s) ST_VALUE:%016x ST_SIZE:%016x ST_INFO:%02x ST_OTHER:%02x ST_SHNDX:%04x" % (sym_entry[0], name, sym_entry[1], sym_entry[2], sym_entry[3], sym_entry[4], sym_entry[5])

