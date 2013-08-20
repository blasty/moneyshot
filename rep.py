#!/usr/bin/python

def main(args):
	if len(args) != 2:
		print "usage: moneyshot rep <str> <length>"
		return

	print args[0] * int(args[1]),
