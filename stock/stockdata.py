#! /usr/bin/env python

import logging
import extargsparse
import requests
import os
import sys
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




def get_stock_outfile(args,url):
	try:
		rsp = requests.get(url)
		outs = rsp.content
		if sys.version[0] == '3':
			logging.info('outs %s'%(repr(outs)))
			outs = outs.decode('GBK')
		if len(outs) == 0:
			logging.error('get %s error'%(url))
		return outs
	except:
		return ''

def write_file(s,outfile=None):
	fout = sys.stdout
	if outfile is not None:
		fout = open(outfile, 'w+b')
	outs = s
	if 'b' in fout.mode and sys.version[0] == '3':
		outs = s.encode('utf-8')
	fout.write(outs)
	if fout != sys.stdout:
		fout.close()
	fout = None
	return 

def make_dir_safe(dpath):
	if os.path.isdir(dpath):
		return
	os.makedirs(dpath)
	if not os.path.isdir(dpath):
		raise Exception('can not make [%s]'%(dpath))
	return

def get_datasheet_single(args,stockcode,prefix):
	retval = False
	url = 'http://quotes.money.163.com/service/%s_%s.html'%(prefix,stockcode)
	if args.byyear:
		url += '?type=year'
	output = get_stock_outfile(args,url)
	if len(output) > 0:
		logging.info('get %s [%s]\n%s'%(prefix,stockcode,output))	
		write_file(output, os.path.join(args.path, '%s_%s.cvs'%(prefix,stockcode)))
		retval = True
	return retval

def parse_stockcode(args,code):
	retcode=[]

	if '-' in code:
		sarr = re.split('\-',code)
		if len(sarr) > 1:
			fromcode = int(sarr[0])
			tocode = int(sarr[1])
			idx = fromcode
			while idx <= tocode:
				retcode.append('%s'%(idx))
				idx += 1
		else:
			retcode.append(code)
	elif '*' in code:
		sarr = re.split('\*', code)
		fromc = sarr[0]
		toc = sarr[0]
		logging.info('sarr %s'%(sarr))
		while len(fromc) < 6:
			fromc += '0'
			toc += '9'
		fromcode = int(fromc)	
		tocode = int(toc)
		idx = fromcode
		logging.info('fromcode %s tocode %s'%(fromcode,tocode))
		while idx <= tocode:
			logging.info('idx %s'%(idx))
			retcode.append('%06d'%(idx))
			idx += 1
	else:
		retcode.append(code)
	return retcode


def get_datasheet(args,prefix):
	if not args.complex:
		for c in args.subnargs:
			get_datasheet_single(args,c,prefix)
	else:
		cnt = 0
		for c in args.subnargs:
			retcode = parse_stockcode(args,c)
			for cc in retcode:
				retval = get_datasheet_single(args,cc,prefix)
				if retval :
					cnt += 1
				else:
					logging.error('get %s [%s] error'%(prefix,cc))
		sys.stdout.write('write %s [%s]\n'%(prefix,cnt))

	return


def lrb_handler(args,parser):
	set_log_level(args)
	make_dir_safe(args.path)
	get_datasheet(args,'lrb')
	return

def zcfzb_handler(args,parser):
	set_log_level(args)
	make_dir_safe(args.path)
	get_datasheet(args,'zcfzb')
	return

def xjllb_handler(args,parser):
	set_log_level(args)
	make_dir_safe(args.path)
	get_datasheet(args,'xjllb')
	return

def main():
	commandline_fmt='''
	{
		"verbose|v" : "+",
		"byyear|Y" : true,
		"path|P" : "%s",
		"complex|C" : false,
		"lrb<lrb_handler>##to get profit datasheet##" : {
			"$" : "+"
		},
		"zcfzb<zcfzb_handler>##to get the pocession datasheet##" : {
			"$" : "+"
		},
		"xjllb<xjllb_handler>##to get cash flow datasheet##" : {
			"$" : "+"
		}
	}
	'''
	curpwd = os.getcwd()
	curpwd = curpwd.replace('\\','\\\\')
	commandline= commandline_fmt%(curpwd)
	parser =extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser.parse_command_line(None,parser)
	return

if __name__ =='__main__':
	main()