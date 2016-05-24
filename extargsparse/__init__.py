#!/usr/bin/python

import argparse
import os
import sys
import json
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import const

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


class ExtArgsParse(argparse.ArgumentParser):
	def __init__(self,prog=None,usage=None,description=None,epilog=None,
                 parents=[],formatter_class=argparse.HelpFormatter,prefix_chars='-',
                 fromfile_prefix_chars=None,argument_default=None,
                 conflict_handler='error',add_help=True):
		super(ExtArgsParse,self).__init__(prog,usage,description,epilog,parents,formatter_class,
			   prefix_chars,fromfile_prefix_chars,argument_default,conflict_handler,add_help)
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


def load_json_args(args,constcls):
	if  not isinstance(constcls , const.ConstantClassBase):
		raise Exception('%s not subclass of const.ConstantClassBase'%(constcls))
	if getattr(args,'%sjsonfile'%(constcls.KEYWORD()),None) is None:
		# now we should get all the default
		for p in dir(constcls):
			if p.startswith(constcls.KEYWORD().upper()):
				if getattr(args,p.lower()) is None:
					setattr(args,p.lower(),getattr(constcls,p))
		return args

	# it will parse the files
	keywords = []
	for p in dir(constcls):
		if p.lower().startswith(constcls.KEYWORD()):
			curkey = p.lower().replace(constcls.KEYWORD(),'')
			if curkey not in keywords:
				keywords.append(curkey)
	logging.info('keywords %s'%(keywords))
	with open(getattr(args,'%sjsonfile'%(constcls.KEYWORD())),'r') as f:
		tcejson = json.load(f)
		for p in tcejson.keys():
			if p in keywords:
				tcekeyword = '%s%s'%(constcls.KEYWORD(),p)
				if getattr(args,tcekeyword) is None:
					setattr(args,tcekeyword,tcejson[p])
		for p in dir(constcls):
			if p.startswith(constcls.KEYWORD().upper()):
				if getattr(args,p.lower()) is None:
					setattr(args,p.lower(),getattr(constcls,p))
	return args

