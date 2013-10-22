#!/usr/bin/python

import sys
import elf
import struct

def main(args):
	if len(args) != 1 and len(args) != 2:
		print "usage: moneyshot dumpelf <filename> [filter]"
		return

	section_filter = ""

	if len(args) == 2:
		section_filter = args[1]

	myelf = elf.fromfile(args[0])

	if section_filter == "":
		myelf.print_header()

	myelf.print_section_headers(section_filter)
