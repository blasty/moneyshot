#!/usr/bin/env python

import re
import sys
import colors

## wrapper
def validate(param, value):
	validators = {
		'u8'	 : validate_u8,
		'ip'     : validate_ip,
		'u16be'  : validate_u16be,
		'string' : validate_string
	}

	return validators[ param['type'] ](value)

def output(param, value):
	outfuncs = {
		'u8'	 : output_u8,
		'ip'     : output_ip,
		'u16be'  : output_u16be,
		'string' : output_string
	}

	return outfuncs[ param['type'] ](value)

## generic number parser
def parse_num(val):
	if val[0:2] == "0x":
		return int(val, 16)
	else:
		return int(val)

## string
def validate_string(val):
	return True

def output_string(instr):
	return instr.encode('hex')

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


## U8
def validate_u8(val):
	val = parse_num(val)
	if val >= 0 and val <= 0xff:
		return True
	else:
		return False

def output_u8(val):
	val = parse_num(val)
	return "%02x" % (val)

## U16be
def validate_u16be(val):
	val = parse_num(val)
	if val >= 0 and val <= 0xffff:
		return True
	else:
		return False

def output_u16be(val):
	val = parse_num(val)
	return "%02x%02x" % ((val >> 8) & 0xff, val & 0xff)

def param_stdin(parameter):
	print >>sys.stderr, "%s  >> [%s (%s)]: %s" % (colors.bold(), parameter['name'], parameter['type'], colors.end()),
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

		print >>sys.stderr, "  " + colors.bold() + colors.fg('green') + "++" + colors.end(),
		print >>sys.stderr, " parameter " + colors.bold() + param['name'] + colors.end(),
		print >>sys.stderr, " set to '" + colors.bold() + params [ param['name'] ] + colors.end() + "'"

	return shellcode
	
