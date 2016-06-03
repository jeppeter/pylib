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
		self.__lineno = 0
		self.__validline = False
		self.__tczexpr = re.compile('(.+)\.tcz$',re.I)
		return

	def get_input(self,l):
		self.__lineno += 1
		if self.__lineno > 1  and not self.__validline:
			# we can not get this
			return
		else:
			sarr  = re.split(':',l)
			if len(sarr) > 1:
				logging.warn('get input error(%s)'%(l))
				self.__validline = False
				self.__deps = []
				return
			self.__validline = True
		l = self.strip_line(l)
		if len(l) > 0:
			m = self.__tczexpr.findall(l)
			if m and len(m) > 0:
				if m[0] not in self.__deps:
					self.__deps.append(m[0])
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
		self.__validline = False
		self.__lineno = 0
		self.__deppaths=[]
		self.__deplists = []
		self.__curdeps = []
		self.__curspace = 0
		self.__depmaps = dict()
		self.__origmaps = dict()
		self.__tczexpr = re.compile('\s*(.+)\.tcz$',re.I)
		self.set_tce_attrs(args)
		return

	def set_dep_map(self,depmaps):
		self.__depmaps = depmaps
		self.__origmaps = dict()
		for p in depmaps.keys():
			self.__origmaps[k] = depmaps[k]
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
		assert(len(self.__curdeps) >= 0)
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
		if self.__lineno > 1 and not self.__validline :
			return
		else:
			# we should test whether it is format ok
			sarr = re.split(':',l)
			if len(sarr) > 1 :
				logging.warn('get tree error(%s)'%(l))
				self.__validline = False
				self.__depmaps = self.__origmaps
				return
			self.__validline = True
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


class TceInstBase(tcebase.TceBase):
	def __init__(self,args):
		super(TceInstBase,self).__init__()
		self.set_tce_attrs(args)
		self.__tczexpr = re.compile('(.+)\.tcz$',re.I)
		self.__insts = []
		return

	def get_input(self,l):
		l = l.rstrip(' \t\r\n')
		l = l.strip(' \t')
		m = self.__tczexpr.findall(l)
		if m and len(m) > 0:
			if m[0] not in self.__insts:
				self.__insts.append(m[0])
		return

	def get_inst(self):
		return self.__insts


class TceListBase(tcebase.TceBase):
	def __init__(self,args):
		super(TceListBase,self).__init__()
		self.set_tce_attrs(args)
		self.__lists = []
		return

	def get_input(self,l):
		l = l.rstrip(' \t\r\n')
		if len(l) > 0:
			if l not in self.__lists:
				self.__lists.append(l)
		return

	def get_lists(self):
		return self.__lists

class TceListFileBase(tcebase.TceBase):
	def __init__(self,args):
		super(TceListFileBase,self).__init__()
		self.set_tce_attrs(args)
		self.__listmap = dict()
		self.__fileexpr = re.compile('^[\s]+(.+)$',re.I)
		self.__pathexpr = re.compile('.*/.*',re.I)
		self.__tczexpr = re.compile('^(.+)\.tcz$',re.I)
		self.__curtcz = None
		self.__curfiles = []
		self.__lineno = 0
		return

	def __set_tczfiles(self,pkgname,pkgfiles):
		if pkgname is None:
			return
		if pkgname not in self.__listmap.keys():
			self.__listmap[pkgname] = pkgfiles
		else:
			for p in pkgfiles:
				if p not in self.__listmap[pkgname]:
					self.__listmap[pkgname].append(p)
		return

	def __flush_tczfiles(self,curtcz):
		self.__set_tczfiles(self.__curtcz,self.__curfiles)
		self.__curtcz = curtcz
		self.__curfiles = []
		return

	def get_input(self,l):
		self.__lineno += 1
		l = l.rstrip('\t \r\n')
		m = self.__tczexpr.findall(l)
		if m and len(m) > 0:
			self.__flush_tczfiles(m[0])
			return

		m = self.__fileexpr.findall(l)
		if m and len(m) > 0:
			if self.__pathexpr.match(m[0]):
				if self.__curtcz is not None:
					if m[0] not in self.__curfiles:
						self.__curfiles.append(m[0])
			else:
				logging.warn('[%d](%s) not path'%(self.__lineno,l))
			return
		return

	def __get_lists_clear(self,pkgname):
		if pkgname in self.__listmap.keys():
			self.__listmap[pkgname].sort()
			cont = True
			while cont:
				cont = False
				lastp = None
				for p in self.__listmap[pkgname]:
					if lastp is not None:
						if p.startswith('%s/'%(lastp)):
							logging.warn('<%s> delete %s'%(pkgname,lastp))
							self.__listmap[pkgname].remove(lastp)
							cont = True
							break
					lastp = p
					lastp = lastp.rstrip('/\\')
			return self.__listmap[pkgname]
		return []



	def get_list_files(self,pkg):
		self.__flush_tczfiles(None)
		return self.__get_lists_clear(pkg)

	def get_list_map(self):
		self.__flush_tczfiles(None)
		for p in self.__listmap.keys():
			self.__get_lists_clear(p)
		return self.__listmap

	def format_list_map(self,listmap):
		keys = []
		for p in listmap.keys():
			if p not in keys:
				keys.append(p)
		keys.sort()
		s = ''
		for p in keys:
			s += '%s.tcz\n'%(p)
			cnt = 0
			for cp in listmap[p]:
				s += ' ' * self.tce_perspace
				s += '%s\n'%(cp)
				cnt += 1
			if cnt == 0 :
				logging.warn('<%s> empty'%(p))
		return s




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


class TceWgetDep(TceDepBase):
	def __init__(self,args):
		super(TceWgetDep,self).__init__()
		self.set_tce_attrs(args)
		return

	def get_deps(self,pkg):		
		depfile = '%s/%s/%s.tcz.dep'%(self.tce_root,self.tce_optional_dir,pkg)
		cmd = ''
		if os.path.isfile(depfile):
			cmd += '"%s" "%s" "%s"'%(self.tce_sudoprefix,self.tce_cat,depfile)
		else:
			# nothing is ,so we download from the file
			cmd += '"%s" --timeout=%d -q -O - %s/%s/%s/tcz/%s.tcz.dep'%(self.tce_wget,self.tce_timeout,self.tce_mirror,self.tce_tceversion,self.tce_platform,pkg)
		cont = True
		tries = 0
		logging.info('run (%s)'%(cmd))
		while cont:
			cont = False
			retval = cmdpack.run_command_callback(cmd,filter_context,self)
			if retval != 0:
				if retval != 8 and tries > self.tce_maxtries:
					raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
				elif retval != 8:
					logging.warn('%s(%s) no dep'%(pkg,cmd))
					tries += 1
					cont = True
				else:
					return []
		return self.get_depend()


class TceAvail(TceAvailBase):
	def __init__(self,args):
		super(TceAvail,self).__init__()
		self.set_tce_attrs(args)

	def get_avails(self):
		cmd = '"%s" --timeout=%d -q -O - "%s/%s/%s/tcz/"'%(self.tce_wget,self.tce_timeout,self.tce_mirror,self.tce_tceversion,self.tce_platform)
		logging.info('run (%s)'%(cmd))
		cont = True
		tries = 0
		while cont:
			cont = False
			retval = cmdpack.run_command_callback(cmd,filter_context,self)
			if retval != 0 and tries > self.tce_maxtries:
				raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
			elif retval != 0 :
				cont = True
				tries += 1
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

class TceWgetTree(TceTreeBase):
	def __init__(self,args):
		super(TceWgetTree,self).__init__(args)
		return

	def get_dep_tree(self,pkgname,depmaps):
		cmd = '"%s" --timeout=%d -q -O - "%s/%s/%s/tcz/%s.tcz.tree"'%(self.tce_wget,self.tce_timeout,self.tce_mirror,self.tce_tceversion,self.tce_platform,pkgname)
		logging.info('run (%s)'%(cmd))
		tries = 0
		cont = True
		while cont:
			cont = False
			self.set_dep_map(depmaps)
			retval = cmdpack.run_command_callback(cmd,filter_context,self)
			if retval != 0 :
				if retval != 8 and tries > self.tce_maxtries:
					raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
				elif retval != 8:
					logging.warn('can not get %s tree'%(pkgname))
					tries += 1
					cont = True
		return self.get_dep_map()


class TceInst(TceInstBase):
	def __init__(self,args):
		super(TceInst,self).__init__(args)
		self.set_tce_attrs(args)
		return

	def get_insts(self):
		cmd = '"%s" "%s/onboot.lst"'%(self.tce_cat,self.tce_optional_dir)
		logging.info('cmd (%s)'%(cmd))
		retval = cmdpack.run_command_callback(cmd,filter_context,self)
		if retval != 0:
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
		return self.get_inst()

	def __write_inst_inner(self,lstfile,s):
		with open(lstfile,'w+') as f:
			f.write(s)
		return

	def __write_inst(self,pkgs):
		s = ''
		pkgs.sort()
		for p in pkgs:
			s += '%s.tcz\n'%(p)

		self.__write_inst_inner('%s/xbase.lst'%(self.tce_optional_dir),s)
		self.__write_inst_inner('%s/copy2fs.lst'%(self.tce_optional_dir),s)
		self.__write_inst_inner('%s/onboot.lst'%(self.tce_optional_dir),s)
		return


	def add_inst(self,pkgs):
		insts = self.get_insts()
		added = 0
		if isinstance(pkgs,list):
			for p in pkgs:
				if p not in insts:
					added += 1
					insts.append(p)
		else:
			if pkgs not in insts:
				insts.append(pkgs)
				added += 1
		if added > 0:
			self.__write_inst(insts)
		return

	def rm_inst(self,pkgs):
		insts = self.get_insts()
		removed = 0
		if isinstance(pkgs,list):
			for p in pkgs:
				if p in insts:
					insts.remove(p)
					removed += 1
		else:
			if pkgs in insts:
				insts.remove(pkgs)
				removed += 1

		if removed > 0:
			self.__write_inst(insts)
		return


class TceList(TceListBase):
	def __init__(self,args):
		super(TceList,self).__init__(args)
		return

	def get_lists_command(self,pkgname):
		tries = 0
		cmd = '"%s" --timeout=%d -q -O - "%s/%s/%s/tcz/%s.tcz.list"'%(self.tce_wget,self.tce_timeout,self.tce_mirror,self.tce_tceversion,self.tce_platform,pkgname)
		logging.info('run (%s)'%(cmd))
		cont = True
		while cont:
			cont = False
			retval = cmdpack.run_command_callback(cmd,filter_context,self)
			if retval != 0 :
				if retval != 8 and tries > 5:
					raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
				elif retval != 8:
					tries += 1
					cont = True
		return self.get_lists()


class TceListFile(TceListFileBase):
	def __init__(self,args):
		super(TceListFile,self).__init__(args)
		return

	def get_lists_file(self,pkgname,listfile):
		with open(listfile,'r+') as f:
			for l in f:
				self.get_input(l)
		return self.get_list_files(pkgname)

	def get_lists_map(self,listfile):
		with open(listfile,'r+') as f:
			for l in f:
				self.get_input(l)
		return self.get_list_map()



def get_available(args):
	tceavail = TceAvail(args)
	return tceavail.get_avails()

def get_all_wget_deps(args,maps):
	avails = get_available(args)
	for p in avails:
		if p not in maps.keys():
			tcedep = TceWgetDep(args)
			maps[p] = tcedep.get_deps(p)
	return maps

def get_dep(args,pkgs,depmap):
	scaned = 0
	alldeps = []
	for p in pkgs:
		if p in depmap.keys():
			continue
		tcedep = TceWgetDep(args)
		depmap[p] = tcedep.get_deps(p)

	for p in pkgs:
		retlists = maphandle.form_map_list(depmap,p)
		for cp in retlists:
			if cp not in alldeps:
				alldeps.append(cp)
	slen = len(alldeps)
	while True:
		for p in alldeps:
			if p not in depmap.keys():
				tcedep = TceWgetDep(args)
				depmap[p] = tcedep.get_deps(p)
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

def get_wget_rdep(args,pkgs,depmaps,rdepmaps):
	scaned = 0
	for p in pkgs:
		if p not in rdepmaps.keys() and scaned == 0:
			depmaps = get_all_wget_deps(args,depmaps)
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
					depmaps = get_all_wget_deps(args,depmaps)
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
	return


def get_alldep_from_file(args):
	maps = dict()
	if args.tce_depmapfile is not None:
		logging.info('loading from %s'%(args.tce_depmapfile))
		tcetree = TceTree(args)
		maps = tcetree.get_dep_tree(args.tce_depmapfile,maps)
	return maps

def out_pkgs(args,pkgs):
	maphandle.format_output(args.subnargs,pkgs,'::%s::'%(args.subcommand))
	return

def out_map(args,maps):
	maphandle.output_map(args.subnargs,maps,'::%s::'%(args.subcommand))
	return

def combine_map(mainmaps,partmaps):
	for k in partmaps.keys():
		if k not in mainmaps.keys():
			mainmaps[k] = []
		for cp in partmaps[k]:
			if cp not in mainmaps[k]:
				mainmaps[k].append(cp)
	return mainmaps

def dep_tce(args,context):
	tcebase.set_log_level(args)
	maps = get_alldep_from_file(args)
	getpkgs,maps = get_dep(args,args.subnargs,maps)
	out_pkgs(args,getpkgs)
	out_map(args,maps)
	sys.exit(0)
	return

def tree_tce(args,context):
	tcebase.set_log_level(args)
	maps = get_dep_tree(args,args.subnargs)
	format_tree(args,maps,args.tree_list)
	sys.exit(0)
	return

def wgetrdep_tce(args,context):
	tcebase.set_log_level(args)
	maps = dict()
	maps2 = get_alldep_from_file(args)
	getpkgs,maps2,maps=get_wget_rdep(args,args.subnargs,maps2,maps)
	out_pkgs(args,getpkgs)
	out_map(args,maps)
	sys.exit(0)
	return


def inst_tce(args,context):
	tceinst = TceInst(args)
	return tceinst.get_insts()

def inst_handler(args,context):
	tcebase.set_log_level(args)
	insts = inst_tce(args,context)
	args.subnargs = []
	out_pkgs(args,insts)
	sys.exit(0)
	return



def all_tce(args,context):
	tcebase.set_log_level(args)
	getpkgs = get_available(args)
	args.subnargs = []
	out_pkgs(args,getpkgs)
	sys.exit(0)
	return

def alldep_tce(args,context):
	tcebase.set_log_level(args)
	getpkgs = get_available(args)
	depmaps = get_alldep_from_file(args)
	getpkgs,depmaps = get_dep(args,getpkgs,depmaps)	
	format_tree(args,depmaps,None,args.output)
	sys.exit(0)
	return

def wgettree_tce(args,context):
	tcebase.set_log_level(args)
	depmaps = dict()
	for p in args.subnargs:
		wtree= TceWgetTree(args)
		depmaps = wtree.get_dep_tree(p,depmaps)
	for p in args.subnargs:
		format_tree(args,depmaps,p)
	sys.exit(0)
	return


def loaddep_tce(args,context):
	if len(args.subnargs) < 1:
		Usage(3,'pkgs...',context)
	pkgs = args.subnargs
	tcebase.set_log_level(args)
	depmaps = get_alldep_from_file(args)
	if len(depmaps.keys()) == 0:
		if len(args.subnargs) < 2:
			Usage(3,'<depfile> pkgs...',context)
		depfile = pkgs.shift()
		depmaps = get_dep_tree(args,[depfile])
	for p in pkgs:
		format_tree(args,depmaps,p)
	sys.exit(0)
	return


def formatlist_handler(args,context):
	tcebase.set_log_level(args)
	listmap = dict()
	logging.info('formatlist')
	if args.subnargs is None or len(args.subnargs) == 0:
		getpkgs = get_available(args)
		logging.info('getpkgs %s'%(getpkgs))
		for p in getpkgs:
			tcelists = TceList(args)
			listmap[p] = tcelists.get_lists_command(p)
	else:
		logging.info('subnargs %s'%(args.subnargs))
		for p in args.subnargs:
			tcelists = TceList(args)
			listmap[p] = tcelists.get_lists_command(p)
	tcelistfile = TceListFileBase(args)
	s = tcelistfile.format_list_map(listmap)
	if args.output is None:
		sys.stdout.write(s)
	else:
		with open(args.output,'w+') as f:
			f.write(s)
	sys.exit(0)
	return

global_listmaps = dict()

def getlist_tce(args):
	global global_listmaps
	if len(global_listmaps.keys()) > 0:
		return global_listmaps
	tcelistsfile = TceListFile(args)
	global_listmaps = tcelistsfile.get_lists_map(args.tce_listsfile)
	return global_listmaps


def getlist_handler(args,context):
	tcebase.set_log_level(args)
	if args.tce_listsfile is None:
		Usage(3,'please specified TCE_LISTSFILE',context)
	totallistmaps = getlist_tce(args)
	listmaps = dict()
	if args.subnargs is not None and len(args.subnargs) > 0 :
		for p in args.subnargs:
			listmaps[p] = []
			if p in totallistmaps.keys():
				listmaps[p] = totallistmaps[p]
	else:
		listmaps = totallistmaps
	tcelistfile = TceListFileBase(args)
	s = tcelistfile.format_list_map(listmaps)
	sys.stdout.write(s)
	sys.exit(0)
	return




tce_dep_command_line = {
	'output|O' : None,
	'dep<dep_tce>## tce dep list ##' : {
		'$' : '+'
	},
	'wgetrdep<wgetrdep_tce>## tce rdep list##' : {
		'$' : '+'
	},
	'tree<tree_tce>## tce tree list##' : {
		'list|l' : [],
		'$' : '+'
	},
	'inst<inst_handler>## tce installed list##' : {
		'$' : 0
	},
	'all<all_tce>## all tce available ##' : {
		'$' : 0
	},
	'wgettree<wgettree_tce>## wget tree value ##' : {
		'$' : '+'
	},
	'alldep<alldep_tce>## to make all dep into a file default out stdout ##' :{
		'$' : 0
	},
	'loaddep<loaddep_tce>## load dep file from the file and set depend for one : depfile ,deppkg ...##' :{
		'$' : '+'
	},
	'formatlist<formatlist_handler>## format file list in tce ##' : {
		'$' : '*'
	},
	'getlist<getlist_handler>## get list file for pkg... ##' : {
		'$' : '*'
	}
}


def main():
	usage_str='%s [options] {commands} pkgs...'%(sys.argv[0])
	parser = extargsparse.ExtArgsParse(description='dpkg encapsulation',usage=usage_str)
	parser = tcebase.add_tce_args(parser)
	parser.load_command_line(tce_dep_command_line)
	args = parser.parse_command_line(None,parser)
	Usage(3,'please specified a command',parser)
	return

if __name__ =='__main__':
	main()
