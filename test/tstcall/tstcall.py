#!/usr/bin/python

import os
import sys
import re
import logging
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import cclass.bclass.dclass as dclass
import importlib

def call_func(funcname,args):
	mname = '__main__'
	fname = funcname
	try:
		if '.' not in funcname:
			m = __import__(mname)
		else:
			sarr = re.split('\.',funcname)
			mname = '.'.join(sarr[:-1])
			fname = sarr[-1]
			m = importlib.import_module(mname)
	except ImportError as e:
		logging.error('can not load %s'%(mname))
		return args

	for d in dir(m):
		if d == fname:
			val = getattr(m,d)
			if hasattr(val,'__call__'):
				val(args)
				return args
	logging.warn('can not call %s'%(funcname))
	return args


def main():
	for a in sys.argv[1:]:
		call_func(a,'call by')
	return

if __name__ == '__main__':
	main()