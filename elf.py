#!/usr/bin/python

import struct
import sys
import os

elf_types = {
	0: 'No file type',
	1: 'Relocatable file',
	2: 'Executable file',
	4: 'Core file'
} 

elf_machines = {
	0: 'No machine',
	1: 'AT&T WE 32100',
	2: 'SPARC',
	3: 'Intel 80386',
	4: 'Motorola 68k',
	5: 'Morotola 88k',
	7: 'Intel 80860',
	8: 'MIPS RS3000'
}

section_types = {
	0: 'NULL',
	1: 'PROGBITS',
	2: 'SYMTAB',
	3: 'STRTAB',
	4: 'RELA',
	5: 'HASH',
	6: 'DYNAMIC',
	7: 'NOTE',
	8: 'NOBITS',
	9: 'REL',
	10: 'SHLIB',
	11: 'DYNSYM'
}

def fromdata(data):
	return ElfObject(data)

def fromfile(filename):
	return ElfObject(open(filename, 'rb').read())

class ElfObject:
	data = ''
	strdata = ''
	header = { }
	section = { }

	def __init__(self, elf_content):
		self.data = elf_content

		self.parse_header()
		#self.print_header()

		sh_offset = self.header['shoff']
		sh_length = self.header['shnum'] * self.header['shentsize']
		sh_end    = sh_offset + sh_length
		sh_raw    = self.data[sh_offset:sh_end]

		self.parse_section_headers()

		self.strtable = [""]
		pos = 0

		if self.header['shstrnidx'] != 0:
			strstart = self.sections[ self.header['shstrnidx'] ]['offset']
			strend   = strstart + self.sections[ self.header['shstrnidx'] ]['size']
			self.strdata  = self.data[strstart:strend]

	def section(self, name):
		for section in self.sections:
			section_name = self.strdata[ section['name']:].split("\x00")[0]
			if section_name == name:
				return section

		return ""


	def parse_header(self):
		self.header['magic']   = struct.unpack("16c", self.data[0:16])
		self.header['type']    = struct.unpack("H",   self.data[16:18])[0]
		self.header['machine'] = struct.unpack("H",   self.data[18:20])[0]
		self.header['version'] = struct.unpack("L",   self.data[20:24])[0]
		self.header['entry']   = struct.unpack("L",   self.data[24:28])[0]
		self.header['phoff']   = struct.unpack("L",   self.data[28:32])[0]
		self.header['shoff']   = struct.unpack("L",   self.data[32:36])[0]
		self.header['flags']   = struct.unpack("L",   self.data[36:40])[0]

		self.header['ehsize']     = struct.unpack("H", self.data[40:42])[0]
		self.header['phentsize']  = struct.unpack("H", self.data[42:44])[0]
		self.header['phnum']      = struct.unpack("H", self.data[44:46])[0]
		self.header['shentsize']  = struct.unpack("H", self.data[46:48])[0]
		self.header['shnum']      = struct.unpack("H", self.data[48:50])[0]
		self.header['shstrnidx']  = struct.unpack("H", self.data[50:52])[0]

	def print_header(self):
		print ""

		print "ELF Type               : %s" % (elf_types[ self.header['type'] ])
		print "Header size            : %d bytes" % (self.header['ehsize'])
		print "Machine Type           : %s" % (elf_machines[ self.header['machine'] ])
		print "ELF Version            : %d" % (self.header['version'])
		print "Entrypoint             : 0x%08x" % (self.header['entry'])
		print ""
		print "Program Headers offset : 0x%08x" % (self.header['phoff'])
		print "Program Header entsize : %d bytes" % (self.header['phentsize'])
		print "Program Header count   : %d" % (self.header['phnum'])
		print ""
		print "Section Headers offset : 0x%08x" % (self.header['shoff'])
		print "Section Header entsize : %d bytes" % (self.header['shentsize'])
		print "Section Header count   : %d" % (self.header['shnum'])
		print "Stringtable section idx: %08x" % (self.header['shstrnidx'])
		print ""

	def parse_section_headers(self):
		i = 0
		self.sections = [ ]

		while i < (self.header['shnum'] * self.header['shentsize']):
			start = self.header['shoff'] + i;
			end   = start + self.header['shentsize']
			sdata = self.data[start:end]
	
			section = { }

			section['name']   = struct.unpack("L", sdata[0:4])[0]
			section['type']   = struct.unpack("L", sdata[4:8])[0]
			section['flags']  = struct.unpack("L", sdata[8:12])[0]
			section['addr']   = struct.unpack("L", sdata[12:16])[0]
			section['offset'] = struct.unpack("L", sdata[16:20])[0]
			section['size']   = struct.unpack("L", sdata[20:24])[0]
			section['link']   = struct.unpack("L", sdata[24:28])[0]
			section['info']   = struct.unpack("L", sdata[28:32])[0]
			section['align']  = struct.unpack("L", sdata[32:36])[0]
			section['entsz']  = struct.unpack("L", sdata[36:40])[0]

			start = section['offset']
			end   = start + section['size']
			section['data'] = self.data[start:end]

			self.sections.append(section)
			i = i + self.header['shentsize']

	def print_section_headers(self):
		for section in self.sections:
			if section['addr'] == 0:
				continue

			section_name = self.strdata[ section['name']:].split("\x00")[0]

			if section['type'] in section_types:
				type_string = section_types[ section['type'] ]
			else:
				type_string = "UNKNOWN"

			print "%20s @ 0x%08x [%6d bytes] ** %s" % (section_name, section['addr'], section['size'], type_string)
