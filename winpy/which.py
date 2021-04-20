#! /usr/bin/env python

import extargsparse
import sys
import os
import logging
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
    if logging.root is not None and logging.root.handlers is not None and len(logging.root.handlers) > 0:
    	logging.root.handlers = []
    logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
    return


def which(exename):
	retval = ''
	paths = os.environ['PATH']
	sarr = re.split(';',paths)
	logging.info('sarr %s'%(sarr))
	for curp in sarr:
		curf = os.path.join(curp,exename)
		if os.path.exists(curf) and os.path.isfile(curf) :
			retval = curf
			break
		curf = os.path.join(curp,'%s.exe'%(exename))
		if os.path.exists(curf) and os.path.isfile(curf) :
			retval = curf
			break		
	return retval

def main():
	commandline='''
	{
		"verbose|v" : "+"
	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	args = parser.parse_command_line(None,parser)
	set_log_level(args)
	for c in args.args:
		r = which(c)
		if len(r) > 0 :
			sys.stdout.write('%s\n'%(r))
	return

if __name__ == '__main__':
	main()
