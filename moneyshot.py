#!/usr/bin/python

import sys
import colors
import outputter
import codelibrary
import codeparameters
import ezrop
import pprint


outfunc = {
	'c'       : outputter.c,
	'php'     : outputter.php,
	'perl'    : outputter.perl,
	'hexdump' : outputter.hexdump,
	'disas'   : outputter.disas,
	'bash'    : outputter.bash
}

def banner():
	ms_fancy  = colors.bold() + colors.fg('yellow') + "$$$ " + colors.end()
	ms_fancy += colors.bold() + "moneyshot" + colors.end()
	ms_fancy += " by "
	ms_fancy += colors.bold() + "blasty"  + colors.end()
	ms_fancy += colors.bold() + colors.fg('yellow') + " $$$" + colors.end()

	sys.stderr.write("\n " + ms_fancy + "\n\n")

def usage():
	print ""
	print "  usage: moneyshot <action> [options]\n"
	print "  actions:"
	print "    * list"
	print "    * build"
	print "    * pattern"
	print "    * format\n"

def warning(instr):
	print "  " + colors.fg('red') + colors.bold() + "!!" + colors.end() + " " + instr

def action_list(path = ""):
	codes = codelibrary.find_codes(path)
	print ""
	codelibrary.print_codes(codes)

def action_format(outformat):
	data = sys.stdin.readlines()
	data = ''.join(data)

	print outfunc[ outformat ](data, fancy = False),

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

def action_build(codename, inparams):
	params = { }

	# parse user args
	for keyval in inparams:
		if len(keyval.split("=")) == 2:
			(key, val) = keyval.split("=")
			params[key] = val

	if 'outformat' not in params:
		params['outformat'] = "c"

	codenames = codename.split(',')

	bincode = ''

	for curname in codenames:
		shellcode = codelibrary.get_by_name(curname)

		if "parameters" in shellcode:
			shellcode = codeparameters.handle_parameters(shellcode, params)

		bincode += outputter.hex_bin(shellcode['code'])


	outformat = params['outformat']
	print "\n\n" + outfunc[ outformat ](bincode, fancy = True)

	if 'outfile' in params:
		rawoutput = outfunc[ outformat](bincode, fancy = False)
		f = open(params['outfile'], 'w')
		f.write(rawoutput)
		f.close()


if len(sys.argv) == 1:
	usage()
	exit()

action = sys.argv[1]

codelibrary.load_codes("codes")

if action == "list":
	if len(sys.argv) == 3:
		action_list(sys.argv[2])
	else:
		action_list()

elif action == "rop":
	# figure out parameter
	#if re.search("^[0-9a-f]+$", sys.argv[3]) != None:

	ezrop.do_ropfind(sys.argv[2], sys.argv[3])

elif action == "pattern":
	if len(sys.argv) == 3:
		length = int(sys.argv[2])
		pat = gen_pattern(length)
		print pat
	elif len(sys.argv) == 4:
		length = int(sys.argv[2])
		pat = gen_pattern(length)

		if sys.argv[3][0:2] == "0x":
			hexval = int(sys.argv[3], 16)
			str  = chr(hexval & 0xff)
			str += chr((hexval >> 8) & 0xff)
			str += chr((hexval >> 16) & 0xff)
			str += chr((hexval >> 24) & 0xff)
			print pat.find(str, 0)
		else:
			print pat.find(sys.argv[3], 0)
	else:
		print "fail"

elif action == "format":
	if len(sys.argv) < 3:
		action_format("c")
	else:
		action_format(sys.argv[2])

elif action == "build":
	action_build(sys.argv[2], sys.argv[2:])
