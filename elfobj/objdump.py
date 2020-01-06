#! /usr/bin/env python

import extargsparse
import sys
import os
import logging
import re
import shutil


def set_logging(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	if logging.root is not None and len(logging.root.handlers) > 0:
		logging.root.handlers = []
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return



def read_file(infile=None):
	fin = sys.stdin
	if infile is not None:
		fin = open(infile,'r+b')
	rets = ''
	for l in fin:
		s = l
		if 'b' in fin.mode:
			if sys.version[0] == '3':
				s = l.decode('utf-8')
		rets += s

	if fin != sys.stdin:
		fin.close()
	fin = None
	return rets

def read_file_callback(handlefn,ctx,infile=None):
	fin = sys.stdin
	if infile is not None:
		fin = open(infile,'r+b')
	for l in fin:
		s = l
		if 'b' in fin.mode:
			if sys.version[0] == '3':
				s = l.decode('utf-8')
		handlefn(s,ctx)
	if fin != sys.stdin:
		fin.close()
	fin = None
	return

class CountNumber(object):
	def __init__(self):
		self.cnt = 0
		return

	def read_f(self,s,ctx):
		s = s.rstrip('\r\n')
		sys.stdout.write('inner[%s]%s\n'%(self.cnt,s))
		self.cnt += 1
		return

def callfile_read(s,ctx):
	s = s.rstrip('\r\n')
	sys.stdout.write('[%d]%s\n'%(ctx.cnt, s))
	ctx.cnt += 1
	return

def callback_handler(args,parser):
	set_logging(args)
	ctx = CountNumber()
	read_file_callback(ctx.read_f,ctx,args.input)
	sys.exit(0)
	return

class Caller(object):
	def __init__(self,func,offset,lineno):
		self.function = func
		self.offset = offset
		self.lineno = lineno
		return

	def __format(self):
		return 'Caller<%s:0x%x:line(%d)>'%(self.function,self.offset,self.lineno)

	def __str__(self):
		return self.__format()

	def __repr__(self):
		return self.__format()

class Callee(object):
	def __init__(self,func,offset,lineno):
		self.function = func
		self.offset = offset
		self.lineno = lineno
		return

	def __format(self):
		return 'Callee<%s:0x%x:line(%d)>'%(self.function,self.offset,self.lineno)

	def __str__(self):
		return self.__format()

	def __repr__(self):
		return self.__format()


class ElfFunctions(object):
	def __init__(self,funcs):
		logging.info(' ')
		self.functions = funcs
		self.curfunc = None
		self.callers = dict()
		self.calloffsets = dict()
		self.callmaps = dict()
		self.lineno = 0
		self.funcstartexpr = re.compile('^([0-9a-fA-F]+)\\s+<([^>]+)>:')
		self.funcoffsetexpr = []
		self.funccallexpr = []
		self.bytecodeoffsetexpr = re.compile('^([0-9a-fA-F]+):')
		for f in funcs:
			self.funcoffsetexpr.append(re.compile('\\s<(%s)\\+0[xX]([0-9a-fA-F]+)>$'%(f)))
			self.funccallexpr.append(re.compile('\\s<(%s)>$'%(f)))
		logging.info(' ')
		return

	def parse_caller(self,s,ctx):
		s = s.rstrip('\r\n')
		self.lineno += 1
		m = self.funcstartexpr.findall(s)
		if m is not None and len(m) > 0 and len(m[0]) > 1:
			offset = int(m[0][0],16)
			name = m[0][1]
			caller = Caller(name,offset,self.lineno)
			if name in self.callers:
				logging.error('%s already in %s new [%s]'%(name, self.callers[name],caller))
			self.callers[name] = caller
			self.curfunc = name
		return

	def parse_callmap(self,s,ctx):
		s = s.rstrip('\r\n')
		self.lineno += 1
		if (self.lineno % 50000) == 0 :
			logging.info('[%d]%s'%(self.lineno,s))
		m = self.funcstartexpr.findall(s)
		if m is not None:
			if len(m) > 0 and len(m[0]) > 1:
				self.curfunc = m[0][1]
				return

		if self.curfunc is None:
			# no function handle
			return
		idx = 0
		matched = 0
		while idx < len(self.funcoffsetexpr):
			f = self.funcoffsetexpr[idx]
			fname = self.functions[idx]
			m = f.findall(s)
			if m is not None:
				assert(self.callers[self.curfunc])
				m2 = self.bytecodeoffsetexpr.findall(s)
				if m2 is not None and len(m2) > 0:
					fileoffset = int(m2[0],16)
					if fname not in self.calloffsets:
						self.calloffsets[fname] = []
					callee =Callee(self.curfunc, fileoffset - self.callers[self.curfunc].offset,self.lineno)
					self.calloffsets[fname].append(callee)
					matched += 1
			idx += 1
		if matched > 0:
			return
		idx = 0
		while idx < len(self.funccallexpr):
			f = self.funccallexpr[idx]
			fname = self.functions[idx]
			m = f.findall(s)
			if m is not None:
				assert(self.callers[self.curfunc])
				m2 = self.bytecodeoffsetexpr.findall(s)
				if m2 is not None and len(m2) > 0:
					fileoffset = int(m2[0],16)
					if fname not in self.callmaps:
						self.callmaps[fname] = []
					callee = Callee(self.curfunc,fileoffset -self.callers[self.curfunc].offset, self.lineno)
					self.callmaps[fname].append(callee)
					matched += 1
			idx += 1
		return



def callmap_handler(args,parser):
	set_logging(args)
	logging.info('subnargs %s'%(args.subnargs))
	elffunc = ElfFunctions(args.subnargs)
	logging.info(' elffunc [%s]'%(elffunc))
	read_file_callback(elffunc.parse_caller,elffunc,args.input)
	elffunc.curfunc = None
	elffunc.lineno = 0

	read_file_callback(elffunc.parse_callmap, elffunc,args.input)
	for f in args.subnargs:
		num = 0
		if f in elffunc.callmaps:
			num = len(elffunc.callmaps[f])
		sys.stdout.write('%s:[%d]\n'%(f,num))
		if f in elffunc.callmaps:
			idx = 0
			for m in self.callmaps[f]:
				sys.stdout.write('    [%d]%s\n'%(idx,m))
				idx += 1				
	sys.exit(0)
	return


def main():
	commandline='''
	{
		"verbose|v" : "+",
		"input|i" : null,
		"callback<callback_handler>##   to test for call back##" : {
			"$" : 0
		},
		"callmap<callmap_handler>## functions...  to ##" : {
			"$" : "+"
		}

	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser.parse_command_line(None,parser)
	raise Exception('can not reach here')
	return

if __name__ == '__main__':
	main()