#!/usr/bin/python

import colors
import distorm3
import optparse
import sys
import struct

from lib.darm import darm

def disas(buf, array_name = '', row_width = 16, fancy = False, sixtyfour = False):
	parser = optparse.OptionParser()

	if sixtyfour == True:
		parser.set_defaults(dt=distorm3.Decode64Bits)
	else:
		parser.set_defaults(dt=distorm3.Decode32Bits)

	options, args = parser.parse_args([])

	disas = distorm3.Decode(0, buf, options.dt)
	out = ''

	for (offset, size, instruction, hexdump) in disas:
		tmp = ''

		if fancy:
			tmp += colors.fg('cyan')

		tmp += "%.8x: " % (offset)

		if fancy:
			tmp += colors.fg('red')

		tmp += hexdump
		tmp += " " * (20-len(hexdump))

		if fancy:
			tmp += colors.fg('green')

		tmp += instruction

		if fancy:
			tmp += colors.end()

		out += "  " + tmp + "\n"

	return out.lower()

def disas64(buf, array_name = '', row_width = 16, fancy = False):
	return disas(buf, array_name, row_width, fancy, True)

def disas_arm(buf, array_name = '', row_width = 16, fancy = False):
	insns = struct.unpack("I"*(len(buf)/4), buf)
	out = ""
	pos = 0
	for insn in insns:
		tmp = ""

		if fancy:
			tmp += colors.fg('cyan')

		tmp += "%.8x: " % (pos)

		if fancy:
			tmp += colors.fg('red') + colors.bold()

		tmp += "%08x " % (insn)

		if fancy:
			tmp += colors.end() + colors.fg('green')

		tmp += str(darm.disasm_armv7(insn))

		if fancy:
			tmp += colors.end()

		out += "  " + tmp + "\n"

		pos = pos+4

	return out

def disas_thumb(buf, array_name = '', row_width = 16, fancy = False):
	insns = struct.unpack("H"*(len(buf)/2), buf)
	out = ""
	pos = 0
	for insn in insns:
		tmp = ""

		if fancy:
			tmp += colors.fg('cyan')

		tmp += "%.8x: " % (pos)

		if fancy:
			tmp += colors.fg('red') + colors.bold()

		tmp += "%08x " % (insn)

		if fancy:
			tmp += colors.end() + colors.fg('green')

		tmp += str(darm.disasm_thumb(insn))

		if fancy:
			tmp += colors.end()

		out += "  " + tmp + "\n"

		pos = pos+2

	return out

def bash(buf, array_name = 'shellcode', row_width = 16, fancy = False):
	out = "$'"
	badchars = [ 0x27, 0x5c ]
	for c in buf:
		o = ord(c)
		if o >= 0x20 and o <= 0x7E and o not in badchars:
			out += c
		else:
			out += "\\x%02x" % (o)

	out += "'"
	return out

def hexdump(buf, array_name = 'shellcode', row_width = 16, fancy = False):
	# build horizontal marker
	out = "           | "

	for i in range(0, row_width):
		if fancy:
			out += "%02x " % (i)
			#out += colors.bold() + colors.fg('yellow') + ("%02x " % (i)) + colors.end()
		else:
			out += "%02x " % (i)

	out += "|\n"

	delim_row  = "  +--------+";
	delim_row += "-" * (row_width*3 + 1) + "+" + "-" * (row_width+1) + "-+"

	if fancy:
		out += colors.bold() + delim_row + colors.end() + "\n"
	else:
		out += delim_row + "\n"

	for i in range(0, len(buf), row_width):
		if fancy:
			out += colors.bold() + "  | " + colors.fg("cyan") + ("%06x" % (i)) + " | " + colors.end()
		else:
			out += "  | %06x | " % (i)

		for j in range(0, row_width):
			if i+j < len(buf):
				if fancy:
					str = colors.fg('red') + ("%02x " % (ord(buf[i+j])))

					if (i+j)%8 >= 4:
						out += colors.bold() + str + colors.end()
					else:
						out += str + colors.end()
				else:
					out += "%02x " % (ord(buf[i+j]))
			else:
				out += "   "

		asciiz = ''

		for j in range(0, row_width):
			if i+j < len(buf):
				c = ord(buf[i+j])

				if c >= 0x20 and c <= 0x7e:
					asciiz += buf[i+j]
				else:
					asciiz += '.'
			else:
				asciiz += ' '

		if fancy:
			out += colors.bold() + "| " + colors.fg('green') + asciiz + colors.end() + colors.bold() + " |" + colors.end() + "\n"
		else:
			out += "| " + asciiz + " |\n"

	if fancy:
		out += colors.bold() + delim_row + colors.end() + "\n"
	else:
		out += delim_row + "\n"

	return out

def code_array(buf, array_name = 'shellcode', row_width = 16, line_delimiter = '', fancy = False):
	lines = []
	out = array_name +" = \n"

	for i in range(0, len(buf), row_width):
		j = 0
		linebuf = ''
		while (j < row_width and (i+j) < len(buf)):
			linebuf += "\\x%02x" % ( ord(buf[i+j]) )
			j = j + 1

		lines.append(linebuf);

	for i in range(0, len(lines)-1):
		if fancy:
			out += "\t" + colors.bold() + colors.fg('magenta') + "\""
			out += colors.fg("red") + lines[i]
			out += colors.fg('magenta') + "\"" + colors.end()
			out += line_delimiter + "\n"
		else:
			out += "\t\"%s\"%s\n" % ( lines[i], line_delimiter )

	if fancy:
		out += "\t" + colors.bold() + colors.fg('magenta') + "\""
		out += colors.fg("red") + lines[len(lines)-1]
		out += colors.fg('magenta') + "\"" + colors.end() + ";"
		out += "\n\n"
		# out += "\t\"%s\";\n\n" % ( lines[len(lines)-1] )
	else:
		out += "\t\"%s\";\n\n" % ( lines[len(lines)-1] )

	return out

def c(buf, array_name = 'shellcode', row_width = 16, fancy = False):
	if fancy:
		name  = colors.fg('green') + "unsigned " + colors.bold() + "char " + colors.end()
		name += colors.bold() + array_name + "[]" +  colors.end()
	else:
		name = "unsigned char " + array_name + "[]"

	return code_array(buf, name, row_width, '', fancy);

def carray(buf, array_name = 'shellcode', row_width = 16, fancy = False):
	out = "unsigned char %s[%d]={\n" % (array_name, len(buf))

	n = 0

	for c in buf:
		if n == len(buf)-1:
			out += "0x%02x " % (ord(c))
		else:
			out += "0x%02x, " % (ord(c))

		n=n+1

		if (n % row_width) == 0:
			out += "\n"

	out += "};\n"

	return out

def python(buf, array_name = 'shellcode', row_width = 16, fancy = False):
	lines = []
	out = ""

	for i in range(0, len(buf), row_width):
		j = 0
		linebuf = ''
		while (j < row_width and (i+j) < len(buf)):
			linebuf += "\\x%02x" % ( ord(buf[i+j]) )
			j = j + 1

		lines.append(linebuf);

	for i in range(0, len(lines)-1):
		if fancy:
			if i == 0:
				out += array_name + " =  " + colors.bold() + colors.fg('magenta') + "\""
			else:
				out += array_name + " += " + colors.bold() + colors.fg('magenta') + "\""

			out += colors.fg("red") + lines[i]
			out += colors.fg('magenta') + "\"\n" + colors.end()
		else:
			if i == 0:
				out += array_name + "  = \"%s\"\n" % ( lines[i] )
			else:
				out += array_name + " += \"%s\"\n" % ( lines[i] )

	if fancy:
		out += array_name + " += " + colors.bold() + colors.fg('magenta') + "\""
		out += colors.fg("red") + lines[len(lines)-1]
		out += colors.fg('magenta') + "\"" + colors.end() + ";"
		out += "\n\n"
		# out += "\t\"%s\";\n\n" % ( lines[len(lines)-1] )
	else:
		out += array_name + " += \"%s\";\n\n" % ( lines[len(lines)-1] )

	return out

def perl(buf, array_name = 'shellcode', row_width = 16, fancy = False):
	return code_array(buf, '$' + array_name, row_width, ' . ', fancy)

def php(buf, array_name = 'shellcode', row_width = 16, fancy = False):
	return perl(buf, array_name, row_width, fancy)

def raw(buf, array_name = '', row_width = 16, fancy = False):
	if fancy:
		return hexdump(buf, array_name, row_width, fancy)
	else:
		return buf

def hhex(buf, array_name = '', row_width = 16, fancy = False):
	return buf.encode("hex")

def hwords(buf, array_name = '', row_width = 16, fancy = False):
	i = 0

	out = ""

	if len(buf) % 2 != 0:
		buf += "\x00" * (2 - (len(buf)%2))

	while i < len(buf):
		v = struct.unpack("<H", buf[i:i+2])
		out += "%08x: 0x%04x\n" % (i, v[0])
		i = i+2

	return out

def dwords(buf, array_name = '', row_width = 16, fancy = False):
	i = 0

	out = ""

	if len(buf) % 4 != 0:
		buf += "\x00" * (4 - (len(buf)%4))

	while i < len(buf):
		v = struct.unpack("<L", buf[i:i+4])
		out += "%08x: 0x%08x\n" % (i, v[0])
		i = i+4

	return out

def qwords(buf, array_name = '', row_width = 16, fancy = False):
	i = 0

	out = ""

	if len(buf) % 8 != 0:
		buf += "\x00" * (8 - (len(buf)%8))

	while i < len(buf):
		v = struct.unpack("<Q", buf[i:i+8])
		out += "%08x: 0x%016x\n" % (i, v[0])
		i = i+8

	return out

def hex_bin(str):
	return str.decode('hex')

outfunc = {
	'c'       : c,
	'carray'  : carray,
	'php'     : php,
	'perl'    : perl,
	'hexdump' : hexdump,
	'hex'     : hhex,
	'disas'   : disas,
	'disas64' : disas64,
	'disas-arm' : disas_arm,
	'disas-thumb' : disas_thumb,
	'python'  : python,
	'bash'    : bash,
	'raw'     : raw,
	'dwords'  : dwords,
	'qwords'  : qwords,
	'hwords'  : hwords
}

def main(args):
	if len(args) > 2:
		print "usage: moneyshot format [outformat] [fancy=0]"
		return

	if len(args) >= 1:
		lang = args[0]
	else:
		lang = "c"

	if lang not in outfunc:
		print "Invalid outformat given: '%s' :(" % (lang)
		return False

	data = sys.stdin.readlines()
	data = ''.join(data)

	if len(args) == 2 and args[1] == "1":
		do_fancy = True
	else:
		do_fancy = False

	print outfunc[ lang ](data, fancy = do_fancy),
