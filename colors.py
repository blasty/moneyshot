color_tbl  = [ 'black', 'red', 'green', 'yellow'  ]
color_tbl += [ 'blue', 'magenta', 'cyan', 'white' ]

def fg(col):
	return "\x1b[%dm" % (30 + color_tbl.index(col))

def bold():
	return "\x1b[1m"

def end():
	return "\x1b[0m"
