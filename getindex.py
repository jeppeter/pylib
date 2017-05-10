#! /usr/bin/env python

import tushare as ts
import extargsparse
import time
import sys

def getk_handler(args,parser):
	for s in args.subnargs:
		res = ts.get_k_data(s,ktype=args.ktype,autype=args.autype,index=args.indexmode,start=args.startdate,end=args.enddate)
		print('%s for %s %s:%s'%(s,args.ktype,args.startdate,args.enddate))
		print('%s'%(res))
	sys.exit(0)
	return

def geth_handler(args,parser):
	for s in args.subnargs:
		res = ts.get_h_data(s,start=args.startdate,end=args.enddate,autype=args.autype,pause=1,retry_count=3)


def main():
	commandline_fmt='''
	{
		"verbose|v" : "+",
		"autype|a" : "hfq",
		"indexmode|i" : false,
		"ktype|k" : "D",
		"startdate|S" : "%s",
		"enddate|E" : "%s",
		"getk<getk_handler>" : {
			"$" : "+"
		}
	}
	'''
	edate = time.strftime('%Y-%m-%d',time.gmtime())
	sdate = time.strftime('%Y-%m-%d',time.gmtime(time.time()-24*3600*365))
	commandline = commandline_fmt%(sdate,edate)
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser.parse_command_line(None,parser)
	raise Exception('can not get handle')
	return

if __name__ == '__main__':
	main()

