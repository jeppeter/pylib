#! /usr/bin/env python

import extargsparse
import logging
import sys

def set_logging_args(parser):
	cmdline='''
	{
		"verbose|v" : "+",
		"logstderr" : true,
		"logapps" : [],
		"logfiles" : []
	}
	'''
	parser.load_command_line_string(cmdline)
	return parser


def set_logging(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	if logging.root is not None and len(logging.root.handlers) > 0:
		logging.root.handlers = []

	cformat = '%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s'
	basicfmt = logging.Formatter(cformat)

	logging.basicConfig(level=loglvl,format=cformat)
	if not args.logstderr:
		logging.root.handlers = []

	for f in args.logapps:
		apphdl = logging.FileHandler(f,mode='a')
		apphdl.setFormatter(basicfmt)
		apphdl.setLevel(loglvl)
		logging.root.addHandler(apphdl)
	for f in args.logfiles:
		loghdl = logging.FileHandler(f,mode='w')
		loghdl.setFormatter(basicfmt)
		loghdl.setLevel(loglvl)
		logging.root.addHandler(loghdl)
	return


def main():
	parser = extargsparse.ExtArgsParse()
	parser = set_logging_args(parser)
	args = parser.parse_command_line(None,parser)
	set_logging(args)
	logging.debug('debug mode')
	logging.info('info mode')
	logging.warn('warn mode')
	logging.error('error mode')
	logging.fatal('fatal mode')
	return

if __name__ == '__main__':
	main()