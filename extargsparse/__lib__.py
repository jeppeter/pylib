#!/usr/bin/python

import argparse
import os
import sys
import json
import logging
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import __key__ as keyparse


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



class ExtArgsParse(argparse.ArgumentParser):

	def __load_command_line_string(self,prefix,keycls,v,curparser=None):
		pass

	def __load_command_line_int(self,prefix,keycls,v,curparser=None):
		pass

	def __load_command_line_float(self,prefix,keycls,v,curparser=None):
		pass

	def __load_command_line_list(self,prefix,keycls,v,curparser=None):
		pass

	def __load_command_line_bool(self,prefix,keycls,v,curparser=None):
		pass

	def __load_command_line_dict(self,prefix,keycls,v,curparser=None):
		pass

	def __init__(self,prog=None,usage=None,description=None,epilog=None,
                 parents=[],formatter_class=argparse.HelpFormatter,prefix_chars='-',
                 fromfile_prefix_chars=None,argument_default=None,
                 conflict_handler='error',add_help=True):
		super(ExtArgsParse,self).__init__(prog,usage,description,epilog,parents,formatter_class,
			   prefix_chars,fromfile_prefix_chars,argument_default,conflict_handler,add_help)
		self.__cmdparsers = dict()
		self.__subparser = None
		self.__load_command_map = {
			'string' : self.__load_command_line_string,
			'int' : self.__load_command_line_int,
			'float' : self.__load_command_line_float,
			'dict' : self.__load_command_line_dict,
			'list' : self.__load_command_line_list,
			'bool' : self.__load_command_line_bool
		}

		return

	def __load_subparser(self,prefix,keycls,mapv,lastparser):
		typecls = _GetType(mapv)
		# we can not add sub command in two level ,or not dictionary format
		if str(typecls) != 'dict' or lastparser is not None:
			keycls.change_to_flag()
			self.__load_command_map[str(typecls)](prefix,keycls,mapv,lastparser)
			return
		if self.__subparser is None:
			self.__subparser = self.add_subparser(help='',dest='subcommand')

		helpinfo = '%s command'%(keycls.cmdname)
		if keycls.helpinfo:
			helpinfo = keycls.helpinfo
		if keycls.cmdname in self.__cmdparsers.keys():
			raise Exception('(%s) subcommand already defined'%(keycls.cmdname))
		curparser = self.__subparser.add_parser(keycls.cmdname,help=helpinfo)
		self.__cmdparsers[keycls.cmdname] = curparser
		# now we should make new prefix
		newprefix = ''
		if len(prefix) > 0:
			newprefix += '%s_'%(prefix)
		newprefix += keycls.cmdname
		self.__load_command_line_inner(newprefix,mapv,curparser)
		return


	def __load_command_line_inner(self,prefix,d,curparser=None):
		for k in d.keys():
			if curparser:
				# if we have in the mode for this we should make it
				# must be the flag mode
				keycls = keyparse.ExtKeyParse(k,True)
			else:
				# we can not make sure it is flag mode
				keycls = keyparse.ExtKeyParse(k,False)
			if keycls.isflag :
				# it is flag mode
				typecls = _GetType(d[k])
				self.__load_command_map[str(typecls)](keycls,d[k],curparser)
			else:
				assert(keycls.iscmd)
				self.__load_subparser(keycls,d[k],curparser)
		return

	def load_command_line(self,d):
		if not isinstance(d,dict):
			raise Exception('input parameter(%s) not dict'%(d))
		self.__load_command_line_inner('',d,None)
		return


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

