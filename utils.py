#! /usr/bin/env python

import extargsparse
import sys
import os
import logging
import re
import shutil
import logging.handlers
import time


def set_logging(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	curlog = logging.getLogger(args.lognames)
	#sys.stderr.write('curlog [%s][%s]\n'%(args.logname,curlog))
	curlog.setLevel(loglvl)
	if len(curlog.handlers) > 0 :
		curlog.handlers = []
	formatter = logging.Formatter('%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d<%(levelname)s>\t%(message)s')
	if not args.lognostderr:
		logstderr = logging.StreamHandler()
		logstderr.setLevel(loglvl)
		logstderr.setFormatter(formatter)
		curlog.addHandler(logstderr)

	for f in args.logfiles:
		flog = logging.FileHandler(f,mode='w',delay=False)
		flog.setLevel(loglvl)
		flog.setFormatter(formatter)
		curlog.addHandler(flog)
	for f in args.logappends:		
		if args.logrotate:
			flog = logging.handlers.RotatingFileHandler(f,mode='a',maxBytes=args.logmaxbytes,backupCount=args.logbackupcnt,delay=0)
		else:
			sys.stdout.write('appends [%s] file\n'%(f))
			flog = logging.FileHandler(f,mode='a',delay=0)
		flog.setLevel(loglvl)
		flog.setFormatter(formatter)
		curlog.addHandler(flog)
	return

def load_log_commandline(parser):
	logcommand = '''
	{
		"verbose|v" : "+",
		"logname" : "root",
		"logfiles" : [],
		"logappends" : [],
		"logrotate" : true,
		"logmaxbytes" : 10000000,
		"logbackupcnt" : 2,
		"lognostderr" : false
	}
	'''
	parser.load_command_line_string(logcommand)
	return parser


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

def bin_to_string(args,ins):
	rets = ''
	retb = b''
	sarr = re.split('\n',ins)
	for s in sarr:
		s = s.rstrip('\r\n')
		ns = re.sub('^\\[0x[a-fA-F0-9]+\\][:]?\\s+','',s)
		if ns == s:
			ns = re.sub('^0x[a-fA-F0-9]+[:]?\\s+','',s)
		s = ns
		logging.info('s [%s]'%(s))
		cursarr = re.split('\\s+',s)
		for c in cursarr:
			if c.startswith('0x') or c.startswith('0X'):
				retb += bytes([int(c[2:],16)])
	if args.utf8mode:
		rets = retb.decode('utf-8')
	else:
		rets = retb.decode('ascii')
	return rets

def bintostr_handler(args,parser):
	set_logging(args)
	for f in args.subnargs:
		logging.info('read [%s]'%(f))
		bins = read_file(f)
		s = bin_to_string(args,bins)
		write_file(s,args.output)

	sys.exit(0)
	return


def testlog_handler(args,parser):
	set_logging(args)
	timeval = 10
	if len(args.subnargs) > 0:
		timeval = int(args.subnargs[0])
	for i in range(timeval):
		logging.info('[%d] value'%(i))
		logging.fatal('[%d] value'%(i))
		logging.error('[%d] value'%(i))
		logging.debug('[%d] value'%(i))
		if sys.version[0] == '3':
			logging.warning('[%d] value'%(i))
		else:
			logging.warn('[%d] value'%(i))
	sys.exit(0)
	return

def testout_handler(args,parser):
	set_logging(args)
	timeval = 1.0
	if len(args.subnargs) > 0:
		timeval = float(args.subnargs[0])
	for l in sys.stdin:
		sys.stdout.write('%s'%(l))
		sys.stderr.write('%s'%(l))
		time.sleep(timeval)
	sys.stdout.flush()
	sys.stderr.flush()
	time.sleep(timeval)
	sys.exit(0)
	return


def main():
	commandline='''
	{
		"input|i" : null,
		"utf8mode|U" : false,
		"output|o" : null,
		"xcopy<xcopy_handler>## dstd [srcd] to copy file from input from srcd to dstd srcd default .##" : {
			"$" : "+"
		},
		"bintostr<bintostr_handler>## inputfile to dump bin to string##" : {
			"$" : "+"
		},
		"testlog<testlog_handler>## time ##" : {
			"$" : "?"
		},
		"testout<testout_handler>##timesleep to sleep for a single line from read stdin default 1.0##" : {
			"$" : "?"
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