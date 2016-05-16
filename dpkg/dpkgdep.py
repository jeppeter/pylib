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
		return

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
		self.__depends = []
		self.__needmore = False
		self.__moreexpr = re.compile('<([^>]+)>')
		self.__depexpr = re.compile('\s*[|]?depends:\s+([^\s]+)\s*',re.I)
		return

	def __add_inner(self,pkg):
		if pkg is None:
			return
		if pkg not in self.__depends:
			self.__depends.append(pkg)
		return

	def add_depend(self,l):
		dependpkg = None
		l = l.rstrip('\r\n')
		if self.__needmore :
			sarr = re.split(':',l)
			if len(sarr) < 2:
				dependpkg = l.strip(' \t')
				dependpkg = dependpkg.rstrip(' \t')
				self.__add_inner(dependpkg)
				return
		self.__needmore = False
		m = self.__depexpr.findall(l)
		if m :
			dependpkg = m[0]
			if self.__moreexpr.match(dependpkg):
				self.__needmore = True
				dependpkg = None
		self.__add_inner(dependpkg)
		return


	def add_depend_direct(self,pkg):
		self.__add_inner(pkg)
		return

	def get_depend(self):
		return self.__depends




class DpkgInstBase(DpkgBase):
	def __init__(self):
		self.__insts = []
		self.__started = False
		self.__startexpr = re.compile('[\+]+\-[\=]+',re.I)
		self.__instexpr = re.compile('ii\s+([^\s]+)\s+',re.I)
		return
	def __add_inner(self,pkg):
		if pkg is None:
			return
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


class DpkgRDependBase(DpkgBase):
	def __init__(self):
		self.__rdepends = []
		self.__insts = []
		self.__started = False
		self.__rdepexpr = re.compile('\s*reverse depends:\s*',re.I)
		return

	def __add_inner(self,pkg):
		if pkg is None:
			return
		if pkg not in self.__rdepends and pkg in self.__insts:
			#logging.info('add %s'%(pkg))
			self.__rdepends.append(pkg)
		return

	def set_insts(self,insts):
		self.__insts = insts
		return

	def get_rdepends(self):
		return self.__rdepends

	def add_depend(self,l):
		l = l.rstrip('\r\n')
		l = l.strip(' \t')
		l = l.rstrip(' \t')
		l = l.replace('|','')
		if not self.__started:
			if self.__rdepexpr.match(l):
				self.__started = True
			return
		self.__add_inner(l)
		return
	def reset_start(self):
		self.__started = False


def filter_depends(instr,context):
	context.add_depend(instr)
	return


class DpkgDepends(DpkgDependBase):
	def __init__(self,args):
		super(DpkgDepends, self).__init__()
		self.dpkg_aptcache = 'apt-cache'
		self.dpkg_sudoprefix = 'sudo'
		self.dpkg_root = '/'
		self.get_all_attr_self(args)
		return

	def get_depend_command(self,pkgname):
		cmds = '%s "%s" -o "dir::cache::archive=%s/var/lib/apt/" depends "%s"'%(self.dpkg_sudoprefix,self.dpkg_aptcache,self.dpkg_root,pkgname)
		retval = cmdpack.run_command_callback(cmds,filter_depends,self)
		if retval != 0 :
			raise Exception('run (%s) error'%(cmds))
		return self.get_depend()

class DpkgRDepends(DpkgRDependBase):
	def __init__(self,args):
		super(DpkgRDepends, self).__init__()
		self.dpkg_aptcache = 'apt-cache'
		self.dpkg_sudoprefix = 'sudo'
		self.dpkg_root = '/'
		self.get_all_attr_self(args)
		return

	def get_depend_command(self,pkgname):
		cmds = '%s "%s" -o "dir::cache::archive=%s/var/lib/apt/" rdepends "%s"'%(self.dpkg_sudoprefix,self.dpkg_aptcache,self.dpkg_root,pkgname)
		self.reset_start()
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
		self.get_all_attr_self(args)
		logging.info('root %s'%(self.dpkg_root))
		return

	def get_install_command(self):
		cmds = '%s "%s" --root "%s" -l'%(self.dpkg_sudoprefix,self.dpkg_dpkg,self.dpkg_root)
		self.reset_start()
		logging.info('run (%s)'%(cmds))
		retval = cmdpack.run_command_callback(cmds,filter_depends,self)
		if retval != 0 :
			raise Exception('run (%s) error'%(cmds))
		return self.get_installed()




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
		curdeps = maps[p]
		for cp in curdeps:
			if cp not in outdeps:
				outdeps.append(cp)

	for p in alldeps:
		if p in outdeps:
			continue
		if p not in maps.keys():
			continue
		__format_output_max([p],maps[p],'%s %s'%(p,outstr),pmax,gmax)
		curdeps = maps[p]
		for cp in curdeps:
			if cp not in outdeps:
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
	for p in pkgs:
		if p in depmap.keys():
			continue
		dpkgdeps = DpkgDepends(args)
		depmap[p] = dpkgdeps.get_depend_command(p)
	alldeps = []
	for p in pkgs:
		ndep = form_map_list(depmap,p)
		for cp in ndep:
			if cp not in alldeps:
				alldeps.append(cp)
		if p not in alldeps:
			alldeps.append(p)
	slen = len(alldeps)
	mod = 0
	while True:
		mod = 0
		for p in alldeps:
			if p in depmap.keys():
				continue
			mod = 1
			dpkgdeps = DpkgDepends(args)
			depmap[p] = dpkgdeps.get_depend_command(p)
		if mod == 0:
			break
		for p in alldeps:
			ndep = form_map_list(depmap,p)
			for cp in ndep:
				if cp not in alldeps:
					alldeps.append(cp)
	return alldeps,depmap

def get_all_inst(args):
	dpkgrdeps = DpkgInst(args)
	return dpkgrdeps.get_install_command()


def get_all_rdeps(pkgs,args,insts,rdepmaps):
	for p in pkgs:
		if p in rdepmaps.keys():
			continue
		dpkgrdeps = DpkgRDepends(args)
		dpkgrdeps.set_insts(insts)
		rdepmaps[p] = dpkgrdeps.get_depend_command(p)
	allrdeps = []
	for p in pkgs:
		if p not in rdepmaps.keys():
			dpkgrdeps = DpkgRDepends(args)
			dpkgrdeps.set_insts(insts)
			rdepmaps[p] = dpkgrdeps.get_depend_command(p)			
		currdeps = rdepmaps[p]
		for cp in currdeps:
			if (cp not in allrdeps) and (cp in insts):
				allrdeps.append(cp)
	slen = len(allrdeps)
	while True:
		for p in allrdeps:
			if p not in rdepmaps.keys():
				dpkgrdeps = DpkgRDepends(args)
				dpkgrdeps.set_insts(insts)
				rdepmaps[p] = dpkgrdeps.get_depend_command(p)
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



def main():
	parser = argparse.ArgumentParser(description='dpkg encapsulation',usage='%s [options] {commands} pkgs...'%(sys.argv[0]))	
	parser.add_argument('-v','--verbose',default=0,action='count')
	parser.add_argument('-r','--root',dest='dpkg_root',default='/',action='store',help='root of dpkg specified')
	parser.add_argument('-a','--aptcache',dest='dpkg_aptcache',default='apt-cache',action='store',help='apt-cache specified')
	parser.add_argument('-d','--dpkg',dest='dpkg_dpkg' ,default='dpkg',action='store',help='dpkg specified')
	sub_parser = parser.add_subparsers(help='',dest='command')
	dep_parser = sub_parser.add_parser('dep',help='get depends')
	dep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get depend')
	rdep_parser = sub_parser.add_parser('rdep',help='get rdepends')
	rdep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get rdepend')
	inst_parser = sub_parser.add_parser('inst',help='get installed')

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
	else:
		Usage(3,'can not get %s'%(args.command),parser)
	if args.command == 'dep' or args.command == 'rdep' or args.command == 'inst':
		format_output(args.pkgs,getpkgs,'::%s::'%(args.command))
	if args.command == 'dep'  or args.command == 'rdep' :
		output_map(args.pkgs,maps,'::%s::'%(args.command))
	return

if __name__ == '__main__':
	main()

