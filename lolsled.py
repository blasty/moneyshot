#!/usr/bin/python

import sys
import rop
import colors

# Yo DAWG, This is the most retarded
# and limitted x86 subset emulation 
# out in the wild! Only here to cater
# some LOLsled generation, heheheh.

func = {
	'@' : lambda x: inc(x, 'eax'),
	'A' : lambda x: inc(x, 'ecx'),
	'B' : lambda x: inc(x, 'edx'),
	'C' : lambda x: inc(x, 'ebx'),
	'D' : lambda x: inc(x, 'esp'),
	'E' : lambda x: inc(x, 'ebp'),
	'F' : lambda x: inc(x, 'esi'),
	'G' : lambda x: inc(x, 'edi'),
	'H' : lambda x: dec(x, 'eax'),
	'I' : lambda x: dec(x, 'ecx'),
	'J' : lambda x: dec(x, 'edx'),
	'K' : lambda x: dec(x, 'ebx'),
	'L' : lambda x: dec(x, 'esp'),
	'M' : lambda x: dec(x, 'ebp'),
	'N' : lambda x: dec(x, 'esi'),
	'O' : lambda x: dec(x, 'edi'),
	'P' : lambda x: dec(x, 'esp', 4),
	'Q' : lambda x: dec(x, 'esp', 4),
	'R' : lambda x: dec(x, 'esp', 4),
	'S' : lambda x: dec(x, 'esp', 4),
	'T' : lambda x: dec(x, 'esp', 4),
	'U' : lambda x: dec(x, 'esp', 4),
	'V' : lambda x: dec(x, 'esp', 4),
	'W' : lambda x: dec(x, 'esp', 4),
	'X' : lambda x: inc(x, 'esp', 4),
	'Y' : lambda x: inc(x, 'esp', 4),
	'Z' : lambda x: inc(x, 'esp', 4),
	'[' : lambda x: inc(x, 'esp', 4),
	'\\' : lambda x: inc(x, 'esp', 4),
	']' : lambda x: inc(x, 'esp', 4),
	'^' : lambda x: inc(x, 'esp', 4),
	'_' : lambda x: inc(x, 'esp', 4),
}

def inc(ctx, reg, n=1):
	ctx[reg] = ctx[reg]+n
	return ctx

def dec(ctx, reg, n=1):
	ctx[reg] = ctx[reg]-n
	return ctx;

def emu(input_code):
	regs = {
		'eax' : 0,
		'ebx' : 0,
		'ecx' : 0,
		'edx' : 0,
		'esi' : 0,
		'edi' : 0,
		'ebp' : 0,
		'esp' : 0
	}

	for c in input_code:
		if c not in func:
			print "*** ILLEGAL OPCODE '%c' *** :(" % (c)
			return

		regs = func[c](regs)

	#print regs

	return regs


def main(args):
	if len(args) != 1 and len(args) != 2:
		print "usage:"
		print "  moneyshot lolsled <length> <words>"
		print "  moneyshot lolsled <dictionary>"

		return 

	# some 'harmless' x86 insns, just inc's and dec's
	whitelist=[
		"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"
	]

	# length?
	if args[0].isdigit():
		rs = emu(args[1])
		fstr = " CLOBBER: "
		cl = False
		for reg in rs:
			if rs[reg] != 0:
				fstr += "%s=%08x " % (reg, rs[reg])
				cl = True

		if cl == False:
			fstr += "No clobbering, yay!"

		print fstr

	# assume dictfile (find mode)
	else:
		words = open(args[0]).readlines()
		for word in words:
			ok = True
			word = word.strip().upper()

			for c in word:
				if c not in whitelist:
					ok = False

			if not ok:
				continue

			fstr = colors.fg('cyan')
			fstr += ">> "
			fstr += colors.fg('green')
			fstr += "'%15s' %s--> " % (word, colors.fg('white')+colors.bold())
			fstr += colors.end() + colors.fg('red')
			r = rop.disas_str(0, word)
			fstr += ' ; '.join(r).lower()
			rs = emu(word)
			fstr += " CLOBBER: "
			cl = False
			for reg in rs:
				if rs[reg] != 0:
					fstr += "%s=%08x " % (reg, rs[reg])
					cl = True

			print fstr

	print colors.end()

