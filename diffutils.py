#! /usr/bin/env python

import extargsparse
import sys
import socket
import logging
import re
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from fileop import read_file,write_file
from loglib import load_log_commandline,set_logging
from strop import parse_int



def difftocp_handler(args,parser):
	set_logging(args)
	s = read_file(args.input)
	basedir = args.subnargs[0]
	basedir = basedir.rstrip('/')
	sarr = re.split('\n',s)
	filestartexpr = re.compile('^Files.*\\s%s/([^\\s]+)\\s+'%(basedir),re.I)
	onlyexpr = re.compile('^Only in\\s+%s/([^:]+):\\s+(.*)$'%(basedir),re.I)
	outs = ''
	for l in sarr:
		l = l.rstrip('\r')
		m = filestartexpr.findall(l)
		if m is not None and len(m) > 0 :
			outs += '%s\n'%(m[0])
			continue
		m = onlyexpr.findall(l)
		if m is not None and len(m) > 0 and len(m[0]) > 1:
			outs += '%s/%s\n'%(m[0][0],m[0][1])
			continue

	write_file(outs,args.output)
	sys.exit(0)
	return



def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "difftocp<difftocp_handler>##basedir to to transfer diff simple format to perl dircp.pl format##" : {
        	"$" : 1
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    load_log_commandline(parser)
    parser.parse_command_line(None,parser)
    raise Exception('can not reach here')
    return

if __name__ == '__main__':
    main()
