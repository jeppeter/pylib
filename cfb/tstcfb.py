#! /usr/bin/env python


import os
import sys
import extargsparse
import logging
import re

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import aes
from loglib import set_logging,load_log_commandline
from strop  import parse_int,dump_ints
from fileop import read_file,write_file

def cfb1_shift(invals):
	oval = []
	idx = 0
	while idx < len(invals):
		nidx = int(idx / 8)
		nshift = idx % 8
		dval = parse_int(invals[idx])
		if len(oval) <= nidx:
			oval.append(0)
		oval[nidx] = ((oval[nidx] & ((~(1 << (7 - nshift))) & 0xff)) | ((dval & 0x80) >> nshift))
		logging.info('oval[%d] = 0x%02x nshift %d'%(nidx,oval[nidx],nshift))
		idx += 1
	return oval

def read_inputvals(infile):
	invals = []
	s = read_file(infile)
	sarr = re.split('\r',s)
	for l in sarr:
		l = l.rstrip('\r')
		if l.startswith('#'):
			continue
		if len(l) == 0:
			continue
		carr = re.split('\\s+',l)
		for i in carr:
			invals.append(parse_int(i))
	return invals

def cfb1shift_handle(args,parser):
	set_logging(args)
	if len(args.subnargs) > 0:
		oval = cfb1_shift(args.subnargs)
	else:
		oval = cfb1_shift(read_inputvals(args.input))
	sys.stdout.write('%s\n'%(dump_ints(oval)))
	sys.exit(0)
	return

def filtercfb1bits_handler(args,parser):
	set_logging(args)
	s = read_file(args.input)
	sarr = re.split('\n',s)
	expr = re.compile('<DEBUG>\\s+out\\s+(0x[0-9a-fA-F]+)\\s*$')
	oval = []
	for l in sarr:
		l = l.rstrip('\r')
		m = expr.findall(l)
		if m is not None and len(m) > 0:
			oval.append(parse_int(m[0]))
	idx = 0
	while idx < len(oval):
		sys.stdout.write(' 0x%02x'%(oval[idx]))
		idx += 1
	sys.stdout.write('\n')
	sys.exit(0)
	return

def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "cfb1shift<cfb1shift_handle>##to give rand bytes##" : {
            "$" : "+"
        },
        "filtercfb1bits<filtercfb1bits_handler>##to filter bits value##" : {
        	"$" : 0
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
