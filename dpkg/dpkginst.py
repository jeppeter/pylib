#!/usr/bin/python
import os
import sys
import argparse
import logging
import shutil
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import dpkgdep
import cmdpack
import dbgexp

class DpkgDownloadBase(dpkgdep.DpkgBase):
	def __init__(self,args):
		self.dpkg_dpkg = 'dpkg'
		self.dpkg_aptget= 'apt-get'
		self.dpkg_aptcache = 'apt-cache'
		self.dpkg_sudoprefix = 'sudo'
		self.dpkg_root = '/'
		self.dpkg_trymode = False
		self.dpkg_chroot = 'chroot'
		self.__args = args
		self.get_all_attr_self(args)
		self.__callidx = 0
		return

	def download_pkg(self,pkgs,debnamemap,directory='.'):
		cmd = ''
		if type(pkgs) is list:
			cmd += 'cd "%s" && "%s" download '%(directory,self.dpkg_aptget)
			for p in pkgs:
				cmd += ' "%s"'%(p)
		else:
			cmd += 'cd "%s" && "%s" download "%s"'%(directory,self.dpkg_aptget,pkgs)
		retval = cmdpack.run_command_callback(cmds,None,None)
		if retval != 0 :
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'can not download (%s)'%(pkgs))
		# now we should test for the packages name
		for p in os.listdir(directory):
			curf = os.path.join(directory,p)
			if os.path.isfile(curf) and curf.endswith('.deb'):
				debnamemap = get_debname(self.__args,curf,debnamemap)
		return debnamemap

class DpkgInstallBase(dpkgdep.DpkgBase):
	def __init__(self,args):
		self.dpkg_dpkg = 'dpkg'
		self.dpkg_aptget= 'apt-get'
		self.dpkg_aptcache = 'apt-cache'
		self.dpkg_sudoprefix = 'sudo'
		self.dpkg_root = '/'
		self.dpkg_trymode = False
		self.dpkg_chroot = 'chroot'
		self.__args = args
		self.get_all_attr_self(args)
		self.__callidx = 0
		return

	def __inner_install(self,pkg):
		if self.dpkg_trymode :
			# we do not do this
			return
		cpfiles = []
		instpkg = []
		try:
			if type(pkg) is list:
				for p in pkg:
					curs = os.pathsep +  os.path.basename(p)
					curd = self.dpkg_root + curs
					cpfiles.append(curd)
					instpkg.append(curs)
					shutil.copy2(p , curd)
			else:
				curs = os.pathsep + os.path.basename(pkg)
				curd = self.dpkg_root + curs
				cpfiles.append(curd)
				instpkg.append(curs)
				shutil.copy2(pkg,curd)
			if type(instpkg) is list:
				cmds = '"%s" "%s" "%s" "%s" --install '%(self.dpkg_sudoprefix,self.dpkg_chroot,self.dpkg_root,self.dpkg_dpkg)
				for p in instpkg:
					cmds += ' "%s"'%(p)
			else:
				#cmds = '"%s" "%s" "%s" "%s" remove --yes "%s" '%(self.dpkg_sudoprefix,self.dpkg_chroot,self.dpkg_root,self.dpkg_aptget,pkg)
				cmds = '"%s" "%s" "%s" "%s"  --install "%s"'%(self.dpkg_sudoprefix,self.dpkg_chroot,self.dpkg_root,self.dpkg_dpkg,instpkg)
			retval = cmdpack.run_command_callback(cmds,None,None)
			if retval != 0 :
				if retval != 100:
					raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'can not remove (%s)'%(pkg))
				else:
					logging.warn('no pkg (%s)removed'%(pkg))
		finally:
			for p in cpfiles:
				os.remove(p)
		return



	def __download_pkg(self,pkg,downloadmap,depmaps,directory=''):
		if pkg in downloadmap.keys():
			return downloadmap,depmaps
		dpkgdownload = DpkgDownloadBase(self.__args)
		downloadmap = dpkgdownload.download_pkg(pkg,directory,downloadmap)
		depmaps = dpkgdep.get_debdep(self.__args,downloadmap[pkg],depmaps)
		return downloadmap,depmaps



	def install_pkg(self,pkgs,directory='.'):
		# now first to 
		downloads = []
		allinsts = []
		allprepares = []
		allavailables = []
		needdownloads = []
		depmaps = dict()
		downloadmap = dict()

		# first we should get all installed packages
		allinsts = dpkgdep.get_all_inst(self.__args)
		for p in pkgs :
			if p not in allinsts:
				if p not in needdownloads:
					needdownloads.append(p)
		alldeps ,depmaps = dpkgdep.get_all_deps(allinsts[0],self.__args,depmaps)
		misskeys = dpkgdep.check_dep_map_integrity(depmaps)
		if len(misskeys) > 0:
			# we not get the integrity depmaps when in install
			raise dbgexp.DebugException(dbgexp.ERROR_INVALID_PARAMETER,'miss dependkeys for (%s)'%(misskeys))
		allavailables = allinsts
		if len(needdownloads) == 0:
			# yes we need install some packages
			logging.info('no need to install (%s)'%(pkgs))
			return

		# now we should download the packages
		while len(needdownloads) > 0:
			pkg = needdownloads[0]
			downloadmap,depmaps = self.__download_pkg(pkg,downloadmap,depmaps,directory)
			needdownloads = needdownloads[1:]
			if pkg not in allprepares:
				allprepares.append(pkg)
			if pkg not in allavailables:
				allavailables.append(pkg)
			misskeys = dpkgdep.check_dep_map_integrity(depmaps)
			for p in misskeys:
				if p not in needdownloads:
					needdownloads.append(p)





		return


