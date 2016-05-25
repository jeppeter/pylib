#!/usr/bin/python

import argparse
import os
import sys
import json
import logging
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import __key__ as keyparse


class ExtArgsParse(argparse.ArgumentParser):
	def __init__(self,prog=None,usage=None,description=None,epilog=None,
                 parents=[],formatter_class=argparse.HelpFormatter,prefix_chars='-',
                 fromfile_prefix_chars=None,argument_default=None,
                 conflict_handler='error',add_help=True):
		super(ExtArgsParse,self).__init__(prog,usage,description,epilog,parents,formatter_class,
			   prefix_chars,fromfile_prefix_chars,argument_default,conflict_handler,add_help)
		return

	def load_command_line(self,d):
		if not isinstance(d,dict):
			raise Exception('input parameter(%s) not dict'%(d))


	def load_command_line_string(self,s):
		try:
			d = json.loads(s)
		except:
			raise Exception('(%s) not valid json string'%(s))
		self.load_command_line(d)
		return
	def add_args_dict(self,prefix,d,dhelp=None):
		if not isinstance(d,dict):
			raise Exception('%s not dict'%(d))
		for k in d.keys():
			helpinfo = '%s sepecified default(%s)'%(k,d[k])
			if dhelp is not None and k in dhelp.keys():
				helpinfo = dhelp[k]
			if isinstance(d[k],bool):
				if d[k] :
					self.add_argument('--%s'%(k),dest='%s%s'%(prefix,k),default=None,action='store_false',help=helpinfo)
				else:
					self.add_argument('--%s'%(k),dest='%s%s'%(prefix,k),default=None,action='store_true',help=helpinfo)
			elif isinstance(d[k],str):
				self.add_argument('--%s'%(k),dest='%s%s'%(prefix,k),default=None,action='store',help=helpinfo)
			elif isinstance(d[k],int):
				self.add_argument('--%s'%(k),dest='%s%s'%(prefix,k),default=None,help=helpinfo,action=IntAction)
			elif isinstance(d[k],list):
				self.add_argument('--%s'%(k),dest='%s%s'%(prefix,k),default=None,help=helpinfo,action=ArrayAction)
			elif d[k] is None:
				self.add_argument('--%s'%(k),dest='%s%s'%(prefix,k),default=None,action='store',help=helpinfo)
			else:
				raise Exception('%s type(%s) not supported'%(k,type(d[k])))
		return

