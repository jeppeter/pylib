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
		elif:
			# we use default string
			self.__type = 'string'
		else:
			raise Exception('(%s)unknown type (%s)'%(v,type(v)))
		return

	def get_type(self):
		return self.__type

	def __str__(self):
		return self.__type


class IntAction(argparse.Action):
	 def __init__(self, option_strings, dest, nargs=1, **kwargs):
	 	super(IntAction,self).__init__(option_strings, dest, **kwargs)
	 	return

	 def __call__(self, parser, namespace, values, option_string=None):
	 	try:
	 		intval = int(values)
	 	except:
	 		raise Exception('%s not valid number'%(values))
	 	setattr(namespace,self.dest,intval)
	 	return


class ArrayAction(argparse.Action):
	 def __init__(self, option_strings, dest, nargs=1, **kwargs):
	 	super(IntAction,self).__init__(option_strings, dest, **kwargs)
	 	return

	 def __call__(self, parser, namespace, values, option_string=None):
	 	if self.dest is None:
	 		self.dest = []
	 	if values not in self.dest:
		 	self.dest.append(values)
	 	return

class FloatAction(argparse.Action):
	 def __init__(self, option_strings, dest, nargs=1, **kwargs):
	 	super(IntAction,self).__init__(option_strings, dest, **kwargs)
	 	return

	 def __call__(self, parser, namespace, values, option_string=None):
	 	try:
	 		fval = float(values)
	 	except:
	 		raise Exception('%s not valid number'%(values))
	 	setattr(namespace,self.dest,fval)
	 	return


class ExtArgParse(argparse.ArgumentParser):
	def __get_opt_varname (self,prefix,keycls):
		assert(keycls.flagname)
		longopt = '--'
		shortopt = None
		optdest = ''
		if len(prefix) > 0:
			longopt += '%s_'%(prefix)
			optdest += '%s_'%(prefix)

		longopt += keycls.flagname
		optdest += keycls.flagname
		longopt = longopt.replace('_','-')
		optdest = optdest.replace('-','_')
		longopt = longopt.lower()
		optdest = optdest.lower()
		if keycls.shortflag:
			shortopt = '-'
			shortopt += keycls.shortflag

		helpinfo = '%s set'%(optdest)
		if keycls.helpinfo:
			helpinfo = keycls.helpinfo
		return longopt,shortopt,optdest,helpinfo


	def __get_help_info(self,optdest,keycls,val):
		tpcls = _GetType(v)
		helpinfo = ''
		if str(typecls) == 'bool':
			if val :
				helpinfo += '%s set false'%(optdest)
			else:
				helpinfo += '%s set true'%(optdest)
		elif str(typecls) == 'string' and val == '+':
			helpinfo += '%s inc'%(optdest)
		else:
			helpinfo += '%s set'%(optdest)
		if keycls.helpinfo:
			helpinfo = keycls.helpinfo
		return helpinfo

	def __load_command_line_string(self,prefix,keycls,v,curparser=None):
		assert(keycls.flagname)
		longopt ,shortopt,optdest = self.__get_opt_varname(prefix,keycls)
		putparser = self
		if curparser is not None:
			putparser = curparser

		helpinfo = self.__get_help_info(optdest,keycls,v)
		if v == '+':
			if shortopt:
				putparser.add_argument(shortopt,longopt,dest=optdest,default=0,action='count')
			else:
				putparser.add_argument(longopt,dest=optdest,default=0,action='count')
		else:
			if shortopt:
				putparser.add_argument(shortopt,longopt,dest=optdest,default=None,help=helpinfo)
			else:
				putparser.add_argument(longopt,dest=optdest,default=None,help=helpinfo)
		return

	def __load_command_line_int(self,prefix,keycls,v,curparser=None):
		longopt,shortopt,optdest = self.__get_opt_varname(prefix,keycls)
		helpinfo = self.__get_help_info(optdest,keycls,v)
		putparser = self
		if curparser is not None:
			putparser = curparser

		if shortopt :
			putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action=IntAction,help=helpinfo)
		else:
			putparser.add_argument(longopt,dest=optdest,default=None,action=IntAction,help=helpinfo)
		return


	def __load_command_line_float(self,prefix,keycls,v,curparser=None):
		longopt,shortopt,optdest = self.__get_opt_varname(prefix,keycls)
		helpinfo = self.__get_help_info(optdest,keycls,v)
		putparser = self
		if curparser is not None:
			putparser = curparser
		if shortopt :
			putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action=FloatAction,help=helpinfo)
		else:
			putparser.add_argument(longopt,dest=optdest,default=None,action=FloatAction,help=helpinfo)
		return

	def __load_command_line_list(self,prefix,keycls,v,curparser=None):
		longopt,shortopt,optdest = self.__get_opt_varname(prefix,keycls)
		helpinfo = self.__get_help_info(optdest,keycls,v)
		putparser = self
		if curparser is not None:
			putparser = curparser
		if shortopt :
			putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action=ArrayAction,help=helpinfo)
		else:
			putparser.add_argument(longopt,dest=optdest,default=None,action=ArrayAction,help=helpinfo)
		return

	def __load_command_line_bool(self,prefix,keycls,v,curparser=None):
		longopt,shortopt,optdest = self.__get_opt_varname(prefix,keycls)
		helpinfo = self.__get_help_info(optdest,keycls,v)
		putparser = self
		if curparser is not None:
			putparser = curparser
		if v :
			if shortopt :
				putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action='store_false',help=helpinfo)
			else:
				putparser.add_argument(longopt,dest=optdest,default=None,action='store_false',help=helpinfo)
		else:
			if shortopt :
				putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action='store_true',help=helpinfo)
			else:
				putparser.add_argument(longopt,dest=optdest,default=None,action='store_true',help=helpinfo)
		return

	def __load_command_line_left(self,prefix,keycls,v,curparser=None):
		assert(keycls.flagname == '$')
		putparser = self
		optdest = 'args'
		if curparser:
			putparser = curparser
			optdest = 'subnargs'
		helpinfo = '%s set '%(optdest)
		if keycls.helpinfo:
			helpinfo = keycls.helpinfo
		putparser.add_argument(optdest,metavar='N',type=str,nargs=keycls.nargs,help=helpinfo)
		return


	def __load_command_line_dict(self,prefix,keycls,v,curparser=None):
		arg_option = {
			'flagname' : None,
			'helpinfo' : None,
			'shortflag' : None,
			'nargs' : None,
			'prefix' : None,
			'shortflag' : None,
			'iscmd' : None,
			'isflag' : None,
			'function' : None,
			'cmdname' : None,
			'origkey' : None
		}
		val = None
		key_option = keycls.get_options()


		for k in v.keys():
			if k in arg_option.keys():
				setattr(arg_option,k,v[k])

		for k in arg_option.keys():
			if arg_option[k] is None and key_option[k] is not None:
				arg_option[k] = key_option[k]

		if 'value' in v.keys():
			val = v['value']		

		# now we get the type
		arg_option['iscmd'] = False
		arg_option['isflag'] = True
		arg_option['function'] = None
		newcls = keyparse.ExtKeyParse(arg_option)
		tpcls = _GetType(val)
		if str(tpcls) == 'dict':			
			raise Exception('can not set %s value as dict type'%(newcls.flagname))
		if newcls.flagname == '$':
			# we used the left one to store
			self.__load_command_line_left(prefix,newcls,val,curparser)
		else:
			self.__load_command_map[str(tpcls)](prefix,newcls,val,curparser)
		return


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
		# or we prefix not set
		if str(typecls) != 'dict' or lastparser is not None or len(prefix) > 0:
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
		parserdict = {
			parser : curparser,
			typeclass : keycls
		}
		self.__cmdparsers[keycls.cmdname] = parserdict
		# now we should make new prefix
		newprefix = ''
		if len(prefix) > 0:
			newprefix += '%s_'%(prefix)
		newprefix += keycls.cmdname
		self.__load_command_line_inner(newprefix,mapv,curparser)
		return

	def __load_command_line_jsonfile(self,prefix,curparser):
		if len(prefix) > 0 and curparser is None:
			# if we are in the above the prefix call ,so we should not make any
			# json
			return

		optdest = ''
		helpinfo = ''
		if len(prefix) > 0:
			optdest += '%s_'%(prefix)
			helpinfo += '%s '%(prefix)
		optdest += 'json'
		helpinfo += ' jsonfile to set'
		origkey += 'json##%s##'%(helpinfo)
		args_option = {
			'cmdname' : None,
			'flagname' : 'json',
			'helpinfo' : helpinfo,
			'function' : None,
			'shortflag' : None,
			'prefix' : prefix,
			'origkey' : origkey
			'iscmd'  : False,
			'isflag' : True,
			'nargs' : 1
		}
		newcls = keyparse.ExtKeyParse(args_option)
		# now for string
		self.__load_command_line_string(prefix,newcls,None,curparser)
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
				if keycls.flagname is None :
					# this may be the prefix for it
					if str(typecls) == 'dict':
						assert(typecls.prefix is not None)
						newprefix = ''
						if len(prefix) > 0:
							newprefix += '%s_'%(prefix)
						newprefix += '%s'%(keycls.prefix)
						self.__load_command_line_inner(newprefix,d[k],curparser)
					else:
						raise Exception('(%s) if only define prefix will have dict'%(k))
				if keycls.flagname == '$' and str(typecls) != 'dict':
					# if it is dictionary ,it will give the more handle
					self.__load_command_line_left(keycls,d[k],curparser)
				else:
					self.__load_command_map[str(typecls)](keycls,d[k],curparser)
			else:
				assert(keycls.iscmd)
				self.__load_subparser(keycls,d[k],curparser)
		# all is over ,so we should get the json parse value ok
		self.__load_command_line_jsonfile(prefix,curparser)
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

	def parse_command_line(self,params=None):
		if params is None:
			params = sys.argv[1:]
		args = self.parse_args(params)
		# now we should get the 


