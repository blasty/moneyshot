#!/usr/bin/python

import struct
import sys

def u32h(v):
	return struct.pack("<L", v).encode('hex')


def u32(v, hex = False):
	return struct.pack("<L", v)

# Tiny ELF stub based on:
# http://www.muppetlabs.com/~breadbox/software/tiny/teensy.html 
def make_elf_x86(sc):
	elf_head = \
		"7f454c46010101000000000000000000" + \
		"02000300010000005480040834000000" + \
		"00000000000000003400200001000000" + \
		"00000000010000000000000000800408" + \
		"00800408" + u32h(0x54+len(sc))*2 + \
		"0500000000100000"

	return elf_head.decode("hex") + sc

def main(args):
	wrap_archs = [
		{ "name" : "x86", "func" : make_elf_x86 }
	]

	if len(args) != 1:
		print "usage moneyshot elfwrap <arch>"

	arch = args[0]

	data = sys.stdin.readlines()
	data = ''.join(data)

	buf = ""

	for t_arch in wrap_archs:
		if t_arch['name'] == arch:
			buf = t_arch['func'](data)

	sys.stdout.write(buf)
