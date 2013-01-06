#!/usr/bin/python

import sys
import colors
import outputter
import codelibrary
import codeparameters
import ezrop
import pprint
import re
import socket
import termios, tty, select, os

from lib.libformatstr import FormatStr

outfunc = {
	'c'       : outputter.c,
	'php'     : outputter.php,
	'perl'    : outputter.perl,
	'hexdump' : outputter.hexdump,
	'disas'   : outputter.disas,
	'bash'    : outputter.bash,
	'raw'     : outputter.raw
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
	print "    * list     - list shellcodes"
	print "    * build    - build shellcodes"
	print "    * pattern  - build patterns"
	print "    * lolsled  - build a lolsled"
	print "    * format   - format input"
	print "    * fmt      - formatstring helper"
	print "    * rop      - ROP helper\n"

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
	banner()
	usage()
	exit()

action = sys.argv[1]

codelibrary.load_codes(sys.path[0] + "/codes")

if action == "list":
	if len(sys.argv) == 3:
		action_list(sys.argv[2])
	else:
		action_list()

elif action == "fmt":
	if len(sys.argv) < 3:
		print "usage: moneyshot fmt <primitives>\n"
		print "availables primitives:"
		print "  * p:NNNN      - parameter position where user-controlled input starts"
		print "  * n:NNNN      - specify bytes already written (defaults to 0)"
		print "  * w:XXXX=YYYY - write value YYYY to address XXXX\n"

	p = FormatStr()

	param_pos = 0
	already_written = 0

	for param in  sys.argv[2:]:
		if param[0:2] == "w:":
			(addr,val) = param[2:].split("=")
			p[ int(addr, 0) ] = int(val, 0);
		elif param[0:2] == "p:":
			param_pos = int(param[2:], 0)
		elif param[0:2] == "n:":
			already_written = int(param[2:], 0)
		else:
			print "UNKNOWN FMT specifier: '%s'" % (param)
			exit()

	sys.stdout.write( p.payload(param_pos, start_len=already_written) )

elif action == "rop":
	if len(sys.argv) < 4:
		print "usage: moneyshot rop <binary> <pattern/code>"
	else:
		ezrop.do_ropfind(sys.argv[2], " ".join(sys.argv[3:]))

elif action == "lolsled":
	if len(sys.argv) < 3:
		print "usage:"
		print "  moneyshot lolsled <length>"
		print "  moneyshot lolsled <dictionary>"

	# some 'harmless' x86 insns, just inc's and dec's
	whitelist=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]

	# length?
	if sys.argv[2].isdigit():
		print "not implemented"
	# assume dictfile (find mode)
	else:
		words = open(sys.argv[2]).readlines()
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
			r = ezrop.disas_str(0, word)
			fstr += ' ; '.join(r).lower()

			print fstr

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
			res = pat.find(str, 0)
		else:
			res = pat.find(sys.argv[3], 0)

		if res == -1:
			print "Value not found in pattern"
		else:
			print res
	else:
		print "usage: moneyshot pattern <length> [hexval]"

elif action == "shell":
	if (len(sys.argv) != 4):
		print "usage: moneyshot shell <host> <port>"
		exit()	

	target = (sys.argv[2], int(sys.argv[3]))

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(target)

	old_settings = termios.tcgetattr(0)
	try:
		tty.setcbreak(0)
		c = True
		while c:
			for i in select.select([0, s.fileno()], [], [], 0)[0]:
				c = os.read(i, 1024)
				if c: os.write(s.fileno() if i == 0 else 1, c)
	except KeyboardInterrupt: pass
	finally: termios.tcsetattr(0, termios.TCSADRAIN, old_settings)

elif action == "format":
	if len(sys.argv) < 3:
		action_format("c")
	else:
		action_format(sys.argv[2])

elif action == "build":
	if len(sys.argv) < 3:
		print "usage: moneyshot build <shellcode_path> [params]"
	else:
		action_build(sys.argv[2], sys.argv[2:])

else:
	banner()
	usage()
	exit()
