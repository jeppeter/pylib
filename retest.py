#!/usr/bin/python

import re
import sys
import extargsparse
import logging

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



def match(args,ctx):
	set_logging(args)
	restr = args.subnargs[0]
	if len(args.subnargs) > 1:
		sarr = args.subnargs[1:]
	else:
		s = read_file(args.infile)
		carr = re.split('\n',s)
		sarr = []
		for l in carr:
			l = l.rstrip('\r')
			sarr.append(l)
	expr = re.compile(restr)
	for instr in sarr:
		if expr.match(instr):
			print ('(%s) match (%s)'%(instr,restr))
		else:
			print ('(%s) not match (%s)'%(instr,restr))
	sys.exit(0)
	return

def findall(args,ctx):
	set_logging(args)
	restr = args.subnargs[0]
	if len(args.subnargs) > 1:
		sarr = args.subnargs[1:]
	else:
		s = read_file(args.infile)
		carr = re.split('\n',s)
		sarr = []
		for l in carr:
			l = l.rstrip('\r')
			sarr.append(l)
	for instr in sarr:
		expr = re.compile(restr)
		m =  expr.findall(instr)
		if m :
			s = '(%s) match (%s)\n'%(instr,restr)
			for i in range(len(m)):
				s += '\t[%d] %s\n'%(i,m[i])
			print ('%s'%(s))
	else:
		print ('(%s) no more for (%s)'%(instr,restr))
	sys.exit(0)
	return

def filefindall(args,ctx):
	fin = sys.stdin
	fout = sys.stdout
	if args.infile is not None:
		fin = open(args.infile,'r')
	if args.outfile is not None:
		fout = open(args.outfile,'w')
	cnt = 1
	exprs = []
	for s in args.subnargs:
		exprs.append(re.compile(s))
	for l in fin:
		l = l.rstrip('\r\n')
		for expr in exprs:
			m = expr.findall(l)
			if m :
				fout.write('[%d]'%(cnt))
				for i in range(len(m)):
					fout.write('\t[%d] %s'%(i,m[i]))
				fout.write('(%s)\n'%(l))
		cnt += 1
	if fin != sys.stdin:
		fin.close()
	fin = None
	if fout != sys.stdout:
		fout.close()
	fout = None
	sys.exit(0)
	return

def filter(args,ctx):
	fin = sys.stdin
	fout = sys.stdout
	if args.infile is not None:
		fin = open(args.infile,'r')
	if args.outfile is not None:
		fout = open(args.outfile,'w')
	cnt = 1
	exprs = []
	for s in args.subnargs:
		exprs.append(re.compile(s))
	for l in fin:
		l = l.rstrip('\r\n')
		matched = 0
		for expr in exprs:
			m = expr.match(l)
			if m :
				matched = 1
				break
		if matched :
			fout.write('%s\n'%(l))
		else:
			fout.write('\n')
		cnt += 1
	if fin != sys.stdin:
		fin.close()
	fin = None
	if fout != sys.stdout:
		fout.close()
	fout = None
	sys.exit(0)
	return

def imatch(args,ctx):
	set_logging(args)
	restr = args.subnargs[0]
	if len(args.subnargs) > 1:
		sarr = args.subnargs[1:]
	else:
		s = read_file(args.infile)
		carr = re.split('\n',s)
		sarr = []
		for l in carr:
			l = l.rstrip('\r')
			sarr.append(l)

	expr = re.compile(restr,re.I)
	for instr in sarr:
		if expr.match(instr):
			print ('(%s) ignore match (%s)'%(instr,restr))
		else:
			print ('(%s) not ignore match (%s)'%(instr,restr))
	sys.exit(0)
	return

def ifindall(args,ctx):
	set_logging(args)
	restr = args.subnargs[0]
	if len(args.subnargs) > 1:
		sarr = args.subnargs[1:]
	else:
		s = read_file(args.infile)
		carr = re.split('\n',s)
		sarr = []
		for l in carr:
			l = l.rstrip('\r')
			sarr.append(l)
	logging.info('restr [%s]'%(restr))
	expr = re.compile(restr,re.I)
	for instr in sarr:
		logging.info('instr [%s]'%(instr))
		m =  expr.findall(instr)
		if m :
			s = '(%s) match (%s)\n'%(instr,restr)
			for i in range(len(m)):
				s += '\t[%d] (%s)\n'%(i,m[i])			
			print ('%s'%(s))
		else:
			print ('(%s) no more for (%s)'%(instr,restr))
	sys.exit(0)
	return

def sub(args,ctx):
	set_logging(args)
	if len(args.subnargs) < 2:
		Usage(3,'sub restr instr [replstr]',ctx)
	if len(args.subnargs) < 3:
		restr = args.subnargs[0]
		instr = args.subnargs[1]
		replstr = ''
	else:
		restr = args.subnargs[0]
		instr = args.subnargs[1]
		replstr = args.subnargs[2]
	newstr = re.sub(restr,replstr,instr)
	print('(%s) sub(%s)(%s) => (%s)'%(instr,restr,replstr,newstr))
	sys.exit(0)
	return

def split(args,ctx):
	set_logging(args)
	restr = args.subnargs[0]
	instr = args.subnargs[1]
	sarr = re.split(restr,instr)
	for i in range(len(sarr)):
		print('[%d] (%s)'%(i,sarr[i]))
	sys.exit(0)
	return

def grpdict_impl(restr,instr,propstr,casesensitive=False):
	if casesensitive:
		expr = re.compile(restr,re.I)
	else:
		expr = re.compile(restr)
	m = expr.match(instr)
	if m is not None:
		groups = m.groupdict(propstr)
		print('(%s) match (%s)'%(instr,restr))
		for k in groups.keys():
			print('   [%s]=(%s)'%(k,groups[k]))
	else:
		print('%s not match (%s)'%(instr,restr))
	return

def grpdict(args,ctx):
	set_logging(args)
	if len(args.subnargs) < 2:
		sys.stderr.write('%s restr instr [propstr]'%(sys.argv[0]))
		sys.exit(5)
	restr = args.subnargs[0]
	instr = args.subnargs[1]
	propstr = ''
	if len(args.subnargs) > 2:
		propstr = args.subnargs[2]
	grpdict_impl(restr,instr,propstr)
	sys.exit(0)
	return

def igrpdict(args,ctx):
	set_logging(args)
	if len(args.subnargs) < 2:
		sys.stderr.write('%s restr instr [propstr]'%(sys.argv[0]))
		sys.exit(5)
	restr = args.subnargs[0]
	instr = args.subnargs[1]
	propstr = ''
	if len(args.subnargs) > 2:
		propstr = args.subnargs[2]
	grpdict_impl(restr,instr,propstr,True)
	sys.exit(0)
	return

def grpfile(args,ctx):
	fin = sys.stdin
	restr = args.subnargs[0]
	propstr = ''
	if len(args.subnargs) > 1:
		propstr = args.subnargs[1]
	if args.infile is not None:
		fin = open(args.infile,'r+')
	for l in fin:
		l = l.rstrip('\r\n')
		l = l.rstrip(' \t')
		l = l.strip(' \t')
		if l.startswith('#'):
			continue
		if len(l) == 0 :
			continue
		instr = l
		grpdict_impl(restr,instr,propstr)
	if fin != sys.stdin:
		fin.close()
	fin = None
	sys.exit(0)
	return

def igrpfile(args,ctx):
	fin = sys.stdin
	restr = args.subnargs[0]
	propstr = ''
	if len(args.subnargs) > 1:
		propstr = args.subnargs[1]
	if args.infile is not None:
		fin = open(args.infile,'r+')
	for l in fin:
		l = l.rstrip('\r\n')
		l = l.rstrip(' \t')
		l = l.strip(' \t')
		if l.startswith('#'):
			continue
		if len(l) == 0 :
			continue
		instr = l
		grpdict_impl(restr,instr,propstr,True)
	if fin != sys.stdin:
		fin.close()
	fin = None
	sys.exit(0)
	return


def search_impl(restr,instr,caseinsensitive= False):
	if caseinsensitive:
		expr = re.compile(restr,re.I)
	else:
		expr = re.compile(restr)
	m = expr.search(instr)
	if m :
		i = 0
		print('(%s) search (%s)'%(restr,instr))
		while True:
			try:
				p = m.group(i)
				print('    [%d] (%s)'%(i,p))
			except:
				break
			i += 1
	else:
		print('(%s) not search (%s)'%(restr,instr))
	return

def search(args,ctx):
	set_logging(args)
	if len(args.subnargs) < 2:
		Usage(3,'%s restr instr...'%(args.command),ctx)
		sys.exit(3)
	restr = args.subnargs[0]
	for s in args.subnargs[1:]:
		search_impl(restr,s)
	sys.exit(0)
	return

def isearch(args,ctx):
	set_logging(args)
	if len(args.subnargs) < 2:
		Usage(3,'%s restr instr...'%(args.command),ctx)
		sys.exit(3)
	restr = args.subnargs[0]
	for s in args.subnargs[1:]:
		search_impl(restr,s,True)
	sys.exit(0)
	return


def Usage(ec,fmt,parser):
	fp = sys.stderr
	if ec == 0 :
		fp = sys.stdout

	if len(fmt) > 0:
		fp.write('%s\n'%(fmt))
	parser.print_help(fp)
	sys.exit(ec)
	return


def gnu_decode_func(funcname):
	decname = funcname
	origname = funcname
	znexpr = re.compile('^(_ZN([0-9]+))(.*)')
	zlexpr = re.compile('^(_ZL([0-9]+))(.*)')
	zexpr = re.compile('^(_Z([0-9]+))(.*)')
	pexpr = re.compile('^(P([0-9]+))(.*)')
	nexpr = re.compile('^([0-9]+)(.*)')
	znm = znexpr.findall(funcname)
	zlm = zlexpr.findall(funcname)
	zm = zexpr.findall(funcname)

	if znm is not None and len(znm) > 0:
		vlen = int(znm[0][1])
		if vlen <= len(znm[0][2]):
			funcname = znm[0][2]
			decname = funcname[:vlen]
			funcname = funcname[vlen:]
	elif zlm is not None and len(zlm) > 0:
		vlen = int(zlm[0][1])
		if vlen <= len(zlm[0][2]):
			funcname = zlm[0][2]
			decname = funcname[:vlen]
			funcname = funcname[vlen:]
	elif zm is not None and len(zm) > 0:
		vlen = int(zm[0][1])
		if vlen <= len(zm[0][2]):
			funcname = zm[0][2]
			decname = funcname[:vlen]
			funcname = funcname[vlen:]
	nm = nexpr.findall(funcname)
	if nm is not None and len(nm) > 0:
		vlen = int(nm[0][0])
		funcname = nm[0][1]
		if vlen <= len(funcname):
			decname += '::'
			decname += funcname[:vlen]
	logging.info('origname [%s] decname[%s]'%(origname, decname))
	return decname


def gnudec_handler(args,parser):
	set_logging(args)
	for c in args.subnargs:
		sys.stdout.write('[%s] decode [%s]\n'%(c,gnu_decode_func(c)))
	sys.exit(0)
	return



command = {
	'verbose|v' : '+',
	'infile|i' : None,
	'outfile|o' : None,
	'match<match>##call re.match func##' : {
		'$' : "+"
	},
	'imatch<imatch>##call re.match with re.I##' : {
		'$' : "+"
	},
	'findall<findall>##re.findall##' : {
		'$' : "+"
	},
	'ifindall<ifindall>##re.findall with re.I##' : {
		'$' : "+"
	},
	'sub<sub>##re.sub##' : {
		'$' : 3
	},
	'split<split>##re.split##' : {
		'$' : 2
	},
	'filefindall<filefindall>##re.findall in file##' : {
		'$' : '+'
	},
	'filter<filter>##re.match for file##' : {
		'$' : '+'
	},
	'grpdict<grpdict>##re.match with groupdict##' : {
		'$' : '+'
	},
	'igrpdict<igrpdict>##re.match ignore case with groupdict##' : {
		'$' : '+'
	},
	'grpfile<grpfile>##re.match with groupdict in file##' : {
		'$' : '+'
	},
	'igrpfile<igrpfile>##re.match ignore case with groupdict in file##' : {
		'$' : '+'
	},
	'search<search>##re.search ##' : {
		'$' : '+'
	},
	'isearch<isearch>##re.search ignore case ##' : {
		'$' : '+'
	},
	"gnufuncdec<gnudec_handler>##funcname ...  to decode gnu function decode##" : {
		"$" : "+"
	}
}

def main():
	global command
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line(command)
	parser.parse_command_line()
	return


if __name__ == '__main__':
	main()