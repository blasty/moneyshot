#!/usr/bin/python

import struct
import sys
import os

elf_types = {
	0: 'No file type',
	1: 'Relocatable file',
	2: 'Executable file',
	3: 'LSB shared object',
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
	8: 'MIPS RS3000',
	62: 'x86-64'
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
	elfwidth = 0
	header = { }
	section = { }
	strtable = []

	def __init__(self, elf_content):
		self.data = elf_content

		if self.data[0:4] != "\x7F"+"ELF":
			return None

		if ord(self.data[4]) == 1:
			self.elfwidth = 32
		else:
			self.elfwidth = 64

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


		for section in self.sections:
			if section['addr'] == 0:
				continue

			section_name = self.strdata[ section['name']:].split("\x00")[0]
			self.strtable.append(section_name)

		#self.print_section_headers()

	def section(self, name):
		for section in self.sections:
			section_name = self.strdata[ section['name']:].split("\x00")[0]
			if section_name == name:
				return section

		return False

	def parse_header(self):
		self.header['magic']   = struct.unpack("16c", self.data[0:16])

		if self.elfwidth == 32:
			ehdr_unpack = "<HHLLLLLHHHHHH"
			ehdr_end = 52
		else:
			ehdr_unpack = "<HHLQQQLHHHHHH"
			ehdr_end = 64

		(
			self.header['type'],
			self.header['machine'],
			self.header['version'],
			self.header['entry'],
			self.header['phoff'],
			self.header['shoff'],
			self.header['flags'],
			self.header['ehsize'],
			self.header['phentsize'],
			self.header['phnum'],
			self.header['shentsize'],
			self.header['shnum'],
			self.header['shstrnidx']
		) = struct.unpack(ehdr_unpack, self.data[16:ehdr_end])


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

			if self.elfwidth == 32:
				shdr_end = 40
				shdr_unpack = "<LLLLLLLLLL"
			else:
				shdr_end = 64
				shdr_unpack = "<LLQQQQLLQQ"

			(
				section['name'],
				section['type'],
				section['flags'],
				section['addr'],
				section['offset'],
				section['size'],
				section['link'],
				section['info'],
				section['align'],
				section['entsz']
			) = struct.unpack(shdr_unpack, sdata[0:shdr_end])


			start = section['offset']
			end   = start + section['size']
			section['data'] = self.data[start:end]

			self.sections.append(section)
			i = i + self.header['shentsize']


	def print_section_headers(self, section_filter = ""):
		for section in self.sections:
			if section['addr'] == 0:
				continue

			section_name = self.strdata[ section['name']:].split("\x00")[0]
	
			if section['type'] in section_types:
				type_string = section_types[ section['type'] ]
			else:
				type_string = "UNKNOWN"

			if section_filter != "" and section_name.find(section_filter) == -1:
				continue

			print "%20s @ 0x%08x [%6d bytes] ** %s" % (section_name, section['addr'], section['size'], type_string)
