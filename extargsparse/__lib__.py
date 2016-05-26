#!/usr/bin/python

import argparse
import os
import sys
import json
import logging
import unittest
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import __key__ as keyparse

def __call_func_args(funcname,args):
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

class _ParserCompact(object):
	pass

class ArrayAction(argparse.Action):
	 def __init__(self, option_strings, dest, nargs=1, **kwargs):
	 	argparse.Action.__init__(self,option_strings, dest, **kwargs)
	 	return

	 def __call__(self, parser, namespace, values, option_string=None):
	 	if getattr(namespace,self.dest) is None:
	 		setattr(namespace,self.dest,[])
	 	lists = getattr(namespace,self.dest)
	 	if values not in lists:
		 	lists.append(values)
		setattr(namespace,self.dest,lists)
	 	return

class FloatAction(argparse.Action):
	 def __init__(self, option_strings, dest, nargs=1, **kwargs):
	 	super(IntAction,self).__init__(option_strings, dest, **kwargs)
	 	self.dest = None
	 	return

	 def __call__(self, parser, namespace, values, option_string=None):
	 	try:
	 		fval = float(values)
	 	except:
	 		raise Exception('%s not valid number'%(values))
	 	setattr(namespace,self.dest,fval)
	 	return


class ExtArgsParse(argparse.ArgumentParser):
	def __get_help_info(self,keycls):
		helpinfo = ''
		if keycls.type == 'bool':
			if keycls.value :
				helpinfo += '%s set false'%(keycls.optdest)
			else:
				helpinfo += '%s set true'%(keycls.optdest)
		elif keycls.type == 'string' and keycls.value == '+':
			if keycls.isflag:
				helpinfo += '%s inc'%(keycls.optdest)
			else:
				raise Exception('cmd(%s) can not set value(%s)'%(keycls.cmdname,keycls.value))
		else:
			if keycls.isflag:
				helpinfo += '%s set'%(keycls.optdest)
			else:
				helpinfo += '%s command exec'%(keycls.cmdname)
		if keycls.helpinfo:
			helpinfo = keycls.helpinfo
		return helpinfo

	def __check_flag_insert(self,keycls,curparser=None):
		if curparser :
			for k in curparser.flags:
				if k.flagname != '$' and keycls.flagname != '$':
					if k.optdest == keycls.optdest:
						return False
				elif k.flagname == keycls.flagname:
					return False
			curparser.flags.append(keycls)
		else:
			for k in self.__flags:
				if (k.flagname != '$') and (keycls.flagname != '$'):
					if k.optdest == keycls.optdest:
						return False
				elif k.flagname == keycls.flagname:
					return False
			self.__flags.append(keycls)
		return True

	def __check_flag_insert_mustsucc(self,keycls,curparser=None):
		valid = self.__check_flag_insert(keycls,curparser)
		if not valid:
			cmdname = 'main'
			if curparser:
				cmdname = curparser.cmdname
			raise Exception('(%s) already in command(%s)'%(keycls.flagname,cmdname))
		return

	def __load_command_line_string(self,prefix,keycls,curparser=None):
		self.__check_flag_insert_mustsucc(keycls,curparser)
		longopt = keycls.longopt
		shortopt = keycls.shortopt
		optdest = keycls.optdest
		putparser = self
		if curparser is not None:
			putparser = curparser.parser
		helpinfo = self.__get_help_info(keycls)
		if keycls.value == '+':
			if shortopt:
				putparser.add_argument(shortopt,longopt,dest=optdest,default=0,action='count')
			else:
				putparser.add_argument(longopt,dest=optdest,default=0,action='count')
		else:
			if shortopt:
				putparser.add_argument(shortopt,longopt,dest=optdest,default=None,help=helpinfo)
			else:
				putparser.add_argument(longopt,dest=optdest,default=None,help=helpinfo)
		return True

	def __load_command_line_int(self,prefix,keycls,curparser=None):
		self.__check_flag_insert_mustsucc(keycls,curparser)
		longopt = keycls.longopt
		shortopt = keycls.shortopt
		optdest = keycls.optdest
		helpinfo = self.__get_help_info(keycls)
		putparser = self
		if curparser is not None:
			putparser = curparser.parser

		if shortopt :
			putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action=IntAction,help=helpinfo)
		else:
			putparser.add_argument(longopt,dest=optdest,default=None,action=IntAction,help=helpinfo)
		return True


	def __load_command_line_float(self,prefix,keycls,curparser=None):
		self.__check_flag_insert_mustsucc(keycls,curparser)
		longopt = keycls.longopt
		shortopt = keycls.shortopt
		optdest = keycls.optdest
		helpinfo = self.__get_help_info(keycls)
		putparser = self
		if curparser is not None:
			putparser = curparser.parser

		if shortopt :
			putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action=FloatAction,help=helpinfo)
		else:
			putparser.add_argument(longopt,dest=optdest,default=None,action=FloatAction,help=helpinfo)
		return True

	def __load_command_line_list(self,prefix,keycls,curparser=None):
		self.__check_flag_insert_mustsucc(keycls,curparser)
		longopt = keycls.longopt
		shortopt = keycls.shortopt
		optdest = keycls.optdest
		helpinfo = self.__get_help_info(keycls)
		putparser = self
		if curparser is not None:
			putparser = curparser.parser
		if shortopt :
			putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action=ArrayAction,help=helpinfo)
		else:
			putparser.add_argument(longopt,dest=optdest,default=None,action=ArrayAction,help=helpinfo)
		return True

	def __load_command_line_bool(self,prefix,keycls,curparser=None):
		self.__check_flag_insert_mustsucc(keycls,curparser)
		longopt = keycls.longopt
		shortopt = keycls.shortopt
		optdest = keycls.optdest
		helpinfo = self.__get_help_info(keycls)
		putparser = self
		if curparser is not None:
			putparser = curparser.parser
		if keycls.value :
			if shortopt :
				putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action='store_false',help=helpinfo)
			else:
				putparser.add_argument(longopt,dest=optdest,default=None,action='store_false',help=helpinfo)
		else:
			if shortopt :
				putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action='store_true',help=helpinfo)
			else:
				putparser.add_argument(longopt,dest=optdest,default=None,action='store_true',help=helpinfo)
		return True

	def __load_command_line_args(self,prefix,keycls,curparser=None):
		valid = self.__check_flag_insert(keycls,curparser)
		if not valid :
			return False
		putparser = self
		optdest = 'args'
		if curparser:
			putparser = curparser.parser
			optdest = 'subnargs'
		helpinfo = '%s set '%(optdest)
		if keycls.helpinfo:
			helpinfo = keycls.helpinfo
		putparser.add_argument(optdest,metavar='N',type=str,nargs=keycls.nargs,help=helpinfo)
		return True

	def __load_command_line_jsonfile(self,keycls,curparser=None):
		valid = self.__check_flag_insert(keycls,curparser)
		if not valid:
			return False
		putparser = self
		if curparser :
			putparser = curparser.parser
		longopt = keycls.longopt
		optdest = keycls.optdest
		helpinfo = self.__get_help_info(keycls)
		putparser.add_argument(longopt,dest=optdest,action='store',default=None,help=helpinfo)
		return True

	def __load_command_line_json_added(self,curparser=None):
		prefix = ''
		key = 'json## json input file to get the value set ##'
		value = None
		if curparser :
			prefix = curparser.cmdname
		keycls = keyparse.ExtKeyParse(prefix,key,value,True)
		return self.__load_command_line_jsonfile(keycls,curparser)


	def __init__(self,prog=None,usage=None,description=None,epilog=None,
                 parents=[],formatter_class=argparse.HelpFormatter,prefix_chars='-',
                 fromfile_prefix_chars=None,argument_default=None,
                 conflict_handler='error',add_help=True):
		argparse.ArgumentParser.__init__(self)
		self.__subparser = None
		self.__cmdparsers = []
		self.__flags = []
		self.__load_command_map = {
			'string' : self.__load_command_line_string,
			'unicode' : self.__load_command_line_string,
			'int' : self.__load_command_line_int,
			'float' : self.__load_command_line_float,
			'list' : self.__load_command_line_list,
			'bool' : self.__load_command_line_bool,
			'args' : self.__load_command_line_args,
			'command' : self.__load_command_subparser,
			'prefix' : self.__load_command_prefix
		}
		return

	def __find_subparser_inner(self,name):
		for k in self.__cmdparsers:
			if k.cmdname == name:
				return k
		return None


	def __get_subparser_inner(self,keycls):
		cmdparser = self.__find_subparser_inner(keycls.cmdname)
		if cmdparser is not None:
			return cmdparser
		if self.__subparser is None:
			self.__subparser = self.add_subparsers(help='',dest='subcommand')
		helpinfo = self.__get_help_info(keycls)
		parser = self.__subparser.add_parser(keycls.cmdname,help=helpinfo)
		cmdparser = _ParserCompact()
		cmdparser.parser = parser
		cmdparser.flags = []
		cmdparser.cmdname = keycls.cmdname
		cmdparser.typeclass = keycls
		self.__cmdparsers.append(cmdparser)
		return cmdparser


	def __load_command_subparser(self,prefix,keycls,lastparser=None):
		if lastparser :
			raise Exception('(%s) can not make command recursively'%(keycls.origkey))
		if not isinstance( keycls.value,dict):
			raise Exception('(%s) value must be dict'%(keycls.origkey))
		parser = self.__get_subparser_inner(keycls)
		self.__load_command_line_inner(keycls.prefix,keycls.value,parser)
		return True

	def __load_command_prefix(self,prefix,keycls,curparser=None):
		self.__load_command_line_inner(keycls.prefix,keycls.value,curparser)
		return True

	def __load_command_line_inner(self,prefix,d,curparser=None):
		self.__load_command_line_json_added(curparser)
		for k in d.keys():
			v = d[k]
			if curparser:
				# if we have in the mode for this we should make it
				# must be the flag mode
				logging.info('%s , %s , %s , True'%(prefix,k,v))
				keycls = keyparse.ExtKeyParse(prefix,k,v,True)
			else:
				# we can not make sure it is flag mode
				logging.info('%s , %s , %s , False'%(prefix,k,v))
				keycls = keyparse.ExtKeyParse(prefix,k,v,False)
			valid = self.__load_command_map[keycls.type](prefix,keycls,curparser)
			if not valid:
				raise Exception('can not add (%s)'%(k,v))
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
		logging.info('d (%s)'%(d))
		self.load_command_line(d)
		return


	def __set_jsonvalue_not_defined(self,args,flagarray,key,value):
		for p in flagarray:
			if p.isflag and p.type != 'prefix' and p.type != 'args':
				if p.optdest == key:
					if getattr(args,key,None) is None:
						if str(keyparse.TypeClass(value)) != str(keyparse.TypeClass(p.value)):
							logging.warn('%s  type (%s) as default value type (%s)'%(key,str(keyparse.TypeClass(value)),str(keyparse.TypeClass(p.value))))
						logging.info('set (%s)=(%s)'%(key,value))
						setattr(args,key,value)
					return args
		logging.info('can not search for (%s)'%(key))
		return args

	def __load_jsonvalue(self,args,prefix,jsonval,flagarray):
		for k in jsonvalue:
			if isinstance(jsonvalue[k],dict):
				newprefix = ''
				if len(prefix) > 0:
					newprefix += '%s_'%(prefix)
				newprefix += k
				args = self.__load_jsonvalue(args,newprefix,jsonvalue[k],flagarray)
			else:
				newkey = ''
				if (len(prefix) > 0):
					newkey += '%s_'%(prefix)
				newkey += k
				args = self.__set_jsonvalue_not_defined(args,flagarray,newkey,jsonvalue[k])
		return args


	def __load_jsonfile(self,args,cmdname,jsonfile,curparser=None):
		assert(jsonfile is not None)
		prefix = ''
		if cmdname is not None :
			prefix += cmdname
		flagarray = self.__flags
		if curparser :
			flagarray = curparser.flags

		fp = open(jsonfile,'r+')
		try:
			jsonvalue = json.load(fp)
		except:
			logging.warn('can not parse (%s)'%(jsonfile))
			fp.close()
			fp = None
			return args
		return self.__load_jsonvalue(args,prefix,jsonvalue,flagarray)



	def __set_parser_default_value(self,args,flagarray):
		for keycls in flagarray:
			if keycls.isflag and keycls.type != 'prefix' and keycls.type != 'args':
				self.__set_jsonvalue_not_defined(args,flagarray,keycls.optdest,keycls.value)
		return args

	def __set_default_value(self,args):
		for parser in self.__cmdparsers:
			args = self.__set_parser_default_value(args,parser.flags)

		args = self.__set_parser_default_value(args,self.__flags)
		return args

	def __set_environ_value_inner(self,args,prefix,flagarray):
		for keycls in flagarray:
			if keycls.isflag and keycls.type != 'prefix' and keycls.type != 'args':
				optdest = keycls.optdest
				oldopt = optdest
				if getattr(args,oldopt,None) is not None:
					# have set ,so we do not set it
					continue
				optdest = optdest.upper()
				if '_' not in optdest:
					optdest = 'EXTARGS_%s'%(optdest)
				val = os.getenv(optdest,None)
				if val is not None:
					# to check the type
					logging.info('set env(%s) (%s = %s)'%(optdest,oldopt,val))
					if keycls.type == 'string':
						setattr(args,oldopt,val)
					elif keycls.type == 'bool':						
						if val.lower() == 'true':
							setattr(args,oldopt,True)
						elif val.lower() == 'false':
							setattr(args,oldopt,False)
					elif keycls.type == 'list':
						try:
							lval = eval(val)
							if not isinstance(lval,list):
								raise Exception('(%s) environ(%s) not valid'%(optdest,val))
							setattr(args,oldopt,lval)
						except:
							logging.warn('can not set (%s) for %s = %s'%(optdest,oldopt,val))
					elif keycls.type == 'int':
						try:
							lval = int(val)
							setattr(args,oldopt,lval)
						except:
							logging.warn('can not set (%s) for %s = %s'%(optdest,oldopt,val))
					elif keycls.type == 'float':
						try:
							lval = float(val)
							setattr(args,oldopt,lval)
						except:
							logging.warn('can not set (%s) for %s = %s'%(optdest,oldopt,val))
					else:
						raise Exception('internal error when (%s) type(%s)'%(keycls.optdest,keycls.type))
		return args



	def __set_environ_value(self,args):
		for parser in self.__cmdparsers:
			args = self.__set_environ_value_inner(args,parser.cmdname,parser.flags)
		args = self.__set_environ_value_inner(args,'',self.__flags)
		return args


	def parse_command_line(self,params=None):
		if params is None:
			params = sys.argv[1:]
		args = self.parse_args(params)
		# now we should get the 
		# first to test all the json file for special command
		if self.__subparser and args.subcommand is not None:
			jsondest = '%s_json'%(args.subcommand)
			curparser = self.__find_subparser_inner(args.subcommand)
			assert(curparser is not None)
			jsonfile = getattr(args,jsondest,None)
			if jsonfile is not None:
				# ok we should make this parse
				args = self.__load_jsonfile(args,args.subcommand,jsonfile,curparser)

		# to get the total command
		if args.json is not None:
			jsonfile = args.json
			args = self.__load_jsonfile(args,'',jsonfile,None)

		# now to check for the environment as the put file
		if self.__subparser and args.subcommand is not None:
			jsondest = '%s_json'%(args.subcommand)
			curparser = self.__find_subparser_inner(args.subcommand)
			assert(curparser is not None)
			jsondest = jsondest.replace('-','_')
			jsondest = jsondest.upper()
			jsonfile = os.getenv(jsondest,None)
			if jsonfile is not None:
				# ok we should make this parse
				args = self.__load_jsonfile(args,args.subcommand,jsonfile,curparser)

		# now get the JSONFILE from environment variable
		args = self.__set_environ_value(args)


		# to get the json existed 
		jsonfile = os.getenv('EXTARGSPARSE_JSON',None)
		if jsonfile is not None:
			args = self.__load_jsonfile(args,'',jsonfile,None)

		# set the default value
		args = self.__set_default_value(args)

		# now test whether the function has
		if self.__subparser and args.subcommand is not None:
			parser = self.__find_subparser_inner(args.subcommand)
			assert(parser is not None)
			funcname = parser.typeclass.function
			if funcname is not None:
				return __call_func_args(funcname,args)
		return args


class ExtArgsTestCase(unittest.TestCase):
	def setUp(self):
		if 'EXTARGSPARSE_JSON' in os.environ.keys():
			del os.environ['EXTARGSPARSE_JSON']
		for k in os.environ.keys():
			if k.startswith('EXTARGS_'):
				del os.environ[k]
		return

	def tearDown(self):
		pass

	@classmethod
	def setUpClass(cls):
		pass

	@classmethod
	def tearDownClass(cls):
		pass

	def test_A001(self):
		loads = '''
		{
			"verbose|v##increment verbose mode##" : "+",
			"flag|f## flag set##" : false,
			"number|n" : 0,
			"list|l" : [],
			"string|s" : "string_var",
			"$" : {
				"value" : [],
				"nargs" : "*",
				"type" : "string"
			}
		}
		'''
		parser = ExtArgsParse()
		parser.load_command_line_string(loads)
		args = parser.parse_command_line(['-vvvv','-f','-n','30','-l','bar1','-l','bar2','var1','var2'])
		self.assertEqual(args.verbose,4)
		self.assertEqual(args.flag,True)
		self.assertEqual(args.number,30)
		self.assertEqual(args.list,['bar1','bar2'])
		self.assertEqual(args.string,'string_var')
		self.assertEqual(args.args,['var1','var2'])
		return

	def test_A002(self):
		loads = '''
		{
			"verbose|v" : "+",
			"port|p" : 3000,
			"dep" : {
				"list|l" : [],
				"string|s" : "s_var",
				"$" : "+"
			}
		}
		'''
		parser = ExtArgsParse()
		parser.load_command_line_string(loads)
		args = parser.parse_command_line(['-vvvv','-p','5000','dep','-l','arg1','--dep-list','arg2','cc','dd'])
		self.assertEqual(args.verbose,4)
		self.assertEqual(args.port,5000)
		self.assertEqual(args.subcommand,'dep')
		self.assertEqual(args.dep_list,['arg1','arg2'])
		self.assertEqual(args.dep_string,'s_var')
		self.assertEqual(args.subnargs,['cc','dd'])
		return




def main():
	if '-v' in sys.argv[1:] or '--verbose' in sys.argv[1:]:
		logging.basicConfig(level=logging.INFO,format="%(levelname)-8s [%(filename)-10s:%(funcName)-20s:%(lineno)-5s] %(message)s")	
	unittest.main()

if __name__ == '__main__':
	main()	
