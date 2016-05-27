#!/usr/bin/python

################################################
##  this file is for tce handle in python module
##
################################################
import re
import os
import sys
import argparse
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import dbgexp
import cmdpack
import tcebase
import maphandle
import extargsparse



class TceDepBase(tcebase.TceBase):
	def __init__(self):
		self.__deps = []
		return

	def get_input(self,l):
		l = self.strip_line(l)
		if len(l) > 0:
			if l not in self.__deps:
				self.__deps.append(l)
		return

	def get_depend(self):
		return self.__deps


class TceAvailBase(tcebase.TceBase):
	def __init__(self):
		self.__avails = []
		self.__started = False
		self.__htmlformat = False
		self.__htmlexpr = re.compile('^<html>.*',re.I)
		self.__ahrefexpr = re.compile('^<a\s+href=("[^"]+")>([^<>]+)</a>',re.I)
		self.__tczexpr = re.compile('(.*)\.tcz$',re.I)
		return

	def __get_tcz(self,l):
		m = self.__tczexpr.findall(l)
		if m and len(m) > 0:
			if m[0] not in self.__avails:
				self.__avails.append(m[0])
		return

	def __get_html_tcz(self,l):
		m = self.__ahrefexpr.findall(l)
		if m and len(m) > 0:
			if len(m[0]) > 1:
				self.__get_tcz(m[0][1])
		return

	def get_input(self,l):
		l = self.strip_line(l)
		if not self.__started :
			self.__started = True
			if self.__htmlexpr.match(l):
				self.__htmlformat = True
			if not self.__htmlformat :
				self.__get_tcz(l)
			return
		if not self.__htmlformat:
			self.__get_tcz(l)
			return
		else:
			self.__get_html_tcz(l)
			return
		return

	def get_avail(self):
		return self.__avails

class TceTreeBase(tcebase.TceBase):
	def __init__(self,args):
		self.__lineno = 0
		self.__deppaths=[]
		self.__deplists = []
		self.__curdeps = []
		self.__curspace = 0
		self.__depmaps = dict()
		self.__tczexpr = re.compile('\s*(.+)\.tcz$',re.I)
		self.set_tce_attrs(args)
		return

	def set_dep_map(self,depmaps):
		self.__depmaps = depmaps
		return

	def __count_space(self,l):
		cnt = 0
		for p in l:
			if p != ' ':
				break
			cnt += 1
		return cnt

	def __pop_out_inner(self):
		if len(self.__deppaths) == 0:
			return False
		assert(len(self.__deppaths) == (len(self.__deplists) + 1))
		depmain = self.__deppaths.pop()
		deps = self.__curdeps
		if depmain not in self.__depmaps.keys():
			self.__depmaps[depmain] = []
		for p in deps:
			if p not in self.__depmaps[depmain]:
				self.__depmaps[depmain].append(p)
		self.__curdeps = []
		if len(self.__deplists) > 0:
			self.__curdeps = self.__deplists.pop()
		return True

	def __pop_out(self,cnt,pkg):
		if len(self.__deppaths) == 0:
			return
		assert(len(self.__deppaths) > 0)
		assert(len(self.__curdeps) > 0)
		retval = True
		while cnt < len(self.__deppaths) and retval:
			retval = self.__pop_out_inner()
		if cnt == 0:
			assert(len(self.__deppaths) == 0)
			assert(len(self.__deplists) == 0)
			assert(len(self.__curdeps) == 0)
			if pkg is not None:
				self.__deppaths.append(pkg)
		else:
			if pkg is not None:
				self.__curdeps.append(pkg)
			else:
				retval = True
				while retval:
					retval = self.__pop_out_inner()
		return

	def __push_in(self,pkg):
		assert(pkg is not None)
		assert(len(self.__curdeps) > 0)
		depmain = self.__curdeps[-1]
		self.__deplists.append(self.__curdeps)
		self.__deppaths.append(depmain)
		self.__curdeps = []
		self.__curdeps.append(pkg)
		return

	def get_input(self,l):
		l = l.rstrip('\r\t\n ')
		self.__lineno += 1
		if len(l) == 0 :
			self.__pop_out(0,None)
			return
		m = self.__tczexpr.findall(l)
		if m is None or len(m) == 0:
			logging.warn('(%s) not valid tcz'%(l))
			return
		cnt = self.__count_space(l)
		if (cnt % self.tce_perspace) != 0 :
			logging.warn('(%s) not %d mod 0'%(l,self.tce_perspace))
			return
		curtcz = m[0]
		nstep = cnt / self.tce_perspace
		if nstep > len(self.__deppaths):
			self.__push_in(curtcz)
		elif nstep < len(self.__deppaths):
			self.__pop_out(nstep,curtcz)
		else:
			if nstep == 0:
				assert(len(self.__deppaths) == 0)
				if curtcz is not None:
					self.__deppaths.append(curtcz)
			else:
				if curtcz not in self.__curdeps:
					self.__curdeps.append(curtcz)
		return

	def get_dep_map(self):
		retval = True
		while retval:
			retval = self.__pop_out(0,None)
		return self.__depmaps

class TceTreeFormat(tcebase.TceBase):
	def __init__(self,args):
		self.__depmaps = dict()
		self.set_tce_attrs(args)
		self.__callidx = 0
		return

	def __format_out(self):
		s = ''
		cnt = 0
		for p in self.__depmaps.keys():
			s += '%s.tcz\n'%(p)
			logging.info('(%s) = %s'%(p,self.__depmaps[p]))
			for cp in self.__depmaps[p]:
				s += ' ' * self.tce_perspace
				s += '%s.tcz\n'%(cp)
			logging.info('cnt(%d)'%(cnt))
			cnt += 1
		return s

	def __format_pkg_out(self,spaces,pkg):
		s = ''
		if spaces > 50:
			logging.error('most calling (%s)'%(pkg))
			return ''
		if pkg in self.__depmaps.keys():
			s += ' '* spaces * self.tce_perspace
			s += '%s.tcz\n'%(pkg)
			deps = self.__depmaps[pkg]
			for cp in deps:
				s += self.__format_pkg_out(spaces+1,cp)
		return s

	def format_out(self,depmaps=None,pkg=None):
		traversed = []
		if depmaps is not None:
			self.__depmaps = depmaps
		if pkg is None:
			s = self.__format_out()
		else:
			s = self.__format_pkg_out(0,pkg)
		return s


def filter_context(instr,context):
	context.get_input(instr)
	return


class TceDep(TceDepBase):
	def __init__(self,args):
		super(TceDep,self).__init__()
		self.set_tce_attrs(args)
		return

	def get_deps(self,pkg):		
		depfile = '%s/%s/%s.tcz.dep'%(self.tce_root,self.tce_optional_dir,pkg)
		cmd = ''
		if os.path.isfile(depfile):
			cmd += '"%s" "%s" "%s"'%(self.tce_sudoprefix,self.tce_cat,depfile)
		else:
			# nothing is ,so we download from the file
			cmd += '"%s" -q -O - %s/%s/%s/tcz/%s.tcz.dep'%(self.tce_wget,self.tce_mirror,self.tce_tceversion,self.tce_platform,pkg)
		retval = cmdpack.run_command_callback(cmd,filter_context,self)
		if retval != 0:
			if retval != 8 :
				raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
			else:
				logging.warn('%s(%s) no dep'%(pkg,cmd))
				return []
		return self.get_depend()


class TceAvail(TceAvailBase):
	def __init__(self,args):
		super(TceAvail,self).__init__()
		self.set_tce_attrs(args)

	def get_avails(self):
		cmd = '"%s" -q -O - %s/%s/%s/tcz/'%(self.tce_wget,self.tce_mirror,self.tce_tceversion,self.tce_platform)
		logging.info('run (%s)'%(cmd))
		retval = cmdpack.run_command_callback(cmd,filter_context,self)
		if retval != 0:
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
		return self.get_avail()

class TceTree(TceTreeBase):
	def __init__(self,args):
		super(TceTree,self).__init__(args)
		return

	def get_dep_tree(self,treefile,depmaps):
		cmd = '"%s" "%s"'%(self.tce_cat,treefile)
		self.set_dep_map(depmaps)
		retval = cmdpack.run_command_callback(cmd,filter_context,self)
		if retval != 0 :
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
		return self.get_dep_map()


def get_available(args):
	tceavail = TceAvail(args)
	return tceavail.get_avails()

def get_all_deps(args,maps):
	avails = get_available(args)
	for p in avails:
		if p not in maps.keys():
			tcedep = TceDep(args)
			maps[p] = tcedep.get_deps(p)
	return maps

def get_dep(args,pkgs,depmap):
	scaned = 0
	alldeps = []
	for p in pkgs:
		if p in depmap.keys():
			continue
		tcedep = TceDep(args)
		depmap[p] = tcedep.get_deps(p)

	for p in pkgs:
		retlists = maphandle.form_map_list(depmap,p)
		for cp in retlists:
			if cp not in alldeps:
				alldeps.append(cp)
	slen = len(alldeps)
	while True:
		for p in alldeps:
			if p not in depmap.key():
				tcedep = TceDep(args)
				depmap[p] = tcedep.get_deps()
		newdeps = []
		for p in alldeps:
			newdeps.append(p)

		for p in alldeps:
			retlists = maphandle.form_map_list(depmap,p)
			for cp in retlists:
				if cp not in newdeps:
					newdeps.append(cp)
		clen = newdeps
		if clen == slen:
			break
		alldeps = []
		for p in newdeps:
			alldeps.append(p)
		slen = clen
	return alldeps,depmap

def transform_to_rdep(depmaps,rdepmaps):
	for p in depmaps.keys():
		deps = depmaps[p]
		for cp in deps:
			if cp not in rdepmaps.keys():
				rdepmaps[cp] = []
			if p not in rdepmaps[cp]:
				rdepmaps[cp].append(p)
	return depmaps,rdepmaps

def get_rdep(args,pkgs,depmaps,rdepmaps):
	scaned = 0
	for p in pkgs:
		if p not in rdepmaps.keys() and scaned == 0:
			depmaps = get_all_deps(args,depmaps)
			scaned = 1
	if scaned > 0:
		depmaps,rdepmaps = transform_to_rdep(depmaps,rdepmaps)
	allrdeps = []
	for p in pkgs:
		if p not in rdepmaps.keys():
			continue
		rdeps = rdepmaps[p]
		for cp in rdeps:
			if cp not in allrdeps:
				allrdeps.append(cp)
	slen = len(allrdeps)
	while True:
		for p in allrdeps:
			if p not in rdepmaps.keys() :
				if scaned > 0:
					continue
				else:
					depmaps = get_all_deps(args,depmaps)
					depmaps,rdepmaps = transform_to_rdep(depmaps,rdepmaps)
					scaned = 1
			if p in rdepmaps.keys():
				rdeps = rdepmaps[p]
				for cp in rdeps:
					if cp not in allrdeps:
						allrdeps.append(cp)
		clen = len(allrdeps)
		if clen == slen:
			break
		slen = clen
	return allrdeps,depmaps,rdepmaps

def get_dep_tree(args,treefiles,listpkg=None):
	deptree = TceTree(args)	
	depmaps = dict()
	for p in treefiles:
		depmaps = deptree.get_dep_tree(p,depmaps)
	return depmaps

def format_tree(args,depmaps,listpkg=None,outfile=None):
	formattree = TceTreeFormat(args)
	s = formattree.format_out(depmaps,listpkg)
	fp = sys.stdout
	if outfile is not None:
		fp = open(outfile,'w')
	fp.write(s)
	if fp != sys.stdout:
		fp.close()
	fp = None
	return


def Usage(ec,fmt,parser):
	fp = sys.stderr
	if ec == 0 :
		fp = sys.stdout

	if len(fmt) > 0:
		fp.write('%s\n'%(fmt))
	parser.print_help(fp)
	sys.exit(ec)

def set_log_level(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	elif args.verbose >= 1 :
		loglvl = logging.WARN
	# we delete old handlers ,and set new handler
	delone = True
	logger = logging.getLogger()
	while delone:
		delone = False
		for hdl in logger.handlers:
			logger.removeHandler(hdl)
			delone = True	
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return

def out_pkgs(args,pkgs):
	maphandle.format_output(args.subnargs,pkgs,'::%s::'%(args.subcommand))
	return

def out_map(args,maps):
	maphandle.output_map(args.subnargs,maps,'::%s::'%(args.subcommand))
	return

def dep_tce(args,context):
	set_log_level(args)

tce_dep_command_line = {
	'dep<dep_tce>## tce dep list ##' : {
		'$' : '+'
	},
	'rdep<rdep_tce>## tce rdep list##' : {
		'$' : '+'
	},
	'tree<tree_tce>## tce tree list##' : {
		'list|l' : [],
		'$' : '+'
	},
	'inst<inst_tce>## tce installed list##' : {
		'$' : 0
	},
	'all<all_tce>## all tce available ##' : {
		'$' : 0
	}
}


def main():
	usage_str='%s [options] {commands} pkgs...'%(sys.argv[0])
	parser = extargsparse.ExtArgsParse(description='dpkg encapsulation',usage=usage_str)
	parser = tcebase.add_tce_args(parser)
	parser.load_command_line(tce_dep_command_line)
	args = parser.parse_command_line()

	sub_parser = parser.add_subparsers(help='',dest='command')
	dep_parser = sub_parser.add_parser('dep',help='get depends')
	dep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get depend')
	rdep_parser = sub_parser.add_parser('rdep',help='get rdepends')
	rdep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get rdepend')
	tree_parser = sub_parser.add_parser('tree',help='get dep from tree files')
	tree_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='files parse dep tree')
	tree_parser.add_argument('--list',dest='listpkg',action='store',default=None,help='specified the list pkg')
	inst_parser = sub_parser.add_parser('inst',help='get installed')
	all_parser = sub_parser.add_parser('all',help='get all available')
	args = parser.parse_args()	
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	args = tcebase.load_tce_jsonfile(args)
	getpkgs = []
	maps = dict()
	maps2 = dict()
	if args.command == 'dep':
		if len(args.pkgs) < 1:
			Usage(3,parser,'%s need a package at least'%(args.command))
		getpkgs,maps = get_dep(args,args.pkgs,maps)
	elif args.command == 'rdep':
		if len(args.pkgs) < 1:
			Usage(3,parser,'%s need a package at least'%(args.command))

		getpkgs,maps2,maps=get_rdep(args,args.pkgs,maps2,maps)
	elif args.command == 'inst':
		pass
	elif args.command == 'tree':
		if len(args.pkgs) < 1:
			Usage(3,parser,'%s need a package at least'%(args.command))
		maps = get_dep_tree(args,args.pkgs)
		format_tree(args,maps,args.listpkg)
	elif args.command == 'all' :
		getpkgs = get_available(args)
		args.pkgs = ''
	else:
		raise dbgexp.DebugException(dbgexp.ERROR_INVALID_PARAMETER,'command (%s) not recognized'%(args.command))
	
	if args.command == 'all' or args.command == 'dep'  or args.command == 'rdep':
		maphandle.format_output(args.pkgs,getpkgs,'::%s::'%(args.command))
	if args.command == 'dep' or args.command == 'rdep' :
		maphandle.output_map(args.pkgs,maps,'::%s::'%(args.command))
	return

if __name__ =='__main__':
	main()
