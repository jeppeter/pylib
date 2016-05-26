#!/usr/bin/python

import os
import sys
import logging
import re
import unittest
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

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
		elif v is None:
			# we use default string
			self.__type = 'string'
		else:
			raise Exception('(%s)unknown type (%s)'%(v,type(v)))
		return

	def get_type(self):
		return self.__type

	def __str__(self):
		return self.__type



class ExtKeyParse:
	flagspecial = ['value','prefix']
	flagwords = ['flagname','helpinfo','shortflag','nargs']
	cmdwords = ['cmdname','function','helpinfo']
	otherwords = ['origkey','iscmd','isflag','type']
	formwords = ['longopt','shortopt','optdest']
	def __reset(self):
		self.__value = None
		self.__prefix = ''
		self.__flagname = None
		self.__helpinfo = None
		self.__shortflag = None
		self.__nargs = None
		self.__cmdname = None
		self.__function = None
		self.__origkey = None
		self.__iscmd = None
		self.__isflag = None
		self.__type = None
		return

	def __validate(self):
		if self.__isflag:
			assert(not self.__iscmd )
			if self.__function is not None:
				raise Exception('(%s) can not accept function'%(self.__origkey))
			if self.__type == 'dict' and self.__flagname:
				# in the prefix we will get dict ok
				raise Exception('(%s) flag can not accept dict'%(self.__origkey))
			if self.__type != str(_GetType(self.__value)):
				raise Exception('(%s) value (%s) not match type (%s)'%(self.__origkey,self.__value,self.__type))
			if self.__nargs is None:
				self.__nargs = 1
			if self.__flagname is None :
				# we should test if the validate flag
				if self.__prefix is None:
					raise Exception('(%s) should at least for prefix'%(self.__origkey))
				self.__type = 'prefix'
				if str(_GetType(self.__value)) != 'dict':
					raise Exception('(%s) should used dict to make prefix'%(self.__origkey))			
				if self.__helpinfo :
					raise Exception('(%s) should not have help info'%(self.__origkey))
				if self.__shortflag:
					raise Exception('(%s) should not set shortflag'%(self.__origkey))
			elif self.__flagname == '$':
				# this is args for handle
				self.__type = 'args'
				if self.__shortflag :
					raise Exception('(%s) can not set shortflag for args'%(self.__origkey))
			else:
				if len(self.__flagname) <= 0:
					raise Exception('(%s) can not accept (%s)short flag in flagname'%(self.__origkey,self.__flagname))
			if self.__shortflag:
				if len(self.__shortflag) > 1:
					raise Exception('(%s) can not accept (%s) for shortflag'%(self.__origkey,self.__shortflag))

		else:
			if self.__cmdname is None or len(self.__cmdname) == 0 :
				raise Exception('(%s) not set cmdname'%(self.__origkey))
			if self.__shortflag :
				raise Exception('(%s) has shortflag (%s)'%(self.__origkey,self.__shortflag))
			if self.__nargs:
				raise Exception('(%s) has nargs (%s)'%(self.__origkey,self.__nargs))
			if self.__type != 'dict':
				raise Exception('(%s) command must be dict'%(self.__origkey))
			self.__prefix = self.__cmdname
			self.__type = 'command'
		return

	def __set_flag(self,prefix,key,value):
		self.__isflag = True
		self.__iscmd = False
		self.__origkey = key
		if 'value' not in value.keys():
			self.__value = None
			self.__type = 'string'

		for k in value.keys():
			if k in self.__class__.flagwords:
				innerkey = self.__get_inner_name(k)
				if self.__dict__[innerkey] and self.__dict__[innerkey] != value[k]:
					raise Exception('set (%s) for not equal value (%s) (%s)'%(k,self.__dict__[innerkey],value[k]))
				if str(_GetType(value[k])) != 'string' and str(_GetType(value[k])) != 'int' :
					raise Exception('(%s)(%s) can not take other than int or string'%(self.__origkey,k))
				self.__dict__[innerkey] = value[k]
			elif k in self.__class__.flagspecial:
				innerkey = self.__get_inner_name(k)
				if k == 'prefix':
					if str(_GetType(value[k])) != 'string' or value[k] is None:
						raise Exception('(%s) prefix not string or None'%(self.__origkey))
					newprefix = ''
					if prefix and len(prefix):
						newprefix += '%s_'%(prefix)
					newprefix += value[k]
					self.__prefix = newprefix
				elif k == 'value':
					if str(_GetType(value[k])) == 'dict':
						raise Exception('(%s)(%s) can not accept dict'%(self.__origkey,k))
					self.__value = value[k]
					self.__type = str(_GetType(value[k]))
				else:
					self.__dict__[innerkey] = value[k]					
		if len(self.__prefix) == 0  and len(prefix) > 0:
			self.__prefix = prefix
		return


	def __parse(self,prefix,key,value,isflag):
		flagmod = False
		cmdmod = False
		flags = None
		self.__origkey = key
		if '$' in self.__origkey:
			if self.__origkey[0] != '$':
				raise Exception('(%s) not right format for ($)'%(self.__origkey))
			ok = 1
			try:
				idx = self.__origkey.index('$',1)
				ok = 0
			except:
				pass
			if ok == 0 :
				raise Exception('(%s) has ($) more than one'%(self.__origkey))
		if isflag :
			m = self.__flagexpr.findall(self.__origkey)
			if m and len(m)>0:
				flags = m[0]
			if flags is None :
				m = self.__mustflagexpr.findall(self.__origkey)
				if m and len(m) > 0:
					flags = m[0]
			if flags is not None:
				if '|' in flags:
					sarr = re.split('\|',flags)
					if len(sarr) > 2 or len(sarr[1]) != 1 or len(sarr[0]) <= 1 :
						raise Exception('(%s) (%s)flag only accept (longop|l) format'%(self.__origkey,flags))
					self.__flagname = sarr[0]
					self.__shortflag = sarr[1]
				else:
					self.__flagname = flags
				flagmod = True
		else:
			m = self.__mustflagexpr.findall(self.__origkey)
			if m and len(m) > 0:
				flags = m[0]
				if '|' in flags:
					sarr = re.split('\|',flags)
					if len(sarr) > 2 or len(sarr[1]) != 1 or len(sarr[0]) <= 1 :
						raise Exception('(%s) (%s)flag only accept (longop|l) format'%(self.__origkey,flags))
					self.__flagname = sarr[0]
					self.__shortflag = sarr[1]
				else:
					if len(flags) <= 1 :
						raise Exception('(%s) flag must have long opt'%(self.__origkey))
					self.__flagname = flags
				flagmod = True
			elif self.__origkey[0] == '$':
				# it means the origin is '$'
				self.__flagname = '$'
				flagmod = True
			m = self.__cmdexpr.findall(self.__origkey)
			if m and len(m) > 0:
				assert(not flagmod)
				if '|' in m[0]:
					flags = m[0]
					if '|' in flags:
						sarr = re.split('\|',flags)
						if len(sarr) > 2 or len(sarr[1]) != 1 or len(sarr[0]) <= 1 :
							raise Exception('(%s) (%s)flag only accept (longop|l) format'%(self.__origkey,flags))
						self.__flagname = sarr[0]
						self.__shortflag = sarr[1]
					else:
						assert( False )
					flagmod = True
				else:
					self.__cmdname = m[0]
					cmdmod = True

		m = self.__funcexpr.findall(self.__origkey)
		if m and len(m):
			self.__function = m[0]
		m = self.__helpexpr.findall(self.__origkey)
		if m and len(m) > 0:
			self.__helpinfo = m[0]
		newprefix = ''
		if prefix and len(prefix) > 0 :
			newprefix = '%s_'%(prefix)
		m = self.__prefixexpr.findall(self.__origkey)
		if m and len(m) > 0:
			newprefix += m[0]
			self.__prefix = newprefix
		if flagmod :
			self.__isflag = True
			self.__iscmd = False
		if cmdmod :
			self.__iscmd = True
			self.__isflag = False
		if  not flagmod and not cmdmod :
			self.__isflag = True
			self.__iscmd = False
		self.__value = value
		self.__type = str(_GetType(value))
		if cmdmod and self.__type != 'dict':
			flagmod = True
			cmdmod = False
			self.__isflag = True
			self.__iscmd = False
			self.__flagname = self.__cmdname
			self.__cmdname = None

		if self.__isflag and self.__flagname == '$' and self.__type != 'dict':
			raise Exception('(%s) for $ should option dict set'%(self.__origkey))
		if self.__isflag and self.__type == 'dict' and self.__flagname:
			self.__set_flag(prefix,key,value)
		self.__validate()
		return

	def __get_inner_name(self,name):
		innerkeyname = name
		if (name in self.__class__.flagwords) or \
			(name in self.__class__.flagspecial) or \
		   (name in self.__class__.cmdwords) or \
		   (name in self.__class__.otherwords):
			innerkeyname = '_%s__%s'%(self.__class__.__name__,name)
		return innerkeyname



	def __init__(self,prefix,key,value,isflag=False):
		self.__reset()
		self.__helpexpr = re.compile('##([^#]+)##$',re.I)
		self.__cmdexpr = re.compile('^([^\#\<\>\+\$]+)',re.I)
		self.__prefixexpr = re.compile('\+([^\+\#\<\>\|\$ \t]+)',re.I)
		self.__funcexpr = re.compile('<([^\<\>\#\$\| \t]+)>',re.I)
		self.__flagexpr = re.compile('^([^\<\>\#\+\$ \t]+)',re.I)
		self.__mustflagexpr = re.compile('^\$([^\$\+\#\<\>]+)',re.I)
		self.__origkey = key
		if isinstance(key,dict):
			self.__set_flag(prefix,key,value)
		else:
			self.__parse(prefix,key,value,isflag)
		return

	def __form_word(self,keyname):
		if keyname == 'longopt':
			if not self.__isflag or self.__flagname is None or self.__type == 'args':
				raise Exception('can not set (%s) longopt'%(self.__origkey))
			longopt = '--'
			if len(self.__prefix) > 0 :
				longopt += '%s_'%(self.__prefix)
			longopt += self.__flagname
			longopt = longopt.lower()
			longopt = longopt.replace('_','-')
			return longopt
		elif keyname == 'shortopt':
			if not self.__isflag or self.__flagname is None or self.__type == 'args':
				raise Exception('can not set (%s) shortopt'%(self.__origkey))
			shortopt = None
			if self.__shortflag:
				shortopt = '-%s'%(self.__shortflag)
			return shortopt
		elif keyname == 'optdest':
			if not self.__isflag or self.__flagname is None or self.__type == 'args':
				raise Exception('can not set (%s) optdest'%(self.__origkey))
			optdest = ''
			if len(self.__prefix) > 0:
				optdest += '%s_'%(self.__prefix)
			optdest += self.__flagname
			optdest = optdest
			optdest = optdest.lower()
			optdest = optdest.replace('-','_')
			return optdest

		assert(False)
		return



	def __getattr__(self,keyname):
		if keyname in self.__class__.formwords:
			return self.__form_word(keyname)
		innername = self.__get_inner_name(keyname)
		return self.__dict__[innername]

	def __setattr__(self,keyname,value):
		if (keyname in self.__class__.flagspecial) or \
			(keyname in self.__class__.flagwords) or \
			(keyname in self.__class__.cmdwords) or \
			(keyname in self.__class__.otherwords):
			raise AttributeError
		self.__dict__[keyname] = value
		return

	def change_to_flag(self):
		if not self.__iscmd or self.__isflag:
			raise Exception('(%s) not cmd to change'%(self.__origkey))
		if self.__function is not None:
			raise Exception('(%s) has function can not change'%(self.__origkey))
		assert(self.__flagname is None)
		assert(self.__shortflag is None)
		assert(self.__cmdname is not None)
		self.__flagname = self.__cmdname
		self.__cmdname = None
		self.__iscmd = False
		self.__isflag = True
		self.__validate()
		return



class UnitTestCase(unittest.TestCase):
	def __opt_fail_check(self,flags):
		ok = False
		try:
			val = flags.longopt
		except:
			ok = True
		self.assertTrue(ok)
		ok = False
		try:
			val = flags.optdest
		except:
			ok = True
		self.assertTrue(ok)
		ok = False
		try:
			val = flags.shortopt
		except:
			ok = True
		self.assertTrue(ok)
		return

	def test_A1(self):
		flags = ExtKeyParse('','$flag|f+type','string',False)
		self.assertEqual(flags.flagname , 'flag')
		self.assertEqual(flags.longopt,'--type-flag')
		self.assertEqual(flags.shortopt,'-f')
		self.assertEqual(flags.optdest,'type_flag')
		self.assertEqual(flags.value,'string')
		self.assertEqual(flags.type,'string')
		self.assertEqual(flags.shortflag , 'f')
		self.assertEqual(flags.prefix , 'type')
		self.assertTrue(flags.cmdname is None)
		self.assertTrue(flags.helpinfo is None)
		self.assertTrue(flags.function is None)
		self.assertTrue(flags.isflag)
		self.assertFalse(flags.iscmd)
		return

	def test_A2(self):
		flags = ExtKeyParse('','$flag|f+type',[],True)
		self.assertEqual(flags.flagname,'flag')
		self.assertEqual(flags.shortflag,'f')
		self.assertEqual(flags.prefix,'type')
		self.assertEqual(flags.longopt,'--type-flag')
		self.assertEqual(flags.shortopt,'-f')
		self.assertEqual(flags.optdest,'type_flag')
		self.assertEqual(flags.value,[])
		self.assertEqual(flags.type,'list')
		self.assertTrue(flags.helpinfo is None)
		self.assertTrue(flags.function is None)
		self.assertTrue(flags.cmdname is None)
		self.assertTrue(flags.isflag)
		self.assertFalse(flags.iscmd)
		return

	def test_A3(self):
		flags = ExtKeyParse('','flag|f',False,False)
		self.assertEqual(flags.flagname,'flag')
		self.assertEqual(flags.shortflag,'f')
		self.assertEqual(flags.longopt,'--flag')
		self.assertEqual(flags.shortopt,'-f')
		self.assertEqual(flags.value,False)
		self.assertEqual(flags.type,'bool')
		self.assertEqual(flags.prefix ,'')
		self.assertTrue(flags.helpinfo is None)
		self.assertTrue(flags.function is None)
		self.assertTrue(flags.cmdname is None)
		self.assertTrue(flags.isflag)
		self.assertFalse(flags.iscmd)
		return

	def test_A4(self):
		flags = ExtKeyParse('newtype','flag<flag.main>##help for flag##',{},False)
		self.assertEqual(flags.cmdname , 'flag')
		self.assertEqual(flags.function , 'flag.main')
		self.assertEqual(flags.type , 'command')
		self.assertEqual(flags.prefix ,'flag')
		self.assertEqual(flags.helpinfo,'help for flag')
		self.assertTrue(flags.flagname is None)
		self.assertTrue(flags.shortflag is None)
		self.assertEqual(flags.value,{})
		self.assertFalse(flags.isflag)
		self.assertTrue(flags.iscmd)
		self.__opt_fail_check(flags)
		return

	def test_A5(self):
		ok = 0
		try:
			flags = ExtKeyParse('','flag<flag.main>##help for flag##','',True)
		except:
			ok = 1
		self.assertTrue( ok > 0)
		return

	def test_A6(self):
		flags = ExtKeyParse('','flag+type<flag.main>##main',{'new':False},False)
		self.assertEqual(flags.cmdname , 'flag')
		self.assertEqual(flags.prefix , 'flag')
		self.assertEqual(flags.function , 'flag.main')
		self.assertTrue(flags.helpinfo is None)
		self.assertTrue(flags.flagname is None)
		self.assertTrue(flags.shortflag is None)
		self.assertFalse(flags.isflag)
		self.assertTrue(flags.iscmd)
		self.assertEqual(flags.type,'command')
		self.assertEqual(flags.value,{'new':False})
		self.__opt_fail_check(flags)
		return

	def test_A7(self):
		flags = ExtKeyParse('','+flag',{},False)
		self.assertEqual(flags.prefix,'flag')
		self.assertEqual(flags.value,{})
		self.assertTrue(flags.cmdname is None)
		self.assertTrue(flags.shortflag is None)
		self.assertTrue(flags.flagname is None)
		self.assertTrue(flags.function is None)
		self.assertTrue(flags.helpinfo is None)
		self.assertTrue(flags.isflag)
		self.assertFalse(flags.iscmd)
		self.assertEqual(flags.type,'prefix')
		self.__opt_fail_check(flags)
		return

	def test_A8(self):
		ok = 0
		try:
			flags = ExtKeyParse('','+flag## help ##',None,False)
		except:
			ok = 1
		self.assertTrue( ok > 0)
		return

	def test_A9(self):
		ok = 0
		try:
			flags = ExtKeyParse('','+flag<flag.main>',None,False)
		except:
			ok = 1
		self.assertTrue( ok > 0)
		return

	def test_A10(self):
		ok = 0
		try:
			flags = ExtKeyParse('','flag|f2','',False)
		except:
			ok = 1
		self.assertTrue( ok > 0)
		return

	def test_A11(self):
		ok = 0
		try:
			flags = ExtKeyParse('','f|f2',None,False)
		except:
			ok = 1
		self.assertTrue( ok > 0)
		return

	def test_A12(self):
		ok =0
		try:
			flags = ExtKeyParse('','$flag|f<flag.main>',{},False)
		except:
			ok = 1
		self.assertTrue ( ok > 0 )
		return

	def test_A13(self):
		ok =0
		try:
			flags = ExtKeyParse('','$flag|f+cc<flag.main>',None,False)
		except:
			ok = 1
		self.assertTrue ( ok > 0 )
		return

	def test_A14(self):
		ok =0
		try:
			flags = ExtKeyParse('','c$','',False)
		except:
			ok = 1
		self.assertTrue ( ok > 0 )
		return

	def test_A15(self):
		ok =0
		try:
			flags = ExtKeyParse('','$$',None,False)
		except:
			ok = 1
		self.assertTrue ( ok > 0 )
		return

	def test_A16(self):
		flags = ExtKeyParse('','$',{ 'nargs':'+'},False)
		self.assertEqual(flags.flagname , '$')
		self.assertEqual(flags.prefix ,'')
		self.assertEqual(flags.type,'args')
		self.assertEqual(flags.value,None)
		self.assertEqual(flags.nargs,'+')
		self.assertTrue(flags.cmdname is None)
		self.assertTrue(flags.shortflag is None)
		self.assertTrue(flags.function is None)
		self.assertTrue(flags.helpinfo is None)
		self.assertTrue(flags.isflag)
		self.assertFalse(flags.iscmd)
		self.__opt_fail_check(flags)
		return

	def test_A17(self):
		flags = ExtKeyParse('type','flag+app## flag help ##',3.3,False)
		self.assertEqual(flags.flagname ,'flag')
		self.assertEqual(flags.prefix , 'type_app')
		self.assertEqual(flags.cmdname , None)
		self.assertEqual(flags.shortflag , None)
		self.assertEqual(flags.function , None)		
		self.assertEqual(flags.type,'float')
		self.assertEqual(flags.value,3.3)
		self.assertEqual(flags.longopt,'--type-app-flag')
		self.assertEqual(flags.shortopt,None)
		self.assertEqual(flags.optdest,'type_app_flag')
		self.assertEqual(flags.helpinfo, ' flag help ')
		self.assertTrue(flags.isflag)
		self.assertFalse(flags.iscmd)
		return

	def test_A18(self):
		flags = ExtKeyParse('','flag+app<flag.main>## flag help ##',{},False)
		self.assertEqual(flags.flagname , None)
		self.assertEqual(flags.prefix , 'flag')
		self.assertEqual(flags.cmdname , 'flag')
		self.assertEqual(flags.shortflag , None)
		self.assertEqual(flags.type ,'command')
		self.assertEqual(flags.value,{})
		self.assertEqual(flags.function ,'flag.main')
		self.assertEqual(flags.helpinfo, ' flag help ')
		self.assertFalse(flags.isflag)
		self.assertTrue(flags.iscmd)
		self.__opt_fail_check(flags)
		return

	def test_A19(self):
		flags = ExtKeyParse('','$flag## flag help ##',{'prefix':'good','value':False,'nargs':2},False)
		self.assertEqual(flags.flagname,'flag')
		self.assertEqual(flags.prefix,'good')
		self.assertEqual(flags.value,False)
		self.assertEqual(flags.type,'bool')
		self.assertEqual(flags.helpinfo,' flag help ')
		self.assertEqual(flags.nargs,2)
		self.assertEqual(flags.shortflag,None)
		self.assertEqual(flags.cmdname,None)
		self.assertEqual(flags.function,None)
		self.assertEqual(flags.longopt,'--good-flag')
		self.assertEqual(flags.shortopt,None)
		self.assertEqual(flags.optdest,'good_flag')
		return

	def test_A20(self):
		ok = False
		try:
			flags = ExtKeyParse('','$',None,False)
		except:
			ok = True
		self.assertEqual(ok,True)
		return

	def test_A21(self):
		flags = ExtKeyParse('command','$## self define ##',{'nargs':'?','value':None},False)
		self.assertEqual(flags.iscmd,False)
		self.assertEqual(flags.isflag,True)
		self.assertEqual(flags.prefix,'command')
		self.assertEqual(flags.flagname,'$')
		self.assertEqual(flags.shortflag,None)
		self.assertEqual(flags.value,None)
		self.assertEqual(flags.type,'args')
		self.assertEqual(flags.nargs,'?')
		self.assertEqual(flags.helpinfo,' self define ')
		self.__opt_fail_check(flags)
		return

def main():
	if '-v' in sys.argv[1:] or '--verbose' in sys.argv[1:]:
		logging.basicConfig(level=logging.INFO,format="%(levelname)-8s [%(filename)-10s:%(funcName)-20s:%(lineno)-5s] %(message)s")	
	unittest.main()

if __name__ == '__main__':
	main()