#!/usr/bin/python

def gen_pattern(length):
	n = 0
	out = ''

	for x in range(0,26):
		for y in range(0,26):
			for z in range(0,10):
				out += "%c%c%c" % (chr(0x41+x), chr(0x61+y), chr(0x30+z))
				n = n + 3
				if n >= length:
					return out[0:length]

def main(args):
	if len(args) == 1:
		length = int(args[0])
		pat = gen_pattern(length)
		print pat
	elif len(args) == 2:
		length = int(args[0])
		pat = gen_pattern(length)

		if args[1][0:2] == "0x":
			hexval = int(args[1], 16)
			str  = chr(hexval & 0xff)
			str += chr((hexval >> 8) & 0xff)
			str += chr((hexval >> 16) & 0xff)
			str += chr((hexval >> 24) & 0xff)
			res = pat.find(str, 0)
		else:
			res = pat.find(args[1], 0)

		if res == -1:
			print "Value not found in pattern"
		else:
			print res
	else:
		print "usage: moneyshot pattern <length> [hexval]"
