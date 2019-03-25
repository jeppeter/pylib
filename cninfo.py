#! /usr/bin/env python

import extargsparse
import requests
import logging

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


def limit_handler(args,parser):
	set_log_level(args)
	for a in args.subnargs:
		typeex = 'szse'
		if a.startswith('6'):
			typeex = 'sse'
		url = 'http://www.cninfo.com.cn/new/singleDisclosure/fulltext?stock=%s&pageSize=20&pageNum=1&tabname=latest&plate=%s&limit='%(a,typeex)
		logging.info('url [%s]'%(url))
		r = requests.post(url)
		print('r %s'%(r.text))
	return

def query_handler(args,parser):
	set_log_level(args)
	pagenum=1
	chkcode=None
	stockcode = None
	if len(args.subnargs) > 0:
		stockcode = args.subnargs[0]
	if len(args.subnargs) > 1:
		chkcode = args.subnargs[1]

	if len(args.subnargs) > 2:
		pagenum = args.subnargs[2]

	typeex = 'szse'
	if stockcode.startswith('6'):
		typeex='sse'

	url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
	postdata = 'pageNum=%s&pageSize=30&tabName=fulltext&column=%s&stock=%s%%2C%s&searchkey=&secid=&plate=sz&category=&seDate=2000-01-01+~+2019-03-25'%(pagenum,typeex,stockcode,chkcode)
	logging.info('postdata [%s]'%(postdata))
	r = requests.post(url,data=postdata,headers={'Content-Type' : 'application/x-www-form-urlencoded'})
	print('r %s'%(r.text))

	return

def main():
	commandline='''
	{
		"verbose|v" : "+",
		"limit<limit_handler>" : {
			"$" : "+"
		},
		"query<query_handler>##stockcode chkcode [pagenum]##" : {
			"$" : "+"
		}
	}
	'''
	parser= extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser.parse_command_line(None,parser)
	return


if __name__ == '__main__':
	main()