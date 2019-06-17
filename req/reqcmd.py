#! /usr/bin/env python
import requests
import extargsparse
import logging
import sys


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


def get_handler(args,parser):
	set_logging(args)
	for c in args.subnargs:
		try:
			rsp = requests.get(c)
			sys.stdout.write('get [%s]\n'%(c))
			sys.stdout.write('status [%s]\n'%(rsp.status_code))
			sys.stdout.write('+++++++++++++++\n%s\n----------------\n'%(rsp.content))
		except Exception as e:
			logging.error('request %s error %s'%(c,e))
	return


def main():
	commandline='''
	{
		"verbose|v" : "+",
		"get<get_handler>" : {
			"$" : "+"
		}
	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser.parse_command_line(None,parser)
	return

main()