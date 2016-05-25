#!/usr/bin/python

import os
import sys
import logging
import re
import unittest
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


class ExtKeyParse:
	readwords = ['cmdname','flagname','helpinfo','function','shortflag','prefix','origkey','iscmd','isflag']
	def __parse(self,isflag):
		flagmod = False
		cmdmod = False
		flags = None
		if '$' in self.__origkey :
			if self.__origkey[0] != '$':
				raise Exception('(%s) not right format for ($)'%(self.__origkey))
			ok = 1
			try:
				idx = self.__origkey.index('$',1)
				ok = 0
			except:
				pass

			if ok == 0 :
				raise Exception('(%s) has more than 1 ($)'%(self.__origkey))
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
						self.__flagname = flags
					flagmod = True					
				else:
					self.__cmdname = m[0]
					cmdmod = True

		m = self.__funcexpr.findall(self.__origkey)
		if m and len(m):
			if not cmdmod:
				raise Exception('(%s) in flag ($%s) can not accept function'%(self.__origkey,flags))
			self.__function = m[0]
		m = self.__helpexpr.findall(self.__origkey)
		if m and len(m) > 0:
			if flagmod or cmdmod:
				self.__helpinfo = m[0]
			else:
				raise Exception('(%s) can not accept no flag or cmd mode with help(%s)'%(self.__origkey,m[0]))
		m = self.__prefixexpr.findall(self.__origkey)
		if m and len(m) > 0:
			self.__prefix = m[0]
		if flagmod :
			self.__isflag = True
		if cmdmod : 
			self.__iscmd = True
		if not flagmod and not cmdmod:
			self.__isflag = True

		return



	def __init__(self,key,isflag=False):
		self.__cmdname = None
		self.__flagname = None
		self.__helpinfo = None
		self.__function = None
		self.__shortflag = None
		self.__prefix = None
		self.__iscmd = False
		self.__isflag = False
		self.__origkey = key
		self.__helpexpr = re.compile('##([^#]+)##$',re.I)
		self.__cmdexpr = re.compile('^([^\#\<\>\+\$]+)',re.I)
		self.__prefixexpr = re.compile('\+([^\+\#\<\>\|\$ \t]+)',re.I)
		self.__funcexpr = re.compile('<([^\<\>\#\$\| \t]+)>',re.I)
		self.__flagexpr = re.compile('^([^\<\>\#\+\$ \t]+)',re.I)
		self.__mustflagexpr = re.compile('^\$([^\$\+\#\<\>]+)',re.I)
		self.__parse(isflag)
		return

	def __getattr__(self,keyname):
		if keyname in self.__class__.readwords:
			keyname = '_%s__%s'%(self.__class__.__name__,keyname)
		return self.__dict__[keyname]

	def __setattr__(self,keyname,value):
		if keyname in self.__class__.readwords:
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
		return


class UnitTestCase(unittest.TestCase):
	def test_A1(self):
		flags = ExtKeyParse('$flag|f+type',False)
		self.assertEqual(flags.flagname , 'flag')
		self.assertEqual(flags.shortflag , 'f')
		self.assertEqual(flags.prefix , 'type')
		self.assertTrue(flags.cmdname is None)
		self.assertTrue(flags.helpinfo is None)
		self.assertTrue(flags.function is None)
		self.assertTrue(flags.origkey == '$flag|f+type')
		self.assertTrue(flags.isflag)
		self.assertFalse(flags.iscmd)
		return

	def test_A2(self):
		flags = ExtKeyParse('$flag|f+type',True)
		self.assertEqual(flags.flagname,'flag')
		self.assertEqual(flags.shortflag,'f')
		self.assertEqual(flags.prefix,'type')
		self.assertTrue(flags.helpinfo is None)
		self.assertTrue(flags.function is None)
		self.assertTrue(flags.cmdname is None)
		self.assertTrue(flags.isflag)
		self.assertFalse(flags.iscmd)
		return

	def test_A3(self):
		flags = ExtKeyParse('flag|f',False)
		self.assertEqual(flags.flagname,'flag')
		self.assertEqual(flags.shortflag,'f')
		self.assertTrue(flags.prefix is None)
		self.assertTrue(flags.helpinfo is None)
		self.assertTrue(flags.function is None)
		self.assertTrue(flags.cmdname is None)
		self.assertTrue(flags.isflag)
		self.assertFalse(flags.iscmd)
		return

	def test_A4(self):
		flags = ExtKeyParse('flag<flag.main>##help for flag##',False)
		self.assertEqual(flags.cmdname , 'flag')
		self.assertTrue(flags.prefix is None)
		self.assertEqual(flags.function , 'flag.main')
		self.assertEqual(flags.helpinfo,'help for flag')
		self.assertTrue(flags.flagname is None)
		self.assertTrue(flags.shortflag is None)
		self.assertFalse(flags.isflag)
		self.assertTrue(flags.iscmd)
		return

	def test_A5(self):
		ok = 0
		try:
			flags = ExtKeyParse('flag<flag.main>##help for flag##',True)
		except:
			ok = 1
		self.assertTrue( ok > 0)
		return

	def test_A6(self):
		flags = ExtKeyParse('flag+flag<flag.main>##main',False)
		self.assertEqual(flags.cmdname , 'flag')
		self.assertEqual(flags.prefix , 'flag')
		self.assertEqual(flags.function , 'flag.main')
		self.assertTrue(flags.helpinfo is None)
		self.assertTrue(flags.flagname is None)
		self.assertTrue(flags.shortflag is None)
		self.assertFalse(flags.isflag)
		self.assertTrue(flags.iscmd)
		return

	def test_A7(self):
		flags = ExtKeyParse('+flag',False)
		self.assertEqual(flags.prefix,'flag')
		self.assertTrue(flags.cmdname is None)
		self.assertTrue(flags.shortflag is None)
		self.assertTrue(flags.flagname is None)
		self.assertTrue(flags.function is None)
		self.assertTrue(flags.helpinfo is None)
		self.assertTrue(flags.isflag)
		self.assertFalse(flags.iscmd)
		return

	def test_A8(self):
		ok = 0
		try:
			flags = ExtKeyParse('+flag## help ##',False)
		except:
			ok = 1
		self.assertTrue( ok > 0)
		return

	def test_A9(self):
		ok = 0
		try:
			flags = ExtKeyParse('+flag<flag.main>',False)
		except:
			ok = 1
		self.assertTrue( ok > 0)
		return

	def test_A10(self):
		ok = 0
		try:
			flags = ExtKeyParse('flag|f2',False)
		except:
			ok = 1
		self.assertTrue( ok > 0)
		return

	def test_A11(self):
		ok = 0
		try:
			flags = ExtKeyParse('f|f2',False)
		except:
			ok = 1
		self.assertTrue( ok > 0)
		return

	def test_A12(self):
		ok =0
		try:
			flags = ExtKeyParse('$flag|f<flag.main>',False)
		except:
			ok = 1
		self.assertTrue ( ok > 0 )
		return

	def test_A13(self):
		ok =0
		try:
			flags = ExtKeyParse('$flag|f+cc<flag.main>',False)
		except:
			ok = 1
		self.assertTrue ( ok > 0 )
		return

	def test_A14(self):
		ok =0
		try:
			flags = ExtKeyParse('c$',False)
		except:
			ok = 1
		self.assertTrue ( ok > 0 )
		return

	def test_A15(self):
		ok =0
		try:
			flags = ExtKeyParse('$$',False)
		except:
			ok = 1
		self.assertTrue ( ok > 0 )
		return

	def test_A16(self):
		flags = ExtKeyParse('$',False)
		self.assertEqual(flags.flagname , '$')
		self.assertTrue(flags.prefix is None)
		self.assertTrue(flags.cmdname is None)
		self.assertTrue(flags.shortflag is None)
		self.assertTrue(flags.function is None)
		self.assertTrue(flags.helpinfo is None)
		self.assertTrue(flags.isflag)
		self.assertFalse(flags.iscmd)
		return

	def test_A17(self):
		flags = ExtKeyParse('flag+flag## flag help ##',False)
		self.assertTrue(flags.flagname is None)
		self.assertEqual(flags.prefix , 'flag')
		self.assertEqual(flags.cmdname , 'flag')
		self.assertTrue(flags.shortflag is None)
		self.assertTrue(flags.function is None)
		self.assertEqual(flags.helpinfo, ' flag help ')
		self.assertFalse(flags.isflag)
		self.assertTrue(flags.iscmd)

		flags.change_to_flag()
		self.assertEqual(flags.flagname ,'flag')
		self.assertEqual(flags.prefix , 'flag')
		self.assertTrue(flags.cmdname is None)
		self.assertTrue(flags.shortflag is None)
		self.assertTrue(flags.function is None)
		self.assertEqual(flags.helpinfo, ' flag help ')
		self.assertTrue(flags.isflag)
		self.assertFalse(flags.iscmd)
		return

	def test_A18(self):
		flags = ExtKeyParse('flag+flag<flag.main>## flag help ##',False)
		self.assertTrue(flags.flagname is None)
		self.assertEqual(flags.prefix , 'flag')
		self.assertEqual(flags.cmdname , 'flag')
		self.assertTrue(flags.shortflag is None)
		self.assertEqual(flags.function ,'flag.main')
		self.assertEqual(flags.helpinfo, ' flag help ')
		self.assertFalse(flags.isflag)
		self.assertTrue(flags.iscmd)

		ok = 0
		try:
			flags.change_to_flag()
		except:
			ok = 1
		self.assertTrue(ok > 0)
		return


def main():
	if '-v' in sys.argv[1:] or '--verbose' in sys.argv[1:]:
		logging.basicConfig(level=logging.INFO,format="%(levelname)-8s [%(filename)-10s:%(funcName)-20s:%(lineno)-5s] %(message)s")	
	unittest.main()

if __name__ == '__main__':
	main()