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
import shell

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
	print "    * rop      - ROP helper\n"

if len(sys.argv) == 1:
	banner()
	usage()
	exit()

action = sys.argv[1]

if action == "list":
	codelibrary.main(sys.argv[2:])

elif action == "fmt":
	fmt.main(sys.argv[2:])

elif action == "rop":
	ezrop.main(sys.argv[2:])

elif action == "lolsled":
	lolsled.main(sys.argv[2:])

elif action == "pattern":
	pattern.main(sys.argv[2:])

elif action == "shell":
	shell.main(sys.argv[2:])

elif action == "format":
	outputter.main(sys.argv[2:])

elif action == "build":
	builder.main(sys.argv[2:])

else:
	banner()
	usage()
	exit()
