#! /usr/bin/env python

import extargsparse
import re
import sys
import logging

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

def write_file(s,outfile=None):
	fout = sys.stdout
	if outfile is not None:
		fout = open(outfile, 'w+b')
	outs = s
	if 'b' in fout.mode:
		outs = s.encode('utf-8')
	fout.write(outs)
	if fout != sys.stdout:
		fout.close()
	fout = None
	return 

def buffer_to_gascode(incode):
	outcode = ''
	sarr = re.split('\n', incode)
	for l in sarr:
		l = l.rstrip('\r\n')
		l = re.sub('^0x[0-9a-fA-F]+:', '', l)
		l = re.sub('[\s]{3,}.*$', '', l)
		nsarr = re.split('[\s]+', l)
		curs = '    .byte '
		incnt = 0

		for c in nsarr:
			if len(c) > 0:
				if incnt > 0:
					curs += ','
				curs += c
				incnt = incnt + 1
		outcode += '%s\n'%(curs)
	return outcode

def btg_handler(args,parser):
	set_logging(args)

	totals = ''
	if len(args.subnargs) > 0:
		for c in args.subnargs:
			totals += read_file(c)
	else:
		totals += read_file()
	logging.info('totals [%s]'%(totals))
	outcode = buffer_to_gascode(totals)
	write_file(outcode, args.output)
	sys.exit(0)
	return

def buffer_to_asmcode(incode):
	outcode = '    asm volatile('
	sarr = re.split('\n', incode)
	lcnt = 0
	for l in sarr:
		l = l.rstrip('\r\n')
		l = re.sub('^0x[0-9a-fA-F]+:', '', l)
		l = re.sub('[\s]{3,}.*$', '', l)
		nsarr = re.split('[\s]+', l)
		curs = '.byte '
		incnt = 0

		for c in nsarr:
			if len(c) > 0:
				if incnt > 0:
					curs += ','
				curs += c
				incnt = incnt + 1
		if incnt > 0:
			if lcnt > 0 :
				outcode += '        "%s\\n"\n'%(curs)
			else:
				outcode += '"%s\\n"\n'%(curs)
			lcnt = lcnt + 1
	outcode += '    );\n'
	return outcode


def bta_handler(args,parser):
	set_logging(args)

	totals = ''
	if len(args.subnargs) > 0:
		for c in args.subnargs:
			totals += read_file(c)
	else:
		totals += read_file()
	logging.info('totals [%s]'%(totals))
	outcode = buffer_to_asmcode(totals)
	write_file(outcode, args.output)
	sys.exit(0)
	return


def main():
	commandline='''
	{
		"verbose|v" : "+",
		"output|o" : null,
		"buffertogas<btg_handler>##[files]... to transcode to gas##" : {
			"$" : "*"
		},
		"buffertoasm<bta_handler>##[files]... to transcode to asm##" : {
			"$" : "*"
		}
	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser.parse_command_line(None,parser)
	raise Exception('can not parse command %s'%(sys.argv))
	return

if __name__ == '__main__':
	main()
