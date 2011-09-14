#!/usr/bin/python

import colors

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
			out += colors.fg("red") + lines[i]
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

def perl(buf, array_name = 'shellcode', row_width = 16, fancy = False):
	return code_array(buf, '$' + array_name, row_width, ' . ', fancy)

def php(buf, array_name = 'shellcode', row_width = 16, fancy = False):
	return perl(buf, array_name, row_width, fancy)

def hex_bin(str):
	return str.decode('hex')

