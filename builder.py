#!/usr/bin/python

import codelibrary
import codeparameters
import outputter
import sys

def do_build(codename, inparams):
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

		if shellcode == False:
			sys.stderr.write("error: shellcode '%s' not found.\n" % curname)
			exit(-1)

		if "parameters" in shellcode:
			shellcode = codeparameters.handle_parameters(shellcode, params)

		bincode += outputter.hex_bin(shellcode['code'])


	outformat = params['outformat']

	if sys.stdout.isatty():
		do_fancy = True
	else:
		do_fancy = False

	sys.stdout.write(outputter.outfunc[ outformat ](bincode, fancy = do_fancy))

	if 'outfile' in params:
		rawoutput = outputter.outfunc[ outformat](bincode, fancy = False)
		f = open(params['outfile'], 'w')
		f.write(rawoutput)
		f.close()


def main(args):
	if len(args) < 1:
		print "usage: moneyshot build <shellcode_path> [params]"
	else:
		codelibrary.load_codes(sys.path[0] + "/codes")
		do_build(args[0], args[1:])
