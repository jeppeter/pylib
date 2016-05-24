#!/usr/bin/python

################################################
##  this file is for tce handle in python module
##
################################################
import re
import os
import sys
import argparse
import logging
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import dbgexp
import cmdpack
import tcebasic


def Usage(ec,fmt,parser):
	fp = sys.stderr
	if ec == 0 :
		fp = sys.stdout

	if len(fmt) > 0:
		fp.write('%s\n'%(fmt))
	parser.print_help(fp)
	sys.exit(ec)


def debug_args(args):
	for p in dir(args):
		if p.startswith(tcebasic.CONST.KEYWORD):
			print('%s = %s'%(p,getattr(args,p)))
	return


def main():
	parser = argparse.ArgumentParser(description='tce encapsulation',usage='%s [options] {commands} pkgs...'%(sys.argv[0]))	
	tcebasic.add_tce_args(parser)
	args = parser.parse_args()	
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	args = tcebasic.load_tce_jsonfile(args)
	debug_args(args)
	return

if __name__ =='__main__':
	main()
