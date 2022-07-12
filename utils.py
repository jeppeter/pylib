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


def get_strval(v):
	base = 10
	iv = v
	if v.startswith('x') or v.startswith('X') :
		base= 16
		iv = v[1:]
	elif v.startswith('0x') or v.startswith('0X'):
		base = 16
		iv = v[2:]
	return int(iv,base)

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

def utf8touni_handler(args,parser):
	set_logging(args)
	outb = []
	inb = []
	for v in args.subnargs:
		inb.append(get_strval(v))
	idx = 0
	while idx < len(inb):
		if inb[idx] <= 0x7f:
			outb.append(inb[idx])
			idx += 1
		elif ((inb[idx] & 0xe0) == 0xc0)  :
			if (idx + 1) >= len(inb):
				raise Exception('%d out'%(idx))
			if inb[idx+1] & 0xc0 != 0x80:
				raise Exception('%d not valid 0b10'%(idx))
			cv1 = inb[idx] & 0x1f
			cv2 = inb[idx+1] & 0x3f
			tv = (cv1 << 6) | cv2
			outb.append((tv >> 8) & 0xff)
			outb.append((tv & 0xff))
			idx += 2
		elif ((inb[idx] & 0xf0) == 0xe0):
			if (idx + 2)  >= len(inb):
				raise Exception('%d out'%(idx))
			if inb[idx+1] & 0xc0 != 0x80 or inb[idx+2] & 0xc0 != 0x80:
				raise Exception('%d not valid 0b10'%(idx))
			cv1 = inb[idx] & 0xf
			cv2 = inb[idx+1] & 0x3f
			cv3 = inb[idx+2] & 0x3f
			tv = (cv1 << 12) | (cv2 << 6)  | cv3 
			outb.append((tv >> 8) & 0xff)
			outb.append((tv & 0xff))
			idx += 3
		elif ((inb[idx] & 0xf1) == 0xf0):
			if (idx + 3) >= len(inb):
				raise Exception('%d out'%(idx))
			if inb[idx+1] & 0xc0 != 0x80 or inb[idx+2] & 0xc0 != 0x80 or inb[idx+3] & 0xc0 != 0x80:
				raise Exception('%d not valid 0b10'%(idx))
			cv1 = inb[idx] & 0xf
			cv2 = inb[idx+1] & 0x3f
			cv3 = inb[idx+2] & 0x3f
			cv4 = inb[idx+3] & 0x3f
			tv = (cv1 << 18) | (cv2 << 12)  | (cv3  << 6) | cv4
			outb.append((tv >> 8) & 0xff)
			outb.append((tv & 0xff))
			idx += 4
		else:
			raise Exception('%d not valid'%(idx))
	idx = 0
	sys.stdout.write('trans out:')
	while idx < len(outb):
		if (idx % 16) == 0:
			sys.stdout.write('\n')
		if (idx % 16) != 0:
			sys.stdout.write(' ')
		sys.stdout.write('0x%x'%(outb[idx]))
		idx += 1
	sys.stdout.write('\n')
	sys.exit(0)
	return


def parse_int(v):
	c = v
	base = 10
	if c.startswith('0x') or c.startswith('0X') :
		base = 16
		c = c[2:]
	elif c.startswith('x') or c.startswith('X'):
		base = 16
		c = c[1:]
	return int(c,base)


def getval_handler(args,parser):
	set_logging(args)
	for s in args.subnargs:
		val = parse_int(s)
		exp = (val >> 11) & 0x1f
		base = (val & 0x3ff)
		sys.stdout.write('%s base[0x%x] exp[0x%x] [%d]\n'%(s,base,exp, (base << exp)))
	sys.exit(0)
	return

def pec_check(data,initval = 0):
	retcrc = initval
	for b in data:
		for _ in range(0,8):
			if (retcrc >> 7) ^ (b & 0x1):
				retcrc = ((retcrc << 1) ^0x07) & 0xff
			else:
				retcrc = (retcrc << 1) & 0xff
			b = b >> 1
	return retcrc

def peccheck_handler(args,parser):
	set_logging(args)
	data = []
	for s in args.subnargs:
		data.append(parse_int(s))
	crc = pec_check(data)
	sys.stdout.write('%s crc 0x%x\n'%(data,crc))
	sys.exit(0)
	return

def walt_handler(args,parser):
	set_logging(args)
	for s in args.subnargs:
		val = parse_int(s)
		highval = (val >> 11) & ((1 << 5) -1)
		exp = highval & 0xf
		leftshift = ((( highval >> 4 ) & 0x1) == 0x0)
		logging.info('highval 0x%x exp 0x%x'%(highval,exp))
		base = (val & ((1 << 11) - 1))
		if leftshift :
			walt = base * exp
		else:
			walt = int(base / exp)
		sys.stdout.write('%s walt [%d] [0x%x:0x%x] leftshift [%s]\n'%(s,walt,highval, base,leftshift))
	sys.exit(0)
	return


def bin_to_rustvec(args,ins):
	rets = 'vec!['
	retb = b''
	sarr = re.split('\n',ins)
	tidx = 0
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
				if tidx > 0 :
					rets += ','
				rets += '%s'%(c)
				tidx += 1
				if (tidx % 16) == 0 :
					rets += '\n'
	rets += ']'
	return rets

def bintorustvec_handler(args,parser):
	set_logging(args)
	logging.info('read [%s]'%(args.input))
	bins = read_file(args.input)
	s = bin_to_rustvec(args,bins)
	write_file(s,args.output)
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
		},
		"utf8touni<utf8touni_handler>## bytes... to change utf8 coding to unicode ##" : {
			"$" : "+"
		},
		"getval<getval_handler>##value ... to change value##" : {
			"$" : "+"
		},
		"peccheck<peccheck_handler>## byte ... to check##" : {
			"$" : "+"
		},
		"walt<walt_handler>## value ... to handle ##" : {
			"$" : "+"
		},
		"bintorustvec<bintorustvec_handler>##to change buffer out to rust vec##" : {
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