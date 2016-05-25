#!/usr/bin/python

import sys
import os
import logging
import argparse

dkeys = {
	'$' : {
		'type' : 'string',
		'value' : [3,2],
		'help' : ' add1 add2'
	},
	'cc|c' :  [],
	'port|d' : 'cc',
	'ccsss' : 99.9,
	'csse' : {
		'ccs|c' : [99.1,99.2]
	}
}

class _GetType(object):
	def __init__(self,v):
		self.__type = type(v)
		if isinstance(v,str):
			self.__type = 'string'
		elif isinstance(v,dict):
			self.__type = 'dict'
		elif isinstance(v,list):
			self.__type = 'list'
		elif isinstance(v,bool):
			self.__type = 'bool'
		elif isinstance (v,int):
			self.__type = 'int'
		elif isinstance(v ,float):
			self.__type = 'float'
		else:
			raise Exception('(%s)unknown type (%s)'%(v,type(v)))
		return

	def get_type(self):
		return self.__type

	def __str__(self):
		return self.__type




class ClassChoice:
	def __string(self,k,v):
		print('(%s) string (%s)'%(k,v))
		return

	def __int(self,k,v):
		print('(%s) int (%d)'%(k,v))
		return

	def __float(self,k,v):
		print('(%s) float (%f)'%(k,v))
		return

	def __list(self,k,v):
		print('(%s) list (%s)'%(k,v))
		return

	def __dict(self,k,v):
		print('(%s) dict (%s)'%(k,v))
		return


	def __init__(self):
		self.__mapfunc = {
			'string' : self.__string,
			'int' : self.__int,
			'float' : self.__float,
			'list' : self.__list,
			'dict' : self.__dict
		}
		return

	def test_dkeys(self,d):
		for k in d.keys():
			tpcls = _GetType(d[k])
			self.__mapfunc[str(tpcls)](k,d[k])
		return


def main():
	usage_str='%s [options] {commands} pkgs...'%(sys.argv[0])
	parser = argparse.ArgumentParser(description='dpkg encapsulation',usage=usage_str)
	sub_parser = parser.add_subparsers(help='',dest='command')
	dep_parser = sub_parser.add_parser('dep',help='get depends')
	dep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get depend')
	rdep_parser = sub_parser.add_parser('rdep',help='get rdepends')
	rdep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get rdepend')
	tree_parser = sub_parser.add_parser('tree',help='get dep from tree files')
	tree_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='files parse dep tree')
	tree_parser.add_argument('--list',dest='listpkg',action='store',default=None,help='specified the list pkg')
	inst_parser = sub_parser.add_parser('inst',help='get installed')
	all_parser = sub_parser.add_parser('all',help='get all available')
	args = parser.parse_args()
	args.newcommand = 'hello'
	for p in vars(args):
		print ('%s %s'%(p,getattr(args,p)))
	choice = ClassChoice()
	choice.test_dkeys(dkeys)
	return

if __name__ == '__main__':
	main()