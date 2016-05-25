#!/usr/bin/python

import os
import sys
import logging
import re
import unittest
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


class ExtKeyParse:
	readwords = ['cmdname','flagname','helpinfo','function','shortflag','prefix','origkey']
	def __parse(self,isflag):
		flagmod = False
		cmdmod = False
		if isflag :
			m = self.__flagexpr.findall(self.__origkey)
			if m and len(m)>0:
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
			m = self.__mustflagexpr.findall(self.__origkey)
			if m and len(m) > 0:
				# we should not get the key type
				raise Exception('(%s) make flag mode with ($) in must flag state'%(self.__origkey))
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
			m = self.__cmdexpr.findall(self.__origkey)
			if m and len(m) > 0:
				assert(not flagmod)
				if '|' in m[0]:
					raise Exception('(%s) cmd(%s) can not accept (|) in '%(self.__origkey,m[0]))
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
		return



	def __init__(self,key,isflag=False):
		self.__cmdname = None
		self.__flagname = None
		self.__helpinfo = None
		self.__function = None
		self.__shortflag = None
		self.__prefix = None
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
		return

	def test_A2(self):
		ok =0
		try:
			flags = ExtKeyParse('$flag|f+type',True)
		except:
			ok = 1
		self.assertTrue ( ok > 0 )
		return

	def test_A3(self):
		ok = 0
		try:
			flags = ExtKeyParse('flag|f',False)
		except:
			ok = 1
		self.assertTrue( ok > 0)
		return

	def test_A4(self):
		flags = ExtKeyParse('flag<flag.main>##help for flag##',False)
		self.assertEqual(flags.cmdname , 'flag')
		self.assertTrue(flags.prefix is None)
		self.assertEqual(flags.function , 'flag.main')
		self.assertEqual(flags.helpinfo,'help for flag')
		self.assertTrue(flags.flagname is None)
		self.assertTrue(flags.shortflag is None)
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
		return

	def test_A7(self):
		flags = ExtKeyParse('+flag',False)
		self.assertEqual(flags.prefix,'flag')
		self.assertTrue(flags.cmdname is None)
		self.assertTrue(flags.shortflag is None)
		self.assertTrue(flags.flagname is None)
		self.assertTrue(flags.function is None)
		self.assertTrue(flags.helpinfo is None)
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



def main():
	if '-v' in sys.argv[1:] or '--verbose' in sys.argv[1:]:
		logging.basicConfig(level=logging.INFO,format="%(levelname)-8s [%(filename)-10s:%(funcName)-20s:%(lineno)-5s] %(message)s")	
	unittest.main()

if __name__ == '__main__':
	main()