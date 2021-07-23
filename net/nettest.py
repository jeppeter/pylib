#! /usr/bin/env


import extargsparse
import logging
import sys
import socket
import re


def set_logging(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	if logging.root is not None and len(logging.root.handlers) > 0:
		logging.root.handlers = []
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return

def connect_handler(args,parser):
	set_logging(args)
	socktype = socket.SOCK_STREAM
	if args.udpmode:
		socktype = socket.SOCK_DGRAM
	host = '127.0.0.1'
	port = 6200
	if len(args.subnargs) > 0:
		hoststr = args.subnargs[0]
		sarr = re.split(':',hoststr)
		host = sarr[0]
		if len(sarr) > 1:
			port = int(sarr[1])
	with socket.socket(socket.AF_INET,socktype) as s:
		s.connect((host,port))
		sys.stdout.write('connect [%s] succ\n'%(args.subnargs[0]))
	sys.exit(0)

def main():
	commandline='''
	{
		"verbose|v" : "+",
		"udpmode|U" : false,
		"connect<connect_handler>" : {
			"$" : "+"
		}
	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser.parse_command_line(None,parser)
	raise Exception('can not reach here')
	return

if __name__ == '__main__':
	main()