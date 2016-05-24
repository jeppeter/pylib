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

def add_tce_args(parser):
	parser.add_argument('-v','--verbose',default=0,action='count')
	parser.add_argument('-r','--root',dest='%sroot'%(tcebasic.CONST.KEYWORD),default=None,action='store',help='root of dpkg specified default (%s)'%(getattr(tcebasic.CONST,'%sroot'%(tcebasic.CONST.KEYWORD)).upper()))
	parser.add_argument('-M','--mirror',dest='%smirror'%(tcebasic.CONST.KEYWORD),default=None,action='store',help='mirror site specify default (%s)'%(getattr(tcebasic.CONST,'%smirro'%(tcebasic.CONST.KEYWORD)).upper()))
	parser.add_argument('-c','--cat',dest='%scat'%(tcebasic.CONST.KEYWORD),default=None,action='store',help='cat specified default(%s)'%(getattr(tcebasic.CONST,'%scat'%(tcebasic.CONST.KEYWORD)).upper()))
	parser.add_argument('-C','--chroot',dest='%schroot'%(tcebasic.CONST.KEYWORD),default=None,action='store',help='chroot specified default (%s)'%(getattr(tcebasic.CONST,'%schroot'%(tcebasic.CONST.KEYWORD)).upper()))
	parser.add_argument('-t','--try',dest='%strymode'%(tcebasic.CONST.KEYWORD),default=None,action='store_true',help='try mode default (%s)'%(getattr(tcebasic.CONST,'%strymode'%(tcebasic.CONST.KEYWORD)).upper()))
	parser.add_argument('-m','--mount',dest='%smount'%(tcebasic.CONST.KEYWORD),default=None,action='store',help='mount specified default (%s)'%(getattr(tcebasic.CONST,'%smount'%(tcebasic.CONST.KEYWORD)).upper()))
	parser.add_argument('-u','--umount',dest='%sumount'%(tcebasic.CONST.KEYWORD),default=None,action='store',help='umount specified default (%s)'%(getattr(tcebasic.CONST,'%sumount'%(tcebasic.CONST.KEYWORD)).upper()))
	parser.add_argument('--chown',dest='%schown'%(tcebasic.CONST.KEYWORD),default=None,action='store',help='chown specified default (%s)'%(getattr(tcebasic.CONST,'%schown'%(tcebasic.CONST.KEYWORD)).upper()))
	parser.add_argument('--chmod',dest='%schmod'%(tcebasic.CONST.KEYWORD),default=None,action='store',help='chmod specified default (%s)'%(getattr(tcebasic.CONST,'%schmod'%(tcebasic.CONST.KEYWORD)).upper()))
	parser.add_argument('-j','--json',dest='%sjsonfile'%(tcebasic.CONST.KEYWORD),default=None,action='store',help='to make json file as input args default(%s)'%(getattr(tcebasic.CONST,'%sjsonfile'%(tcebasic.CONST.KEYWORD)).upper()))
	return parser


def load_tce_jsonfile(args):
	if args.tce_jsonfile is None:
		# now we should get all the default
		for p in dir(tcebasic.CONST):
			if p.startswith('TCE_'):
				if getattr(args,p.lower()) is None:
					setattr(args,p.lower(),getattr(tcebasic.CONST,p))
		return

	# it will parse the files
	keywords = []
	for p in dir(tcebasic.CONST):
		if p.lower().startswith(tcebasic.CONST.KEYWORD):
			curkey = p.lower().replace(tcebasic.CONST.KEYWORD,'')
			if curkey not in keywords:
				keywords.append(curkey)
	with open(args.tce_jsonfile,'r') as f:
		tcejson = json.load(f)
		for p in dir(tcejson):
			if p in keywords:
				if getattr(args,p) is None:
					setattr(args,p,getattr(tcebasic.CONST,p.upper()))
	return args

def debug_args(args):
	for p in dir(args):
		if p.startswith(tcebasic.CONST.KEYWORD):
			print('%s = %s'%(p,getattr(args,p)))
	return


def main():
	parser = argparse.ArgumentParser(description='tce encapsulation',usage='%s [options] {commands} pkgs...'%(sys.argv[0]))	
	add_tce_args(parser)
	sub_parser = parser.add_subparsers(help='',dest='command')
	dep_parser = sub_parser.add_parser('dep',help='get depends')
	dep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get depend')
	rdep_parser = sub_parser.add_parser('rdep',help='get rdepends')
	rdep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get rdepend')
	inst_parser = sub_parser.add_parser('inst',help='get installed')
	all_parser = sub_parser.add_parser('all',help='get all available')
	args = parser.parse_args()	
	args = load_tce_jsonfile(args)
	debug_args(args)
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return

if __name__ =='__main__':
	main()
