#! /usr/bin/env python

import extargsparse
import logging
import cmdpack
import sys
import re


def set_log_level(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	elif args.verbose >= 1 :
		loglvl = logging.WARN
	# we delete old handlers ,and set new handler
	if logging.root and logging.root.handlers and len(logging.root.handlers) > 0 :
		logging.root.handlers = []
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return

def list_one_packet(args,pkgname):
	depexpr = re.compile('\s+Depends:')
	preferexpr = re.compile('\s+Recommends:')
	deps = []
	for l in cmdpack.run_cmd_output(['dpkg','-I',pkgname]):
		l = l.rstrip('\r\n')
		if depexpr.match(l):
			sarr = re.split(':',l,1)
			if len(sarr) > 1:
				logging.info('sarr [%d] [%s]'%(len(sarr),sarr[1]))
				sarr = re.split(',', sarr[1])
				for p in sarr:
					sa = re.split('\s+',p)
					logging.info('sa %s'%(sa))
					deps.append(sa[1])
		elif preferexpr.match(l):
			sarr = re.split(':',l,1)
			if len(sarr) > 1:
				logging.info('sarr [%d] [%s]'%(len(sarr),sarr[1]))
				sarr = re.split(',',sarr[1])
				for p in sarr:
					sa = re.split('\s+',p)
					logging.info('sa %s'%(sa))
					deps.append(sa[1])
	return  sorted(deps)

def listdep_handler(args,parser):
	set_log_level(args)
	deps = dict()
	for c in args.subnargs:
		deps[c] = list_one_packet(args,c)
	for k in deps.keys():
		sys.stdout.write('DPKG:%s\n'%(k))
		for c in deps[k]:
			sys.stdout.write('%s\n'%(c))
	sys.exit(0)
	return

def main():
	commandline='''
	{
		"verbose|v" : "+",
		"listdep<listdep_handler>##debname ... to list dep##" : {
			"$" : "+"
		}
	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser.parse_command_line(None,parser)
	return

if __name__== '__main__':
	main()
