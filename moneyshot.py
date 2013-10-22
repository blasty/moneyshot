#!/usr/bin/python

import sys
import colors, outputter, codelibrary, codeparameters
import lolsled, builder, pattern, rop, rop_arm, fmt
import shell, rep, dwords, dumpsym, dumpelf

def banner():
	asquee = """
    __   __  ______.___   __  _____._  __._______._ __  ____._________
   /  \ /  \/  __  |    \|  |/  ___| \/  /\  ___/  |  |/ __  \__   __/
  /    '    \   /  |  |\    |   _|_\    /__\   \|     |   /  |  |  |
 /___\  /    \_____|__|  \__|______||__||______/|__|__|\_____|  |__|
      \/ _____\\   """

	sys.stderr.write(colors.bold() + colors.fg('cyan') + asquee + colors.end() + "\n\n")

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
	print "    * rop      - ROP helper"
	print "    * rop-arm  - ARM ROP helper"
	print "    * rep      - String repeater"
	print "    * dwords   - binary format dwords"
	print "    * dumpsym  - dump symbols for given binary"
	print "    * dumpelf  - dump information for given binary"

if len(sys.argv) == 1:
	banner()
	usage()
	exit()

action = sys.argv[1]

valid_actions = [
	"list", "build", "pattern", "lolsled", "format", "fmt", 
	"rop", "rop-arm", "rep", "dwords", "dumpsym", "dumpelf"
]

if action not in valid_actions:
	banner()
	usage()
	exit()

action = action.replace("-", "-")

if action == "list":
	action = "codelibrary"

if action == "format":
	action = "outputter"

if action == "build":
	action = "builder"

globals()[ action ].main(sys.argv[2:])

exit()
