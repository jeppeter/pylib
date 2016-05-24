#!/usr/bin/python
import re
import os
import sys
import argparse
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import dbgexp
import cmdpack

class DpkgBase(object):
	def __init__(self):
		self.cmdline = ''
		return
	def resub(self,l):
		newl = re.sub('\([^\(\)]*\)','',l)
		newl = re.sub('[\s]+','',newl)
		newl = re.sub(':([^\s:,]+)','',newl)
		return newl

	def get_attr_self(self,args,name):
		dpname = 'dpkg_%s'%(name)
		sname = 'dpkg_%s'%(name)
		if getattr(args,dpname) is not None:
			setattr(self,sname,getattr(args,dpname))
		return

	def get_all_attr_self(self,args):
		for p in dir(args):
			if p.startswith('dpkg_'):
				name = p.replace('dpkg_','')
				self.get_attr_self(args,name)
		return


class DpkgDependBase(DpkgBase):
	def __init__(self):
		self.__depmap = dict()
		self.__pkg = ''
		self.__pkgexpr = re.compile('^Package:\s+([^\s]+)',re.I)
		self.__depexpr = re.compile('^Depends:\s+(.*)',re.I)
		self.__predepexpr = re.compile('^Pre-Depends:\s+(.*)',re.I)
		self.__emptylineexpr = re.compile('^$')
		self.__splitexpr = re.compile('\|',re.I)
		return


	def __add_inner(self,pkg,deppkg):
		if self.__pkg == '' or deppkg is None:
			return
		m = self.__splitexpr.findall(deppkg)
		if m and len(m) > 0:
			deppkgs = re.split('\|',deppkg)
			if pkg not in self.__depmap.keys():
				self.__depmap[pkg] = []
			for p in deppkgs:
				if p not in self.__depmap[pkg]:
					self.__depmap[pkg].append(p)
		else:
			if pkg not in self.__depmap.keys():
				self.__depmap[pkg] = []
			if deppkg not in self.__depmap[pkg]:
				self.__depmap[pkg].append(deppkg)
		return

	def add_depend(self,l):
		l = l.rstrip('\r\n')
		l = l.strip(' \t')
		l = l.rstrip(' \t')
		m = self.__pkgexpr.findall(l)
		if m and len(m) > 0:
			self.__pkg = self.resub(m[0])
			if self.__pkg not in self.__depmap.keys():
				self.__depmap[self.__pkg] = []
			return
		m = self.__depexpr.findall(l)
		if m and len(m) > 0:
			if self.__pkg == '':
				logging.error('(%s) before pkg set'%(l))
				return
			newl = self.resub(m[0])
			sarr = re.split(',',newl)
			for p in sarr:
				self.__add_inner(self.__pkg,p)
			return
		m = self.__predepexpr.findall(l)
		if m and len(m) > 0:
			if self.__pkg == '':
				logging.error('(%s) before pkg set'%(l))
				return
			newl = self.resub(m[0])
			sarr = re.split(',',newl)
			for p in sarr:
				self.__add_inner(self.__pkg,p)
			return
		if self.__emptylineexpr.match(l):
			self.__pkg = ''
			return
		return


	def get_depend(self):
		return self.__depmap




class DpkgInstBase(DpkgBase):
	def __init__(self):
		self.__insts = []
		self.__started = False
		self.__startexpr = re.compile('[\+]+\-[\=]+',re.I)
		# we get installed package
		self.__instexpr = re.compile('^[a-zA-Z]i\s+([^\s]+)\s+',re.I)
		return
	def __add_inner(self,pkg):
		if pkg is None:
			return
		sarr = re.split(':',pkg)
		if len(sarr) > 1 :
			pkg = sarr[0]
		if pkg not in self.__insts:
			self.__insts.append(pkg)
		return

	def get_installed(self):
		return self.__insts

	def add_depend(self,l):
		l = l.rstrip('\r\n')
		l = l.strip(' \t')
		l = l.rstrip(' \t')
		if not self.__started:
			if self.__startexpr.match(l):
				self.__started = True
			return
		pkg = None
		m = self.__instexpr.findall(l)
		if m :
			pkg = m[0]
		self.__add_inner(pkg)
		return
	def reset_start(self):
		self.__started = False


class DpkgRcBase(DpkgBase):
	def __init__(self):
		self.__rcs = []
		self.__started = False
		self.__startexpr = re.compile('[\+]+\-[\=]+',re.I)
		self.__instexpr = re.compile('^rc\s+([^\s]+)\s+',re.I)
		return
	def __add_inner(self,pkg):
		if pkg is None:
			return
		sarr = re.split(':',pkg)
		if len(sarr) > 1 :
			pkg = sarr[0]
		if pkg not in self.__rcs:
			self.__rcs.append(pkg)
		return

	def get_rc(self):
		return self.__rcs

	def add_depend(self,l):
		l = l.rstrip('\r\n')
		l = l.strip(' \t')
		l = l.rstrip(' \t')
		if not self.__started:
			if self.__startexpr.match(l):
				self.__started = True
			return
		pkg = None
		m = self.__instexpr.findall(l)
		if m :
			pkg = m[0]
		self.__add_inner(pkg)
		return
	def reset_start(self):
		self.__started = False

class DpkgRDependBase(DpkgBase):
	def __init__(self):
		self.__rdepmap = dict()
		self.__pkg = ''
		self.__insts = []
		self.__pkgexpr = re.compile('^Package:\s+([^\s]+)',re.I)
		self.__depexpr = re.compile('^Depends:\s+(.*)',re.I)
		self.__predepexpr = re.compile('^Pre-Depends:\s+(.*)',re.I)
		self.__emptylineexpr = re.compile('^$')
		self.__splitexpr = re.compile('\|',re.I)
		return


	def __add_inner(self,pkg,deppkg):
		if pkg is None:
			return
		sarr = re.split(':',pkg)
		if len(sarr)> 1:
			# we should not get the name of pkg:i386 or pkg:amd64
			return
		m = self.__splitexpr.findall(deppkg)
		if m and len(m) > 0:
			deppkgs = re.split('\|',deppkg)
			for p in deppkgs:
				if p not in self.__rdepmap.keys():
					self.__rdepmap[p] = []
				if pkg not in self.__rdepmap[p]:
					self.__rdepmap[p].append(pkg)
		else:
			if deppkg not in self.__rdepmap.keys():
				self.__rdepmap[deppkg] = []
			if pkg not in self.__rdepmap[deppkg]:
				#logging.info('add %s'%(pkg))
				self.__rdepmap[deppkg].append(pkg)
		return


	def get_rdepends(self):
		return self.__rdepmap

	def add_depend(self,l):
		l = l.rstrip('\r\n')
		l = l.strip(' \t')
		l = l.rstrip(' \t')
		m = self.__pkgexpr.findall(l)
		if m and len(m) > 0:
			self.__pkg = self.resub(m[0])
			return
		m = self.__depexpr.findall(l)
		if m and len(m) > 0:
			if self.__pkg == '':
				logging.error('(%s) not before set Package'%(l))
				return
			newl = self.resub(m[0])
			sarr = re.split(',',newl)
			for p in sarr:
				self.__add_inner(self.__pkg,p)
			return
		m = self.__predepexpr.findall(l)
		if m and len(m) > 0:
			if self.__pkg == '':
				logging.error('(%s) not before set Package'%(l))
				return
			newl = self.resub(m[0])
			sarr = re.split(',',newl)
			for p in sarr:
				self.__add_inner(self.__pkg,p)
			return			
		if self.__emptylineexpr.match(l):
			self.__pkg = '';
			return
		return


class DpkgEssentailBase(DpkgBase):
	def __init__(self):
		self.__essentials = []
		self.__pkgexpr = re.compile('^Package:\s+([^\s]+)',re.I)
		self.__essentialexpr = re.compile('^Essential:\s+yes$',re.I)
		self.__emptylineexpr = re.compile('^$',re.I)
		self.__pkg = ''
		return

	def __add_inner(self,pkg):
		if self.__pkg == '':
			logging.error('not sepecified pkg')
			return
		if pkg not in self.__essentials:
			self.__essentials.append(pkg)
		return

	def add_depend(self,l):
		l = l.strip(' \t')
		l = l.rstrip('\r\n')
		l = l.strip(' \t')
		m = self.__pkgexpr.findall(l)
		if m and len(m) > 0:
			self.__pkg = self.resub(m[0])
			return

		if self.__essentialexpr.match(l):			
			self.__add_inner(self.__pkg)
			return
		if self.__emptylineexpr.match(l):
			self.__pkg = ''
			return
		return

	def get_essential(self):
		return self.__essentials


class DpkgDebInfoBase(DpkgBase):
	def __init__(self):
		self.__name = ''
		self.__version = ''
		self.__deps = []
		self.__pkgexpr = re.compile('^Package:\s+(.+)$',re.I)
		self.__versionexpr = re.compile('^Version:\s+(.+)$',re.I)
		self.__depexpr = re.compile('^Depends:\s+(.+)$',re.I)
		self.__predepexpr = re.compile('^Pre-Depends:\s+(.+)$',re.I)
		return

	def __add_inner(self,pkgs):
		if pkgs is None:
			return

		for p in pkgs:
			sarr = re.split('\|',p)
			for cp in sarr:
				if cp not in self.__deps:
					self.__deps.append(cp)
		return

	def add_depend(self,l):
		l = l.rstrip('\r\n')
		l = l.strip(' \t')
		l = l.rstrip(' \t')
		m = self.__depexpr.findall(l)
		if m and len(m) > 0:
			deps = self.resub(m[0])
			sarr = re.split(',',deps)
			self.__add_inner(sarr)
			return

		m = self.__predepexpr.findall(l)
		if m and len(m) > 0:
			deps = self.resub(m[0])
			sarr = re.split(',',deps)
			self.__add_inner(sarr)
			return
		m = self.__pkgexpr.findall(l)
		if m and len(m) > 0:
			name = self.resub(m[0])
			self.__name = name
			return
		m = self.__versionexpr.findall(l)
		if m and len(m) > 0:
			self.__version = self.resub(m[0])
			return
		return

	def get_depend(self):
		return self.__deps

	def get_version(self):
		return self.__version

	def get_name(self):
		return self.__name


def filter_depends(instr,context):
	context.add_depend(instr)
	return


class DpkgDepends(DpkgDependBase):
	def __init__(self,args):
		super(DpkgDepends, self).__init__()
		self.dpkg_sudoprefix = 'sudo'
		self.dpkg_root = '/'
		self.dpkg_cat = 'cat'
		self.dpkg_chroot = 'chroot'
		self.get_all_attr_self(args)
		return

	def get_depend_command(self,pkgname):
		cmds = '"%s" "%s" "%s" "%s" "/var/lib/dpkg/available"'%(self.dpkg_sudoprefix,self.dpkg_chroot,self.dpkg_root,self.dpkg_cat)
		self.cmdline = cmds
		retval = cmdpack.run_command_callback(cmds,filter_depends,self)
		if retval != 0 :
			raise Exception('run (%s) error'%(cmds))
		return self.get_depend()

class DpkgRDepends(DpkgRDependBase):
	def __init__(self,args):
		super(DpkgRDepends, self).__init__()
		self.dpkg_sudoprefix = 'sudo'
		self.dpkg_root = '/'
		self.dpkg_cat = 'cat'
		self.dpkg_chroot = 'chroot'
		self.get_all_attr_self(args)
		return

	def get_depend_command(self,pkgname):
		cmds = '"%s" "%s" "%s" "%s" "/var/lib/dpkg/available"'%(self.dpkg_sudoprefix,self.dpkg_chroot,self.dpkg_root,self.dpkg_cat)
		self.cmdline = cmds
		retval = cmdpack.run_command_callback(cmds,filter_depends,self)
		if retval != 0 :
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run (%s) error'%(cmds))
		return self.get_rdepends()

class DpkgInst(DpkgInstBase):
	def __init__(self,args):
		super(DpkgInst, self).__init__()
		self.dpkg_dpkg = 'dpkg'
		self.dpkg_sudoprefix = 'sudo'
		self.dpkg_root = '/'
		self.dpkg_chroot = 'chroot'
		self.get_all_attr_self(args)
		logging.info('root %s'%(self.dpkg_root))
		return

	def get_install_command(self):
		cmds = '"%s" "%s" "%s" "%s" -l'%(self.dpkg_sudoprefix,self.dpkg_chroot,self.dpkg_root,self.dpkg_dpkg)
		self.cmdline = cmds
		self.reset_start()
		logging.info('run (%s)'%(cmds))
		retval = cmdpack.run_command_callback(cmds,filter_depends,self)
		if retval != 0 :
			raise Exception('run (%s) error'%(cmds))
		return self.get_installed()


class DpkgRc(DpkgRcBase):
	def __init__(self,args):
		super(DpkgRc, self).__init__()
		self.dpkg_dpkg = 'dpkg'
		self.dpkg_sudoprefix = 'sudo'
		self.dpkg_root = '/'
		self.dpkg_chroot = 'chroot'
		self.get_all_attr_self(args)
		logging.info('root %s'%(self.dpkg_root))
		return

	def get_rc_command(self):
		cmds = '"%s" "%s" "%s" "%s" -l'%(self.dpkg_sudoprefix,self.dpkg_chroot,self.dpkg_root,self.dpkg_dpkg)
		self.cmdline = cmds
		self.reset_start()
		logging.info('run (%s)'%(cmds))
		retval = cmdpack.run_command_callback(cmds,filter_depends,self)
		if retval != 0 :
			raise Exception('run (%s) error'%(cmds))
		return self.get_rc()


class DpkgEssential(DpkgEssentailBase):
	def __init__(self,args):
		super(DpkgEssential, self).__init__()
		self.dpkg_dpkg = 'dpkg'
		self.dpkg_sudoprefix = 'sudo'
		self.dpkg_root = '/'
		self.dpkg_chroot = 'chroot'
		self.dpkg_cat = 'cat'
		self.get_all_attr_self(args)
		return

	def get_essential_command(self):
		cmds = '"%s" "%s" "%s" "%s"  "/var/lib/dpkg/available"'%(self.dpkg_sudoprefix,self.dpkg_chroot,self.dpkg_root,self.dpkg_cat)
		self.cmdline = cmds
		logging.info('run (%s)'%(cmds))
		retval = cmdpack.run_command_callback(cmds,filter_depends,self)
		if retval != 0 :
			raise Exception('run (%s) error'%(cmds))
		return self.get_essential()

class DpkgDebDep(DpkgDebInfoBase):
	def __init__(self,args):
		super(DpkgDebDep, self).__init__()
		self.dpkg_dpkg = 'dpkg'
		self.dpkg_sudoprefix = 'sudo'
		self.dpkg_root = '/'
		self.dpkg_chroot = 'chroot'
		self.dpkg_cat = 'cat'
		self.get_all_attr_self(args)
		return

	def get_deb_dep(self,p):
		cmds = '"%s" "%s" --info "%s"'%(self.dpkg_sudoprefix,self.dpkg_dpkg,p)
		self.cmdline = cmds
		retval = cmdpack.run_command_callback(cmds,filter_depends,self)
		if retval != 0 :
			raise Exception('run (%s) error'%(cmds))
		return self.get_depend()

class DpkgDebName(DpkgDebInfoBase):
	def __init__(self,args):
		super(DpkgDebName, self).__init__()
		self.dpkg_dpkg = 'dpkg'
		self.dpkg_sudoprefix = 'sudo'
		self.dpkg_root = '/'
		self.dpkg_chroot = 'chroot'
		self.dpkg_cat = 'cat'
		self.get_all_attr_self(args)
		return

	def get_deb_name(self,p):
		cmds = '"%s" "%s" --info "%s"'%(self.dpkg_sudoprefix,self.dpkg_dpkg,p)
		self.cmdline = cmds
		retval = cmdpack.run_command_callback(cmds,filter_depends,self)
		if retval != 0 :
			raise Exception('run (%s) error'%(cmds))
		return self.get_name()

class DpkgUtils(DpkgBase):
	def __init__(self,args):
		self.dpkg_mount = 'mount'
		self.dpkg_umount = 'umount'
		self.dpkg_sudoprefix = 'sudo'
		self.dpkg_root = '/'
		self.dpkg_chown = 'chown'
		self.dpkg_chmod = 'chmod'
		self.get_all_attr_self(args)
		return

	def mount_dir(self,directory):
		if self.dpkg_root == '/':
			return
		mdir = '%s%s%s'%(self.dpkg_root,os.sep,directory)
		if os.path.ismount(mdir):
			logging.warn('%s mount already'%(mdir))
			return
		cmds = '"%s" "%s" --bind "%s" "%s"'%(self.dpkg_sudoprefix,self.dpkg_mount,directory,mdir)
		retval = cmdpack.run_command_callback(cmds,None,None)
		if retval != 0 :
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'can not run (%s)'%(cmds))
		return

	def umount_dir(self,directory):
		if self.dpkg_root == '/':
			return
		dmount = '%s%s%s'%(self.dpkg_root,os.sep,directory)
		if not os.path.ismount(dmount):
			logging.warn('(%s) not mount'%(dmount))
			return
		cmds = '"%s" "%s" "%s"'%(self.dpkg_sudoprefix,self.dpkg_umount,dmount)
		retval = cmdpack.run_command_callback(cmds,None,None)
		if retval != 0:
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'can not run (%s)'%(cmds))
		return

	def mkdir(self,directory):
		if self.dpkg_root == '/':
			return
		mdir = '%s%s%s'%(self.dpkg_root,os.sep,directory)
		if os.path.isdir(mdir):
			return
		os.makedirs(mdir)
		return

	def rmdir(self,directory):
		if self.dpkg_root == '/':
			return
		mdir = '%s%s%s'%(self.dpkg_root,os.sep,directory)
		if not os.path.isdir(mdir):
			return
		try:
			os.rmdir(mdir)
		except os.OSErr as e:
			logging.warn('can not remove (%s) error(%s)'%(mdir,e))
		return

	def chown(self,fileordir,ownid,grpid=-1):
		if self.dpkg_root == '/':
			return
		if grpid < 0:
			grpid = ownid
		fdir = '%s%s%s'%(self.dpkg_root,os.sep,fileordir)
		cmd = ''
		if os.path.isdir(fdir):
			cmd += '"%s" "%s" "%d:%d" -R "%s"'%(self.dpkg_sudoprefix,self.dpkg_chown,ownid,grpid,fdir)
		elif os.path.isfile(fdir):
			cmd += '"%s" "%s" "%d:%d" "%s"'%(self.dpkg_sudoprefix,self.dpkg_chown,ownid,grpid,fdir)
		else:
			logging.info('%s not valid'%(fdir))
			return
		retval = cmdpack.run_command_callback(cmd,None,None)
		if retval !=0 :
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'can not run (%s)'%(cmd))
		return

	def setuid(self,fileordir):
		if self.dpkg_root == '/':
			return
		fdir = '%s%s%s'%(self.dpkg_root,os.sep,fileordir)
		cmd = ''
		if os.path.isfile(fdir):
			cmd += '"%s" "%s" u+s "%s"'%(self.dpkg_sudoprefix,self.dpkg_chmod,fdir)
		else:
			logging.info('%s not valid'%(fdir))
			return
		logging.info('run (%s)'%(cmd))
		retval = cmdpack.run_command_callback(cmd,None,None)
		if retval !=0 :
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'can not run (%s)'%(cmd))
		return





def Usage(ec,fmt,parser):
	fp = sys.stderr
	if ec == 0 :
		fp = sys.stdout

	if len(fmt) > 0:
		fp.write('%s\n'%(fmt))
	parser.print_help(fp)
	sys.exit(ec)



def check_dep_map_integrity(depmap):
	searchkeys = []
	misskeys = []
	for p in depmap.keys():
		deps = depmap[p]
		for cp in deps:
			if cp not in depmap.keys():
				#logging.info('(%s=>%s) (%s)'%(p,deps,cp))
				if cp not in misskeys:
					misskeys.append(cp)
	return misskeys

def make_normalize_dep(depmap,insts):
	allkeys = []
	for p in depmap.keys():
		allkeys.append(p)
	while len(allkeys) > 0:
		p = allkeys[0]
		allkeys.remove(p)
		if p not in insts:
			del depmap[p]
			logging.warn('delete (%s)'%(p))
			continue
		deps = depmap[p]
		for cp in deps:
			if cp not in insts:
				logging.warn('delete (%s)'%(cp))
				depmap[p].remove(cp)
	return depmap

def get_all_deps(pkgs,args,depmap):
	hasscaned = 0
	for p in pkgs:
		if p in depmap.keys() or hasscaned > 0:
			continue
		dpkgdeps = DpkgDepends(args)
		depmap = dpkgdeps.get_depend_command(p)
		hasscaned = 1
	alldeps = []
	for p in pkgs:
		if p not in depmap.keys():
			logging.error('(%s) not in depmap'%(p))
			continue
		ndep = form_map_list(depmap,p)
		for cp in ndep:
			if cp not in alldeps:
				alldeps.append(cp)
		if p not in alldeps:
			alldeps.append(p)
	slen = len(alldeps)
	mod = 0
	while True:
		for p in alldeps:
			ndep = form_map_list(depmap,p)
			for cp in ndep:
				if cp not in alldeps:
					alldeps.append(cp)
		clen = len(alldeps)
		if clen == slen:
			break
		slen = clen
	return alldeps,depmap

def get_dep_noself(pkgs,args,depmap):
	hasscaned = 0
	for p in pkgs:
		if p in depmap.keys() or hasscaned > 0:
			continue
		dpkgdeps = DpkgDepends(args)
		depmap = dpkgdeps.get_depend_command(p)
		hasscaned = 1
	alldeps = []
	for p in pkgs:
		if p not in depmap.keys():
			logging.error('(%s) not in depmap'%(p))
			continue
		ndep = form_map_list(depmap,p)
		for cp in ndep:
			if cp not in alldeps:
				alldeps.append(cp)
	slen = len(alldeps)
	mod = 0
	while True:
		for p in alldeps:
			ndep = form_map_list(depmap,p)
			for cp in ndep:
				if cp not in alldeps:
					alldeps.append(cp)
		clen = len(alldeps)
		if clen == slen:
			break
		slen = clen
	return alldeps,depmap

def get_all_inst(args):
	dpkgrdeps = DpkgInst(args)
	return dpkgrdeps.get_install_command()

def get_all_rc(args):
	dpkgrcs = DpkgRc(args)
	return dpkgrcs.get_rc_command()

def get_all_rdeps(pkgs,args,insts,rdepmaps):
	hasscaned = 0
	for p in pkgs:
		if p in rdepmaps.keys() or hasscaned > 0:
			continue
		dpkgrdeps = DpkgRDepends(args)
		rdepmaps = dpkgrdeps.get_depend_command(p)
		hasscaned = 1
	allrdeps = []
	for p in pkgs:
		if p not in rdepmaps.keys():
			# we have match before
			continue
		currdeps = rdepmaps[p]
		for cp in currdeps:
			if (cp not in allrdeps) and (cp in insts):
				allrdeps.append(cp)
	slen = len(allrdeps)
	while True:
		for p in allrdeps:
			if p not in rdepmaps.keys():
				continue
			currdeps = rdepmaps[p]
			for cp in currdeps:
				if (cp not in allrdeps) and (cp in insts):
					allrdeps.append(cp)
		clen = len(allrdeps)
		#logging.info('slen %d clen %d'%(slen,clen))
		if clen == slen:
			break
		slen = clen
	return allrdeps,rdepmaps


def get_essentials(args):
	dpkgessential = DpkgEssential(args)
	return dpkgessential.get_essential_command()

def get_debdep(args,debs,depmap):
	if type(debs) is list:
		for d in debs:
			dpkgname = DpkgDebName(args)
			name = dpkgname.get_deb_name(d)
			if name not in depmap.keys():
				dpkgdebdep = DpkgDebDep(args)
				debdeps = dpkgdebdep.get_deb_dep(d)
				depmap[name] = debdeps	
				logging.info('(%s): (%s)'%(name,debdeps))
	else:
		dpkgname = DpkgDebName(args)
		name = dpkgname.get_deb_name(debs)
		if name not in depmap.keys():
			dpkgdebdep = DpkgDebDep(args)
			debdeps = dpkgdebdep.get_deb_dep(debs)
			depmap[name] = debdeps
			logging.info('(%s): (%s)'%(name,debdeps))
	return depmap

def get_debname(args,pkgs,debmap):
	if type(pkgs) is list:
		for p in pkgs:
			dpkgname = DpkgDebName(args)
			name = dpkgname.get_deb_name(p)
			if len(name) > 0 :
				debmap[name]=os.path.abspath(p)
	else:
		dpkgname = DpkgDebName(args)
		name = dpkgname.get_deb_name(pkgs)
		if len(name) > 0:
			debmap[name]=os.path.abspath(pkgs)
	return debmap

mount_dirs=['/sys','/proc','/tmp']
make_dirs=['/var/tmp','/sys','/proc','/tmp']
sudo_root_files=['/usr/bin/sudo','/usr/lib/sudo/sudoers.so','/etc/sudoers','/etc/sudoers.d']
sudo_s_files=['/usr/bin/sudo']

def environment_before(args):
	global mount_dirs
	global make_dirs
	global sudo_root_files
	utils = DpkgUtils(args)
	for d in make_dirs:
		utils.mkdir(d)
	for d in mount_dirs:
		utils.mount_dir(d)
	for d in sudo_root_files:
		utils.chown(d,0,0)
	for d in sudo_s_files:
		utils.setuid(d)
	return

def environment_after(args):
	global mount_dirs
	utils = DpkgUtils(args)
	for d in mount_dirs:
		utils.umount_dir(d)
	return

def add_dpkg_args(parser):
	parser.add_argument('-v','--verbose',default=0,action='count')
	parser.add_argument('-r','--root',dest='dpkg_root',default='/',action='store',help='root of dpkg specified')
	parser.add_argument('-a','--aptcache',dest='dpkg_aptcache',default='apt-cache',action='store',help='apt-cache specified')
	parser.add_argument('-g','--aptget',dest='dpkg_aptget',default='apt-get',action='store',help='apt-get specified')
	parser.add_argument('-c','--cat',dest='dpkg_cat',default='cat',action='store',help='cat specified')
	parser.add_argument('-C','--chroot',dest='dpkg_chroot',default='chroot',action='store',help='chroot specified')
	parser.add_argument('-d','--dpkg',dest='dpkg_dpkg' ,default='dpkg',action='store',help='dpkg specified')
	parser.add_argument('-t','--try',dest='dpkg_trymode',default=False,action='store_true',help='try mode')
	parser.add_argument('-D','--directory',dest='directory',default=os.path.abspath('.'),action='store',help='directory for download')
	parser.add_argument('-R','--reserved',dest='dpkg_reserved',default=False,action='store_true',help='not delete files')
	parser.add_argument('--norollback',dest='dpkg_rollback',default=True,action='store_false',help='to rollback when failed')
	parser.add_argument('-m','--mount',dest='dpkg_mount',default='mount',action='store',help='mount specified')
	parser.add_argument('-u','--umount',dest='dpkg_umount',default='umount',action='store',help='umount specified')
	parser.add_argument('--chown',dest='dpkg_chown',default='chown',action='store',help='chown specified')
	parser.add_argument('--chmod',dest='dpkg_chmod',default='chmod',action='store',help='chmod specified')
	return parser


def main():
	parser = argparse.ArgumentParser(description='dpkg encapsulation',usage='%s [options] {commands} pkgs...'%(sys.argv[0]))	
	add_dpkg_args(parser)
	sub_parser = parser.add_subparsers(help='',dest='command')
	dep_parser = sub_parser.add_parser('dep',help='get depends')
	dep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get depend')
	rdep_parser = sub_parser.add_parser('rdep',help='get rdepends')
	rdep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get rdepend')
	inst_parser = sub_parser.add_parser('inst',help='get installed')
	rc_parser = sub_parser.add_parser('rc',help='get rcs')
	essential_parser =sub_parser.add_parser('essentials',help='get essential')
	debdep_parser = sub_parser.add_parser('debdep',help='get dep of deb')
	debdep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get depend')
	debname_parser = sub_parser.add_parser('debname',help='get dep of deb')
	debname_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get name')
	prepare_parser = sub_parser.add_parser('prepare',help='get prepare')	

	args = parser.parse_args()	

	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	maps = dict()
	if args.command == 'dep':
		if len(args.pkgs) < 1:
			Usage(3,'packages need',parser)
		getpkgs,maps = get_all_deps(args.pkgs,args,maps)
	elif args.command == 'inst':
		getpkgs = get_all_inst(args)
		args.pkgs = ''
	elif args.command == 'rdep':
		if len(args.pkgs) < 1:
			Usage(3,'packages need',parser)
		insts = get_all_inst(args)
		getpkgs,maps = get_all_rdeps(args.pkgs,args,insts,maps)
	elif args.command == 'rc':
		getpkgs = get_all_rc(args)
		args.pkgs = ''
	elif args.command == 'essentials':
		getpkgs = get_essentials(args)
		args.pkgs = ''
	elif args.command == 'debdep':
		if len(args.pkgs) < 1:
			Usage(3,'packages need',parser)		
		maps = get_debdep(args,args.pkgs,maps)
		args.pkgs = maps.keys()
	elif args.command == 'debname':
		if len(args.pkgs) < 1:
			Usage(3,'packages need',parser)
		maps = get_debname(args,args.pkgs,maps)
		for k in maps.keys():
			curpath = maps[k]
			maps[k] = [curpath]
		args.pkgs = maps.keys()
	elif args.command == 'prepare':
		try:
			environment_before(args)
		finally:
			environment_after(args)
	else:
		Usage(3,'can not get %s'%(args.command),parser)
	if args.command == 'dep' or args.command == 'rdep' or args.command == 'inst' or args.command == 'rc' \
	   or args.command == 'essentials':
		format_output(args.pkgs,getpkgs,'::%s::'%(args.command))
	if args.command == 'dep'  or args.command == 'rdep' or args.command == 'debdep' or args.command == 'debname':
		output_map(args.pkgs,maps,'::%s::'%(args.command))
	return

if __name__ == '__main__':
	main()

