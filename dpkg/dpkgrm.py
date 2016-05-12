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
		return

	def __inner_remove(self,pkg):
		cmds = '"%s" "%s" remove --force-yes "%s" '%(self.__sudoprefix,self.__aptcache,pkg)
		retval = cmdpack.run_command_callback(cmds,None,None)
		if retval != 0 and retval != 100:
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'can not remove (%s)'%(pkg))
		return

	def __remove_recursive(self,pkg,insts):
		rdeps = dpkgdep.get_all_rdeps(pkg,self.__aptcache,self.__dpkg,insts)
		retpkgs = []
		if len(rdeps) > 0:
			for p in rdeps:
				pkgs ,insts = self.__remove_recursive(p,insts)
				for p in pkgs:
					if p not in retpkgs:
						retpkgs.append(p)
		logging.info('remove %s'%(pkg))
		retpkgs.append(pkg)
		if pkg in insts:
			insts.remove(pkg)
		return retpkgs,insts


	def remove_not_dep(self,pkgs):
		allinsts = dpkgdep.get_all_inst(self.__dpkg)
		alldeps = dpkgdep.get_all_deps(pkgs,self.__aptcache)
		rmpkgs = []
		for p in allinsts:
			if p not in alldeps:
				rmpkgs.append(p)
		while len(rmpkgs):
			retpkgs,allinsts = self.__remove_recursive(rmpkgs[0],allinsts)
			newallrdeps = []
			for p in retpkgs:
				if p  in rmpkgs:
					rmpkgs.remove(p)
		return

