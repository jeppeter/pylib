#! /usr/bin/env python

import extargsparse
import sys
import os
import logging
import re
import shutil


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



def read_file(infile=None):
	fin = sys.stdin
	if infile is not None:
		fin = open(infile,'r+b')
	rets = ''
	for l in fin:
		s = l
		if 'b' in fin.mode:
			if sys.version[0] == '3':
				s = l.decode('utf-8')
		rets += s

	if fin != sys.stdin:
		fin.close()
	fin = None
	return rets

def makedir_safe(d):
	if os.path.isdir(d):
		return
	os.makedirs(d)
	return

def xcopy_handler(args,parser):
	set_logging(args)
	s = read_file(args.input)
	destd = args.subnargs[0]
	srcd = os.getcwd()
	if len(args.subnargs) > 1:
		srcd = args.subnargs[1]
	sarr = re.split('\n',s)
	for l in sarr:
		l = l.rstrip('\r\n')
		srcf = os.path.join(srcd,l)
		dstf = os.path.join(destd,l)
		logging.info('[%s] => [%s]'%(srcf,dstf))
		dstd = os.path.dirname(dstf)
		makedir_safe(dstd)
		if os.path.isfile(srcf):
			shutil.copyfile(srcf,dstf)
		elif os.path.isdir(srcf):
			makedir_safe(dstf)
		else:
			logging.error('%s not valid type'%(srcf))
	sys.exit(0)
	return


def main():
	commandline='''
	{
		"verbose|v" : "+",
		"input|i" : null,
		"xcopy<xcopy_handler>## dstd [srcd] to copy file from input from srcd to dstd srcd default .##" : {
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