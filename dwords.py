#!/usr/bin/python

import struct
import sys

def main(args):
	# try read STDIN with 0 argz
	if len(args) == 0:
		lines = sys.stdin.readlines()

		args = []

		for line in lines:
			parts = line.split(" ")

			for part in parts:
				args.append(part)

	if len(args) == 0:
		print "usage: moneyshot rep dwords <dword1> [dword2] [dword..]"
		return

	buf = ""

	for arg in args:
		buf += struct.pack("<L", int(arg, 0))

	sys.stdout.write(buf)
