#! /usr/bin/env python

import extargsparse
import tushare
import logging
import sys
import os
import re
import time
import math


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


def get_token(args):
	if args.tokentype.startswith('env:'):
		sarr = re.split(':',args.tokentype)
		return os.environ[sarr[1]]
	elif args.tokentype.startswith('file:'):
		sarr = re.split(':',args.tokentype)
		s = read_file(sarr[1])
		s = s.rstrip('\r\n')
		return s
	elif args.tokentype == 'stdin':
		if sys.version[0] == '3':
			s = input('token:')
		else:
			s = raw_input('token:')
		return s
	elif args.tokentype.startswith('var:'):
		sarr = re.split(':',args.tokentype)
		return sarr[1]
	raise Exception('not support token type %s'%(args.tokentype))

def output_file(s,outf=sys.stdout):	
	if 'b' in outf.mode  and sys.version[0] == '3':
		s = s.encode('utf-8')
	outf.write(s)
	return

def getlist_handler(args,parser):
	set_log_level(args)
	tok = get_token(args)
	logging.info('token %s'%(tok))
	sys.stdout.write('version %s\n'%(tushare.__version__))
	tushare.set_token(tok)
	pro = tushare.pro_api()
	data = pro.query('stock_basic',fields='ts_code,symbol,name,list_date')
	outf = sys.stdout
	if args.output is not None:
		outf = open(args.output,'wb')
	for idx,row in data.iterrows():
		output_file('%s %s %s\n'%(row['symbol'],row['name'], row['list_date']),outf)
	if outf != sys.stdout:
		outf.close()
	outf=None
	return

def get_ts_code(code):
	if code.startswith('6'):
		return '%s.SH'%(code)
	return '%s.SZ'%(code)

def get_ts_adjcode(prots,args,code):
	return prots.query('adj_factor',ts_code=get_ts_code(code),state_date=args.startdate,end_date=args.enddate)

EPISILON=0.001

def getadj_handler(args,parser):
	set_log_level(args)
	tok = get_token(args)
	tushare.set_token(tok)
	pro = tushare.pro_api()
	for c in args.subnargs:
		df = get_ts_adjcode(pro,args,c)
		lastf = 0.0
		for i, row in df.iterrows():
			curf = float(row['adj_factor'])
			if abs(curf - lastf)  > EPISILON:
				output_file('%s %s %s %s\n'%(i,row['ts_code'],row['trade_date'],curf))
			lastf = curf
	return

def main():
	commandline_fmt = '''
	{
		"verbose|v" : "+",
		"tokentype|T##token to set , type can be stdin|env|file|var default(env:TOKEN)##" : "env:TOKEN",
		"output|o" : null,
		"startdate|S" : "20000101",
		"enddate|E" : "%s",
		"getlist<getlist_handler>##get all list##" : {
			"$" : 0
		},
		"getadj<getadj_handler>" : {
			"$" : "+"
		}
	}
	'''
	curd = time.localtime()
	curdate = '%04d%02d%02d'%(curd.tm_year,curd.tm_mon,curd.tm_mday)
	commandline = commandline_fmt%(curdate)
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser.parse_command_line(None,parser)
	return

if __name__ == '__main__':
	main()