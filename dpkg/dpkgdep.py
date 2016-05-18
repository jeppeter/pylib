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

def Usage(ec,fmt,parser):
	fp = sys.stderr
	if ec == 0 :
		fp = sys.stdout

	if len(fmt) > 0:
		fp.write('%s\n'%(fmt))
	parser.print_help(fp)
	sys.exit(ec)

def __format_output_max(pkgs,getpkgs,outstr,pmax,gmax):
	s = ''
	i = 0
	j = 0
	for p in pkgs:
		if (i % 5)==0:			
			if i != 0:
				j += 1
			i = 0
			s += '\n'
		if i != 0 :
			s += ','
		s += '%-*s'%(pmax,p)
		i += 1
	s += '\n'
	i = 0
	j = 0
	s += '%s (%d)'%(outstr,len(getpkgs))
	for p in getpkgs:
		if (i % 5)==0:			
			if i != 0:
				j += 1
			i = 0
			s += '\n'
		if i != 0 :
			s += ','
		s += '%-*s'%(gmax,p)
		i += 1
	s += '\n'
	sys.stdout.write(s)

def format_output(pkgs,getpkgs,outstr):
	s = ''
	i = 0
	j = 0
	pmax = 0
	gmax = 0
	for p in pkgs:
		if len(p) > pmax:
			pmax = len(p)

	for p in getpkgs:
		if len(p) > gmax:
			gmax = len(p)
	__format_output_max(pkgs,getpkgs,outstr,pmax,gmax)
	return


def output_map(pkgs,maps,outstr):
	s = ''
	i = 0
	j = 0
	pmax = 0
	gmax = 0
	alldeps = []
	outputdeps = []
	curdeps = []
	for p in pkgs:
		if len(p) > pmax:
			pmax = len(p)
		curdeps = form_map_list(maps,p)
		for cp in curdeps:
			if cp not in alldeps:
				if len(cp) > gmax:
					gmax = len(cp)
				alldeps.append(cp)
	slen = len(alldeps)
	while True:
		for p in alldeps:
			curdeps = form_map_list(maps,p)
			for cp in curdeps:
				if cp not in alldeps:
					if len(cp) > gmax:
						gmax = len(cp)
					alldeps.append(cp)
		clen = len(alldeps)
		if clen == slen:
			break
	outdeps = []
	for p in pkgs:
		if p not in maps.keys():
			continue
		__format_output_max([p],maps[p],'%s %s'%(p,outstr),pmax,gmax)
		if p not in outdeps:
			logging.info('outdeps (%s)'%(cp))
			outdeps.append(cp)

	for p in alldeps:
		if p in outdeps:
			continue
		if p not in maps.keys():
			continue
		__format_output_max([p],maps[p],'%s %s'%(p,outstr),pmax,gmax)
		if p not in outdeps:
			outdeps.append(cp)
	return

def form_map_list(depmap,pkg):
	retlist = []
	curpkg = pkg
	if curpkg in depmap.keys():
		retlist.extend(depmap[pkg])
	slen = len(retlist)
	while True:
		for p in retlist:
			if p in depmap.keys():
				for cp in depmap[p]:
					if cp not in retlist:
						retlist.append(cp)
		clen = len(retlist)
		if clen == slen:
			break
		slen = clen
	return retlist

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

def main():
	parser = argparse.ArgumentParser(description='dpkg encapsulation',usage='%s [options] {commands} pkgs...'%(sys.argv[0]))	
	parser.add_argument('-v','--verbose',default=0,action='count')
	parser.add_argument('-r','--root',dest='dpkg_root',default='/',action='store',help='root of dpkg specified')
	parser.add_argument('-d','--dpkg',dest='dpkg_dpkg' ,default='dpkg',action='store',help='dpkg specified')
	parser.add_argument('-c','--cat',dest='dpkg_cat',default='cat',action='store',help='cat specified')
	parser.add_argument('-C','--chroot',dest='dpkg_chroot',default='chroot',action='store',help='chroot specified')
	sub_parser = parser.add_subparsers(help='',dest='command')
	dep_parser = sub_parser.add_parser('dep',help='get depends')
	dep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get depend')
	rdep_parser = sub_parser.add_parser('rdep',help='get rdepends')
	rdep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get rdepend')
	inst_parser = sub_parser.add_parser('inst',help='get installed')
	rc_parser = sub_parser.add_parser('rc',help='get rcs')
	essential_parser =sub_parser.add_parser('essentials',help='get essential')

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
	else:
		Usage(3,'can not get %s'%(args.command),parser)
	if args.command == 'dep' or args.command == 'rdep' or args.command == 'inst' or args.command == 'rc' or args.command == 'essentials':
		format_output(args.pkgs,getpkgs,'::%s::'%(args.command))
	if args.command == 'dep'  or args.command == 'rdep' :
		output_map(args.pkgs,maps,'::%s::'%(args.command))
	return

if __name__ == '__main__':
	main()

