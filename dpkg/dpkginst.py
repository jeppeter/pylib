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
import dpkgbase
import extargsparse

class DpkgDownloadBase(dpkgbase.DpkgBase):
	def __init__(self,args):
		self.__args = args
		self.set_dpkg_attrs(args)
		self.__callidx = 0
		return

	def download_pkg(self,pkgs,debnamemap,directory='.'):
		cmd = ''
		lastpwd = os.getcwd()
		try:
			os.chdir(directory)
			if type(pkgs) is list:
				cmd += '"%s" download '%(self.dpkg_aptget)
				for p in pkgs:
					cmd += ' "%s"'%(p)
			else:
				cmd += '"%s" download "%s"'%(self.dpkg_aptget,pkgs)
			retval = cmdpack.run_command_callback(cmd,None,None)
			if retval != 0 :
				raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'can not download (%s) (%s)'%(cmd,pkgs))
			os.chdir(lastpwd)
			# now we should test for the packages name
			for p in os.listdir(directory):
				curf = os.path.join(directory,p)
				if os.path.isfile(curf) and curf.endswith('.deb'):
					debnamemap = dpkgdep.get_debname(self.__args,curf,debnamemap)
		finally:
			os.chdir(lastpwd)
		return debnamemap

class DpkgInstallBase(dpkgbase.DpkgBase):
	def __init__(self,args):
		self.__args = args
		self.__insted = []
		self.set_dpkg_attrs(args)
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
					curs = os.sep + os.path.basename(p)
					curd = self.dpkg_root + curs
					cpfiles.append(curd)
					instpkg.append(curs)
					shutil.copy2(p , curd)
			else:
				curs = os.sep + os.path.basename(pkg)
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
				raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'can not run (%s) (%s)'%(cmds,pkg))
		finally:
			if not self.dpkg_reserved:
				for p in cpfiles:
					os.remove(p)
		return

	def __inner_remove(self,pkgs):
		if len(pkgs) == 0:
			return
		cmd = ''
		cmd += '"%s" "%s" "%s" "%s" --remove --force-depends'%(self.dpkg_sudoprefix,self.dpkg_chroot,self.dpkg_root,self.dpkg_dpkg)
		for p in pkgs:
			cmd += ' "%s"'%(p)
		retval = cmdpack.run_command_callback(cmd,None,None)
		if retval != 0:
			logging.error('can not remove (%s)'%(pkgs))
		return




	def __download_pkg(self,pkg,downloadmap,depmaps,directory='.'):
		if pkg in downloadmap.keys():
			logging.info('no more download (%s)'%(pkg))
			depmaps = dpkgdep.get_debdep(self.__args,downloadmap[pkg],depmaps)
			return downloadmap,depmaps
		dpkgdownload = DpkgDownloadBase(self.__args)
		downloadmap = dpkgdownload.download_pkg(pkg,downloadmap,directory)
		if pkg not in downloadmap.keys():
			raise dbgexp.DebugException(dbgexp.ERROR_DOWNLOAD_ERROR,'no download(%s)'%(pkg))
		logging.info('download (%s) (%s)'%(pkg,downloadmap[pkg]))
		depmaps = dpkgdep.get_debdep(self.__args,downloadmap[pkg],depmaps)
		return downloadmap,depmaps

	def __install_pkg_recursive(self,pkg,allinsts,depmaps,downloadmap):
		retpkgs = []
		insted = True
		self.__callidx += 1
		if pkg in allinsts:
			logging.info('[%d] no more install (%s)'%(self.__callidx,pkg))
			self.__callidx -= 1
			return insted,[pkg],allinsts,depmaps,downloadmap
		alldeps,depmaps = dpkgdep.get_dep_noself([pkg],self.__args,depmaps)
		if pkg in alldeps:
			# it is in the packages
			willinstpkgs = []
			for p in alldeps:
				if p not in allinsts:
					if p not in downloadmap.keys():
						raise dbgexp.DebugException(dbgexp.ERROR_DOWNLOAD_ERROR,'not download (%s) (%s)'%(p,alldeps))
					if downloadmap[p] not in willinstpkgs:
						willinstpkgs.append(downloadmap[p])
					if p not in retpkgs:
						retpkgs.append(p)
			assert(len(willinstpkgs) > 0)
			logging.info('[%d]install (%s:%s)'%(self.__callidx,retpkgs,willinstpkgs))
			self.__inner_install(willinstpkgs)
			for p in alldeps:
				if p not in allinsts:
					allinsts.append(p)
			for p in retpkgs:
				if p not in self.__insted:
					self.__insted.append(p)
			alldeps = []
		while len(alldeps) > 0 and insted :
			insted,curretpkgs,allinsts,depmaps,downloadmap = self.__install_pkg_recursive(alldeps[0],allinsts,depmaps,downloadmap)
			if not insted :
				break
			for p in curretpkgs:
				if p not in retpkgs:
					retpkgs.append(p)
				if p not in allinsts:
					allinsts.append(p)
				if p in alldeps:
					alldeps.remove(p)
		if insted:
			if pkg not in allinsts:
				if pkg not in downloadmap.keys():
					raise dbgexp.DebugException(dbgexp.ERROR_DOWNLOAD_ERROR,'not download (%s)'%(pkg))
				logging.info('[%d]install (%s:%s)'%(self.__callidx,pkg,downloadmap[pkg]))
				self.__inner_install(downloadmap[pkg])
				allinsts.append(pkg)
			if pkg not in retpkgs:
				retpkgs.append(pkg)
			if pkg not in self.__insted:
				self.__insted.append(pkg)
		self.__callidx -= 1
		return insted,retpkgs,allinsts,downloadmap,depmaps



	def install_pkg(self,pkgs,directory='.'):
		# now first to 
		allinsts = []
		needdownloads = []
		needinstalls = []
		depmaps = dict()
		downloadmap = dict()
		instedpkgs = []
		availables = []
		success = False
		self.__insted = []
		try:
			# first we should get all installed packages
			allinsts = dpkgdep.get_all_inst(self.__args)
			if type(pkgs) is list:
				for p in pkgs :
					if p not in allinsts:
						if p not in needdownloads:
							logging.info('add (%s)'%(p))
							needdownloads.append(p)
			else:
				if pkgs not in allinsts:
					logging.info('add (%s)'%(pkgs))
					needdownloads.append(pkgs)
			alldeps ,depmaps = dpkgdep.get_all_deps([allinsts[0]],self.__args,depmaps)
			misskeys = dpkgdep.check_dep_map_integrity(depmaps)
			if len(misskeys) > 0:
				# we not get the integrity depmaps when in install
				depmaps = dpkgdep.make_normalize_dep(depmaps,allinsts)
				misskeys = dpkgdep.check_dep_map_integrity(depmaps)
				assert(len(misskeys) == 0)
			if len(needdownloads) == 0:
				# yes we need install some packages
				logging.info('no need to install (%s)'%(pkgs))
				success = True
				return instedpkgs

			availables = []
			for p in allinsts:
				if p not in availables:
					availables.append(p)
			# now we should download the packages
			while len(needdownloads) > 0:
				pkg = needdownloads[0]
				needdownloads.remove(pkg)
				try:
					downloadmap,depmaps = self.__download_pkg(pkg,downloadmap,depmaps,directory)
					if pkg not in needinstalls:
						needinstalls.append(pkg)
					if pkg not in availables:
						availables.append(pkg)
					misskeys = dpkgdep.check_dep_map_integrity(depmaps)
					for p in misskeys:
						if p not in needdownloads and p not in needinstalls:
							logging.info('add (%s)'%(p))
							needdownloads.append(p)
				except:
					logging.warn('can not download(%s)'%(pkg))
					pass

			# we make avaibles
			depmaps = dpkgdep.make_normalize_dep(depmaps,availables)
			misskeys = dpkgdep.check_dep_map_integrity(depmaps)
			if len(misskeys) > 0:
				raise dbgexp.DebugException(dbgexp.ERROR_DOWNLOAD_ERROR,'misskeys (%s)'%(misskeys))
			logging.info('need install (%s)'%(needinstalls))
			while len(needinstalls) > 0:
				pkg = needinstalls[0]
				logging.info('inst (%s)'%(pkg))
				insted,retpkgs,allinsts,downloadmap,depmaps = self.__install_pkg_recursive(pkg,allinsts,depmaps,downloadmap)
				if not insted:
					raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'can not install (%s)'%(needinstalls[0]))
				for p in retpkgs:
					if p in needinstalls:
						needinstalls.remove(p)
					if p not in instedpkgs:
						instedpkgs.append(p)
			success = True
		finally:
			# remove the file
			if not success:
				if self.dpkg_rollback:
					self.__inner_remove(self.__insted)
				else:
					logging.error('installed (%s)'%(self.__insted))
			if not self.dpkg_reserved:
				for p in downloadmap.keys():
					os.remove(downloadmap[p])
			downloadmap = dict()
			self.__insted = []
		return instedpkgs


def cmd_install_pkgs(args,pkgs,directory='.'):
	dpkginst = DpkgInstallBase(args)
	return dpkginst.install_pkg(pkgs,directory)



def Usage(ec,fmt,parser):
	fp = sys.stderr
	if ec == 0 :
		fp = sys.stdout

	if len(fmt) > 0:
		fp.write('%s\n'%(fmt))
	parser.print_help(fp)
	sys.exit(ec)


def main():
	parser = extargsparse.ExtArgsParse(description='dpkg encapsulation',usage='%s [options] {commands} pkgs...'%(sys.argv[0]))	
	parser = dpkgbase.add_dpkg_args(parser)
	sub_parser = parser.add_subparsers(help='',dest='command')
	inst_parser = sub_parser.add_parser('inst',help='to install packages')
	inst_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get rdepend')
	args = parser.parse_args()	
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	args = dpkgbase.load_dpkg_jsonfile(args)
	try:
		if args.command == 'inst':
			if len(args.pkgs) < 1:
				Usage(3,'packages need',parser)
			logging.info('pkgs (%s)'%(args.pkgs))
			args.directory = os.path.abspath(args.directory)
			dpkgdep.environment_before(args)
			getpkgs = cmd_install_pkgs(args,args.pkgs,args.directory)
		else:
			Usage(3,'can not get %s'%(args.command),parser)
	finally:
		dpkgdep.environment_after(args)
	return

if __name__ == '__main__':
	main()