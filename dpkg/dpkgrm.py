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


class DpkgRmBase(object):
	def __init__(self,dpkg='dpkg',aptcache='apt-cache',sudoprefix='sudo'):
		self.__dpkg = dpkg
		self.__aptcache= aptcache
		self.__sudoprefix = sudoprefix
		self.__callidx = 0
		return

	def __inner_remove(self,pkg):
		cmds = '"%s" "%s" remove --force-yes "%s" '%(self.__sudoprefix,self.__aptcache,pkg)
		retval = cmdpack.run_command_callback(cmds,None,None)
		if retval != 0 and retval != 100:
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'can not remove (%s)'%(pkg))
		return

	def __remove_recursive(self,pkg,insts,maps):
		self.__callidx += 1
		rdeps,maps = dpkgdep.get_all_rdeps([pkg],self.__aptcache,self.__dpkg,insts,maps)
		retpkgs = []
		if pkg in rdeps:
			logging.info('remove %s'%(pkg))
			self.__inner_remove(pkg)
			if pkg in insts:
				insts.remove(pkg)
			rdeps.remove(pkg)
			if pkg not in retpkgs:
				retpkgs.append(pkg)
		while len(rdeps) > 0:
			p = rdeps[0]
			pkgs ,insts,maps = self.__remove_recursive(p,insts,maps)
			for p in pkgs:
				if p not in retpkgs:
					retpkgs.append(p)
				if p in rdeps:
					rdeps.remove(p)
		if pkg in insts:
			logging.info('remove %s'%(pkg))
			self.__inner_remove(pkg)
			if pkg not in retpkgs:
				retpkgs.append(pkg)
			if pkg in insts:
				insts.remove(pkg)
		self.__callidx -= 1
		return retpkgs,insts,maps


	def remove_not_dep(self,pkgs):
		self.__callidx = 0
		depmaps = dict()
		rdepmaps = dict()
		allinsts = dpkgdep.get_all_inst(self.__dpkg)
		alldeps,depmaps = dpkgdep.get_all_deps(pkgs,self.__aptcache,depmaps)
		rmpkgs = []
		for p in allinsts:
			if p not in alldeps:
				rmpkgs.append(p)
		while len(rmpkgs):
			retpkgs,allinsts,rdepmaps = self.__remove_recursive(rmpkgs[0],allinsts,rdepmaps)
			newallrdeps = []
			for p in retpkgs:
				if p  in rmpkgs:
					rmpkgs.remove(p)
		return rmpkgs


def remove_exclude(pkgs):
	rmdpkg = DpkgRmBase()
	return rmdpkg.remove_not_dep(pkgs)

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
	parser.add_argument('-a','--aptcache',default='apt-cache',action='store')
	parser.add_argument('-d','--dpkg',default='dpkg',action='store')
	sub_parser = parser.add_subparsers(help='',dest='command')
	exrm_parser = sub_parser.add_parser('exrm',help='to remove package exclude')
	exrm_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get rdepend')
	args = parser.parse_args()	

	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	if args.command == 'exrm':
		if len(args.pkgs) < 1:
			Usage(3,'packages need',parser)
		getpkgs = remove_exclude(args.pkgs)
	else:
		Usage(3,'can not get %s'%(args.command),parser)
	return

if __name__ == '__main__':
	main()