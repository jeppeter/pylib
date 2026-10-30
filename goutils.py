#! /usr/bin/env python


import extargsparse
import sys
import os
import logging
import re
import json
import subprocess
import traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from loglib import set_logging,load_log_commandline
from strop import parse_int
from fileop import read_file,write_file


def gojsonstruct_handler(args,parser):
	set_logging(args)
	ins = read_file(args.input)
	sarr = re.split('\n',ins)
	outs = ''
	mexpr = re.compile('^\\s+([A-Z].*)\\s+(.*)$')
	for l in sarr:
		l = l.rstrip('\r\n')
		m = mexpr.findall(l)
		if m is not None and len(m) >0:
			cname = m[0][0]
			cname = cname.lower()
			outs += '%s `json:"%s"`\n'%(l,cname)
		else:
			outs += '%s\n'%(l)
	write_file(outs,args.output)
	sys.exit(0)
	return

def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "directory|D" : null,
        "gojsonstruct<gojsonstruct_handler>##to format go json struct##" : {
        	"$" : 0
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    load_log_commandline(parser)
    parser.load_command_line_string(commandline)
    parser.parse_command_line(None,parser)
    raise Exception('can not here for no command handle')
    return


if __name__ == '__main__':
    main()