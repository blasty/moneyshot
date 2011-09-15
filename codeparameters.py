#!/usr/bin/env python

import re
import sys
import colors

## wrapper
def validate(param, value):
	validators = {
		'ip'     : validate_ip,
		'u16be'  : validate_u16be,
		'string' : validate_string
	}

	return validators[ param['type'] ](value)

def output(param, value):
	outfuncs = {
		'ip'     : output_ip,
		'u16be'  : output_u16be,
		'string' : output_string
	}

	return outfuncs[ param['type'] ](value)

## string
def validate_string(val):
	return True

def output_string(instr):
	return instr.encode('hex') + 'aa'

## IP
def validate_ip(val):
	pattern = "^(([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]).){3}([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"

	if re.match(pattern, val) is not None:
		return True
	else:
		return False

def output_ip(instr):
	(a,b,c,d) = instr.split(".")
	return "%02x%02x%02x%02x" % (int(a), int(b), int(c), int(d))


## U16be
def validate_u16be(val):
	val = int(val)
	if val >= 0 and val <= 0xffff:
		return True
	else:
		return False

def output_u16be(val):
	val = int(val)
	return "%02x%02x" % ((val >> 8) & 0xff, val & 0xff)

def param_stdin(parameter):
	print "%s  >> [%s (%s)]: %s" % (colors.bold(), parameter['name'], parameter['type'], colors.end()),
	line = sys.stdin.readline()

	return line.replace("\n", "")

def handle_parameters(shellcode, params):
	for param in shellcode["parameters"]:
		ok = False

		while ok == False:
			if param['name'] not in params:
				params[ param['name'] ] = param_stdin(param)

			ok = validate(param,  params[ param['name'] ])

			if ok == False:
				print "validation for parameter " + param['name'],
				print " (of type " + param['type'] + ") ",
				print "failed with input " +  params[ param['name'] ]

				del params [ param['name'] ]

		shellcode["code"] = shellcode["code"].replace(param['placeholder'], output(param, params[ param['name'] ]))

		print "  " + colors.bold() + colors.fg('green') + "++" + colors.end(),
		print " parameter " + colors.bold() + param['name'] + colors.end(),
		print " set to '" + colors.bold() + params [ param['name'] ] + colors.end() + "'"

	return shellcode
	
