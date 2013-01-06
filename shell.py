#!/usr/bin/python

import socket, termios, tty, select, os

def main(args):
	if (len(args) != 2):
		print "usage: moneyshot shell <host> <port>"
		exit()	

	target = (args[0], int(args[1]))

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(target)

	old_settings = termios.tcgetattr(0)
	try:
		tty.setcbreak(0)
		c = True
		while c:
			for i in select.select([0, s.fileno()], [], [], 0)[0]:
				c = os.read(i, 1024)
				if c: os.write(s.fileno() if i == 0 else 1, c)
	except KeyboardInterrupt: pass
	finally: termios.tcsetattr(0, termios.TCSADRAIN, old_settings)
