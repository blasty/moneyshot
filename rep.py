#!/usr/bin/python

import sys

def main(args):
	if len(args) != 2:
		print "usage: moneyshot rep <str> <length>"
		return

	sys.stdout.write(args[0] * int(args[1]))
