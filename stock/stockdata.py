#! /usr/bin/env python

import logging
import extargsparse
import requests
import os
import sys


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
		return rsp.content
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


def lrb_handler(args,parser):
	set_log_level(args)
	for c in args.subnargs:
		url = 'http://quotes.money.163.com/service/lrb_%s.html'%(c)
		if args.byyear:
			url += '?type=year'
		output = get_stock_outfile(args,url)
		logging.info('get [%s]\n%s'%(c,output))
		write_file(output, os.path.join(args.path, 'lrb_%s.cvs'%(c)))

	return


def main():
	commandline_fmt='''
	{
		"verbose|v" : "+",
		"byyear|Y" : true,
		"path|P" : "%s",
		"lrb<lrb_handler>##to get profit datasheet##" : {
			"$" : "+"
		}
	}
	'''
	commandline= commandline_fmt%(os.getcwd())
	parser =extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser.parse_command_line(None,parser)
	return

if __name__ =='__main__':
	main()