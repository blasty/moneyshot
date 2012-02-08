#!/usr/bin/env python

import colors
import json
import fnmatch
import os

codes = { }

def load_codes(dirname):
	global codes
	codes = load_codes_dir(dirname)

def load_codes_dir(dirname, depth = 0):
	shellcodes = { }

	entries = os.listdir(dirname)

	for entry in entries:
		if os.path.isdir(dirname + os.sep + entry):
			shellcodes[entry] = load_codes_dir(dirname + os.sep + entry, depth+1)
		else:
			basename, extension = os.path.splitext(entry)

			if extension == ".json":
				jstr = open(dirname + os.sep + entry).read()
				shellcodes[basename] = json.loads(jstr)

				# fixup multiline kodez
				shellcodes[basename]["code"] = ''.join(shellcodes[basename]["code"])
	
	return shellcodes

def find_codes(path = ''):
	global codes
	return_codes = codes

	if path == '' or path == '.':
		return return_codes

	for part in path.split(os.sep):
		if part in return_codes:
			if "description" in return_codes[part]:
				return False
			else:
				return_codes = return_codes[part]
		else:
			return False

	return return_codes

def get_by_name(path):
	global codes
	return_codes = codes

	for part in path.split(os.sep):
		if part in return_codes:
			if "description" in return_codes[part]:
				return return_codes[part]
			else:
				return_codes = return_codes[part]
		else:
			return False

def get_code_size(code_obj):
	return len(code_obj['code']) / 2


def print_codes(codes, depth = 0):
	for key in codes.keys():
		if "description" in codes[key]:
			second_col = "%s%4d%s bytes -- %s" % (colors.fg('green'), get_code_size(codes[key]), colors.end(), codes[key]['description'])
			print "  " * (depth+1) + key.ljust(40 - (depth*2)) + second_col
			
		else:
			print "  " * (depth+1) + colors.bold() + key + colors.end()
			print_codes(codes[key], depth+1)
