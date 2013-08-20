#!/usr/bin/python

import struct
import sys

def main(args):
	if len(args) == 0:
		print "usage: moneyshot rep dwords <dword1> [dword2] [dword..]"
		return

	buf = ""

	for arg in args:
		buf += struct.pack("<L", int(arg, 0))

	sys.stdout.write(buf)
