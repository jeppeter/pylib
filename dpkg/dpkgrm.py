#!/usr/bin/python
import os
import sys
import argparse
import logging
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import dpkgdep
import cmdpack
import dbgexp


class DpkgRmBase(dpkgdep.DpkgBase):
	def __init__(self,args):
		self.dpkg_dpkg = 'dpkg'
		self.dpkg_aptget= 'apt-get'
		self.dpkg_aptcache = 'apt-cache'
		self.dpkg_sudoprefix = 'sudo'
		self.dpkg_root = '/'
		self.dpkg_trymode = False
		self.dpkg_chroot = 'chroot'
		self.get_all_attr_self(args)
		self.__callidx = 0
		return

	def __inner_remove(self,pkg):
		if self.dpkg_trymode :
			# we do not do this
			return
		if type(pkg) is list:
			cmds = '"%s" "%s" "%s" "%s" --remove --force-depends '%(self.dpkg_sudoprefix,self.dpkg_chroot,self.dpkg_root,self.dpkg_dpkg)
			for p in pkg:
				cmds += ' "%s"'%(p)
		else:
			#cmds = '"%s" "%s" "%s" "%s" remove --yes "%s" '%(self.dpkg_sudoprefix,self.dpkg_chroot,self.dpkg_root,self.dpkg_aptget,pkg)
			cmds = '"%s" "%s" "%s" "%s"  --remove --force-depends "%s"'%(self.dpkg_sudoprefix,self.dpkg_chroot,self.dpkg_root,self.dpkg_dpkg,pkg)
		retval = cmdpack.run_command_callback(cmds,None,None)
		if retval != 0 :
			if retval != 100:
				raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'can not remove (%s)'%(pkg))
			else:
				logging.warn('no pkg (%s)removed'%(pkg))
		return

	def __remove_recursive(self,args,pkg,forbidpkgs,insts,maps):
		deleted = True
		self.__callidx += 1
		if pkg in forbidpkgs:
			# we do not remove this
			deleted = False
			if pkg in insts:
				insts.remove(pkg)
			logging.info('[%d] not delete (%s)'%(self.__callidx,pkg))
			self.__callidx -= 1
			return deleted,[pkg],insts,maps
		rdeps,maps = dpkgdep.get_all_rdeps([pkg],args,insts,maps)
		logging.info('[%d](%s) rdeps(%s)'%(self.__callidx,pkg,rdeps))
		if self.__callidx > 50:
			logging.info('[%d] (%s) rdeps (%s)'%(self.__callidx,pkg,rdeps))
		retpkgs = []
		if pkg in rdeps:
			for p in rdeps:
				if p in forbidpkgs:
					# we can not make delete
					deleted = False
					break
			if deleted:
				self.__inner_remove(rdeps)
				logging.info('[%d] recycle remove (%s)'%(self.__callidx,rdeps))
			else:
				logging.info('[%d] not delete recycle (%s)'%(self.__callidx,rdeps))
			for p in rdeps:
				if p in insts:
					insts.remove(p)
				if p not in retpkgs:
					retpkgs.append(p)
			# we delete all
			rdeps = []
		while len(rdeps) > 0 and deleted :
			p = rdeps[0]
			deleted,pkgs ,insts,maps = self.__remove_recursive(args,p,forbidpkgs,insts,maps)
			for p in pkgs:
				if p not in retpkgs:
					retpkgs.append(p)
				if p in rdeps:
					rdeps.remove(p)
			if not deleted :
				# if not deleted ,so we should pretend delete all rdeps
				for p in rdeps:
					logging.info('[%d] not delete (%s)'%(self.__callidx,p))
					if p not in retpkgs:
						retpkgs.append(p)
					if p in insts:
						insts.remove(p)
		if pkg in insts:
			logging.info('[%d]remove %s'%(self.__callidx,pkg))
			if deleted:
				self.__inner_remove(pkg)
			if pkg not in retpkgs:
				retpkgs.append(pkg)
			if pkg in insts:
				insts.remove(pkg)
		self.__callidx -= 1
		return deleted,retpkgs,insts,maps


	def remove_not_dep(self,args,pkgs):
		self.__callidx = 0
		depmaps = dict()
		rdepmaps = dict()
		allinsts = dpkgdep.get_all_inst(args)
		alldeps,depmaps = dpkgdep.get_all_deps(pkgs,args,depmaps)
		essentials = dpkgdep.get_essentials(args)
		for p in essentials:
			if p not in alldeps:
				alldeps.append(p)
		rmpkgs = []
		for p in allinsts:
			if p not in alldeps :
				rmpkgs.append(p)
		while len(rmpkgs) > 0:
			logging.info('rm (%s)'%(rmpkgs[0]))
			deleted,retpkgs,allinsts,rdepmaps = self.__remove_recursive(args,rmpkgs[0],alldeps,allinsts,rdepmaps)
			newallrdeps = []
			for p in retpkgs:
				if p  in rmpkgs:
					rmpkgs.remove(p)
				if p in allinsts:
					allinsts.remove(p)
		return rmpkgs

	def __purge_rc_inner(self,pkg):
		cmds = '"%s" "%s" "%s" "%s" --purge "%s" '%(self.dpkg_sudoprefix,self.dpkg_chroot,self.dpkg_root,self.dpkg_dpkg,pkg)
		logging.info('run (%s)'%(cmds))
		retval = cmdpack.run_command_callback(cmds,None,None)
		if retval != 0 :
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'can not run (%s)'%(cmds))
		return

	def purge_rc(self,args):
		pkgs = dpkgdep.get_all_rc(args)
		for p in pkgs:
			self.__purge_rc_inner(p)
		return

	def remove_pkg(self,args,pkgs):
		allinsts  = dpkgdep.get_all_inst(args)
		essentials = dpkgdep.get_essentials(args)
		rdepmaps = dict()
		rmpkgs = []
		for p in pkgs:
			rdeps,rdepmaps = dpkgdep.get_all_rdeps([p],args,allinsts,rdepmaps)
			for cp in rdeps:
				if (cp not in rmpkgs) and (cp in allinsts):
					rmpkgs.append(cp)
			if (p not in rmpkgs) and (p in allinsts):
				rmpkgs.append(p)
		logging.info('(%s)rmpkgs (%s)'%(pkgs,rmpkgs))
		while len(rmpkgs) > 0:
			logging.info('rm (%s)'%(rmpkgs[0]))
			deleted,retpkgs,allinsts,rdepmaps = self.__remove_recursive(args,rmpkgs[0],essentials,allinsts,rdepmaps)
			logging.info('rm (%s) retpkgs(%s)'%(rmpkgs[0],retpkgs))
			for p in retpkgs:
				if p  in rmpkgs:
					rmpkgs.remove(p)
				if p in allinsts:
					allinsts.remove(p)
		return


def remove_exclude(args):
	rmdpkg = DpkgRmBase(args)
	if getattr(args,'pkgs') is None:
		raise dbgexp.DebugException(dbgexp.ERROR_INVALID_PARAMETER,'pkgs not in args')
	getpkgs = rmdpkg.remove_not_dep(args,args.pkgs)
	rmdpkg.purge_rc(args)
	return getpkgs

def remove_package(args):
	rmdpkg = DpkgRmBase(args)
	if getattr(args,'pkgs') is None:
		raise dbgexp.DebugException(dbgexp.ERROR_INVALID_PARAMETER,'pkgs not in args')
	getpkgs = rmdpkg.remove_pkg(args,args.pkgs)
	rmdpkg.purge_rc(args)
	return

def Usage(ec,fmt,parser):
	fp = sys.stderr
	if ec == 0 :
		fp = sys.stdout

	if len(fmt) > 0:
		fp.write('%s\n'%(fmt))
	parser.print_help(fp)
	sys.exit(ec)


def main():
	parser = argparse.ArgumentParser(description='dpkg encapsulation',usage='%s [options] {commands} pkgs...'%(sys.argv[0]))	
	parser.add_argument('-v','--verbose',default=0,action='count')
	parser.add_argument('-r','--root',dest='dpkg_root',default='/',action='store',help='root of dpkg specified')
	parser.add_argument('-a','--aptcache',dest='dpkg_aptcache',default='apt-cache',action='store',help='apt-cache specified')
	parser.add_argument('-g','--aptget',dest='dpkg_aptget',default='apt-get',action='store',help='apt-get specified')
	parser.add_argument('-c','--cat',dest='dpkg_cat',default='cat',action='store',help='cat specified')
	parser.add_argument('-C','--chroot',dest='dpkg_chroot',default='chroot',action='store',help='chroot specified')
	parser.add_argument('-d','--dpkg',dest='dpkg_dpkg' ,default='dpkg',action='store',help='dpkg specified')
	parser.add_argument('-t','--try',dest='dpkg_trymode',default=False,action='store_true',help='try mode')
	parser.add_argument('-m','--mount',dest='dpkg_mount',default='mount',action='store',help='mount specified')
	parser.add_argument('-u','--umount',dest='dpkg_umount',default='umount',action='store',help='umount specified')
	sub_parser = parser.add_subparsers(help='',dest='command')
	exrm_parser = sub_parser.add_parser('exrm',help='to remove package exclude')
	exrm_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get rdepend')
	rm_parser = sub_parser.add_parser('rm',help='to remove package')
	rm_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get rdepend')

	args = parser.parse_args()	

	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	try:		
		if args.command == 'exrm':
			if len(args.pkgs) < 1:
				Usage(3,'packages need',parser)
			dpkgdep.environment_before(args)
			getpkgs = remove_exclude(args)
		elif args.command == 'rm':
			if len(args.pkgs) < 1:
				Usage(3,'packages need',parser)
			dpkgdep.environment_before(args)
			getpkgs = remove_package(args)
		else:
			Usage(3,'can not get %s'%(args.command),parser)
	finally:
		dpkgdep.environment_after(args)
	return

if __name__ == '__main__':
	main()