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
import fmt
import re
import socket
import termios, tty, select, os

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
	fmt.main(sys.argv[2:])

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
