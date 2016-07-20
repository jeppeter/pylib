#!/usr/bin/python

import re
import sys
import extargsparse
import logging

def set_logging(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return

def match(args,ctx):
	set_logging(args)
	restr = args.subnargs[0]
	instr = args.subnargs[1]
	expr = re.compile(restr)	
	if expr.match(instr):
		print ('(%s) match (%s)'%(instr,restr))
	else:
		print ('(%s) not match (%s)'%(instr,restr))
	sys.exit(0)
	return

def findall(args,ctx):
	set_logging(args)
	restr = args.subnargs[0]
	instr = args.subnargs[1]
	expr = re.compile(restr)
	m =  expr.findall(instr)
	if m :
		s = '(%s) match (%s)\n'%(instr,restr)
		for i in range(len(m)):
			s += '\t[%d] %s\n'%(i,m[i])
		print ('%s'%(s))
	else:
		print ('(%s) no more for (%s)'%(instr,restr))
	sys.exit(0)
	return

def filefindall(args,ctx):
	restr = args.subnargs[0]
	expr = re.compile(restr)
	fin = sys.stdin
	fout = sys.stdout
	if args.infile is not None:
		fin = open(args.infile,'r')
	if args.outfile is not None:
		fout = open(args.outfile,'w')
	cnt = 1
	for l in fin:
		l = l.rstrip('\r\n')
		m = expr.findall(l)
		if m :
			fout.write('[%d]'%(cnt))
			for i in range(len(m)):
				fout.write('\t[%d] %s'%(i,m[i]))
			fout.write('\n')
		cnt += 1
	sys.exit(0)
	return

def imatch(args,ctx):
	set_logging(args)
	restr = args.subnargs[0]
	instr = args.subnargs[1]
	expr = re.compile(restr,re.I)
	if expr.match(instr):
		print ('(%s) ignore match (%s)'%(instr,restr))
	else:
		print ('(%s) not ignore match (%s)'%(instr,restr))
	sys.exit(0)
	return

def ifindall(args,ctx):
	set_logging(args)
	restr = args.subnargs[0]
	instr = args.subnargs[1]
	expr = re.compile(restr,re.I)
	m =  expr.findall(instr)
	if m :
		s = '(%s) match (%s)\n'%(instr,restr)
		for i in range(len(m)):
			s += '\t[%d] (%s)\n'%(i,m[i])			
		print ('%s'%(s))
	else:
		print ('(%s) no more for (%s)'%(instr,restr))
	sys.exit(0)
	return

def sub(args,ctx):
	set_logging(args)
	if len(args.subnargs) < 2:
		Usage(3,'sub restr instr [replstr]',ctx)
	if len(args.subnargs) < 3:
		restr = args.subnargs[0]
		instr = args.subnargs[1]
		replstr = ''
	else:
		restr = args.subnargs[0]
		instr = args.subnargs[1]
		replstr = args.subnargs[2]
	newstr = re.sub(restr,replstr,instr)
	print('(%s) sub(%s)(%s) => (%s)'%(instr,restr,replstr,newstr))
	sys.exit(0)
	return

def split(args,ctx):
	set_logging(args)
	restr = args.subnargs[0]
	instr = args.subnargs[1]
	sarr = re.split(restr,instr)
	for i in range(len(sarr)):
		print('[%d] (%s)'%(i,sarr[i]))
	sys.exit(0)
	return

def Usage(ec,fmt,parser):
	fp = sys.stderr
	if ec == 0 :
		fp = sys.stdout

	if len(fmt) > 0:
		fp.write('%s\n'%(fmt))
	parser.print_help(fp)
	sys.exit(ec)



command = {
	'verbose|v' : '+',
	'infile|i' : None,
	'outfile|o' : None,
	'match<match>##call re.match func##' : {
		'$' : 2
	},
	'imatch<imatch>##call re.match with re.I##' : {
		'$' : 2
	},
	'findall<findall>##re.findall##' : {
		'$' : 2
	},
	'ifindall<ifindall>##re.findall with re.I##' : {
		'$' : 2
	},
	'sub<sub>##re.sub##' : {
		'$' : '+'
	},
	'split<split>##re.split##' : {
		'$' : 2
	},
	'filefindall<filefindall>##re.findall in file##' : {
		'$' : 1
	}
}

def main():
	global command
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line(command)
	parser.parse_command_line()
	return


if __name__ == '__main__':
	main()