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
import hashlib
import tempfile
import pwd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import dbgexp
import cmdpack
import tcebase
import tcedep
import maphandle
import extargsparse

class TceMd5Base(tcebase.TceBase):
	def __init__(self):
		super(TceMd5Base,self).__init__()
		self.__md5 = ''
		return

	def get_input(self,l):
		l = l.rstrip(' \t\r\n')
		l = l.strip(' \t')
		sarr = re.split('[\s]+',l)
		if len(sarr) > 1:
			self.__md5 = sarr[0]
		return

	def get_md5(self):
		return self.__md5

class TceMd5(TceMd5Base):
	def __init__(self,args):
		super(TceMd5,self).__init__()
		self.set_tce_attrs(args)
		return

	def check_md5(self,md5file,tczfile):
		cmd = '"%s" "%s"'%(self.tce_cat,md5file)
		retval = cmdpack.run_command_callback(cmd,tcedep.filter_context,self)
		if retval != 0 :
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
		md5cat = self.get_md5()
		# now check the file
		md5cal = hashlib.md5()
		with open(tczfile,'r+b') as f:
			for b in f:
				md5cal.update(b)
		if md5cal.hexdigest() != md5cat:
			logging.warn('%s %s not match'%(md5file,tczfile))
			return False
		return True



class TceCheck(tcedep.TceInst):
	def __init__(self,args):
		super(TceCheck,self).__init__(args)
		self.__args = args
		self.__md5expr = re.compile('(.+)\.tcz\.md5\.txt$',re.I)
		self.__tczexpr = re.compile('(.+)\.tcz$',re.I)
		return

	def __get_directory_valid(self):
		tczfiles = []
		md5files = []
		tczdict = dict()
		for f in os.listdir('%s/optional'%(self.tce_optional_dir)):
			if os.path.isfile('%s/optional/%s'%(self.tce_optional_dir,f)):
				m = self.__md5expr.findall(f)
				if m and len(m) > 0:
					if f not in md5files:
						md5files.append(f)
				m = self.__tczexpr.findall(f)
				if m and len(m) > 0:
					if f not in tczfiles:
						tczfiles.append(f)
		# now to pair it
		for p in tczfiles:
			curmd5 = '%s.md5.txt'%(p)
			if curmd5 in md5files:
				tczdict[p] = curmd5

		# now we check the file
		tcemd5 = TceMd5(self.__args)
		validpkgs = []
		for p in tczdict.keys():
			curtcz = '%s/optional/%s'%(self.tce_optional_dir,p)
			curmd5 = '%s/optional/%s'%(self.tce_optional_dir,tczdict[p])
			retval = tcemd5.check_md5(curmd5,curtcz)
			if retval :
				m = self.__tczexpr.findall(p)
				if m and len(m) > 0:
					if m[0] not in validpkgs:
						validpkgs.append(m[0])
		return validpkgs


	def check_validate(self):
		# first we should read all insts
		insts = self.get_insts()
		validpkgs = self.__get_directory_valid()

		corrupted = []
		missed = []
		for p in insts:
			if p not in validpkgs:
				if p not in corrupted:
					corrupted.append(p)

		for p in validpkgs:
			if p not in insts:
				if p not in missed:
					missed.append(p)

		logging.warn('corrupted (%s)'%(corrupted))
		logging.warn('missed (%s)'%(missed))
		self.rm_inst(corrupted)
		self.add_inst(missed)

		return corrupted,missed


class TceDownload(tcedep.TceInst):
	def __init__(self,args):
		super(TceDownload,self).__init__(args)
		self.__args = args
		return

	def __check_file(self,md5file,tczfile):
		tcemd5 = TceMd5(self.__args)
		return tcemd5.check_md5(md5file,tczfile)

	def __download_pkg(self,pkg,outdir):
		tczfile = '%s/%s.tcz'%(outdir,pkg)
		md5file = '%s/%s.tcz.md5.txt'%(outdir,pkg)
		if os.path.isfile(tczfile) and os.path.isfile(md5file):
			retval = self.__check_file(md5file,tczfile)
			if retval :
				logging.info('%s file already in'%(pkg))
				return
		cmd = '"%s" --timeout=%d -O "%s" "%s/%s/%s/tcz/%s.tcz" '%(self.tce_wget,self.tce_timeout,tczfile,self.tce_mirror,self.tce_tceversion,self.tce_platform,pkg)
		logging.info('run cmd(%s)'%(cmd))
		tries = 0
		cont = True
		while cont:
			cont = False
			retval = cmdpack.run_command_callback(cmd,None,None)
			if retval != 0 and tries > self.tce_maxtries:
				raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
			elif retval != 0 :
				cont = True
				tries += 1
		cmd = '"%s" --timeout=%d -O "%s" "%s/%s/%s/tcz/%s.tcz.md5.txt"'%(self.tce_wget,self.tce_timeout,md5file,self.tce_mirror,self.tce_tceversion,self.tce_platform,pkg)
		logging.info('run cmd(%s)'%(cmd))
		tries = 0
		cont = True
		while cont:
			cont = False
			retval = cmdpack.run_command_callback(cmd,None,None)
			if retval != 0 and tries > self.tce_maxtries:
				raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
			elif retval != 0:
				cont = True
				tries += 1
		retval = self.__check_file(md5file,tczfile)
		if not retval:
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run check(%s)(%s) not match '%(md5file,tczfile))
		return

	def download_pkg(self,pkg,parser):
		maps = tcedep.get_alldep_from_file(self.__args)
		alldeps,maps = tcedep.get_dep(self.__args,[pkg],maps)
		logging.info('alldeps (%s)'%(alldeps))
		insts = tcedep.inst_tce(self.__args,parser)
		addedpkgs = []
		while len(alldeps) > 0:
			p = alldeps.pop(0)
			self.__download_pkg(p,'%s/optional/'%(self.tce_optional_dir))
			if p not in addedpkgs and p not in insts:
				addedpkgs.append(p)


		if pkg not in insts:
			logging.info('pkg check(%s)'%(pkg))
			self.__download_pkg(pkg,'%s/optional/'%(self.tce_optional_dir))
			if pkg not in addedpkgs:
				addedpkgs.append(pkg)
		return addedpkgs

class TceInstPkgBase(TceDownload):
	def __init__(self,args):
		super(TceInstPkgBase,self).__init__(args)
		self.set_tce_attrs(args)
		self.__args = args
		return

	def __append_file(self,pkgs,lstfile):
		with open(lstfile,'a+') as f:
			for p in pkgs:
				f.write('%s.tcz\n'%(p))
		return

	def install_pkg(self,pkg,parser):
		addpkgs = self.download_pkg(pkg,parser)
		self.add_inst(addpkgs)
		return

class TceRmPkgBase(tcebase.TceBase):
	def __init__(self,args):
		super(TceRmPkgBase,self).__init__()
		self.set_tce_attrs(args)
		self.__args = args
		self.__callidx = 0
		return

	def __remove_pkg_inner(self,pkgs):
		if isinstance(pkgs,list):
			cmds = '"%" -f '%(self.tce_rm)
			for p in pkgs:
				cmds += ' "%s/optional/%s.tcz" "%s/optional/%s.tcz.md5.txt"'%(self.tce_optional_dir,p,self.tce_optional_dir,p)			
		else:
			cmds = '"%s" -f "%s/optional/%s.tcz" "%s/optional/%s.tcz.md5.txt"'%(self.tce_rm,self.tce_optional_dir,pkgs,self.tce_optional_dir,pkgs)
		logging.info('rm (%s)'%(cmds))
		retval = cmdpack.run_command_callback(cmds,None,None)
		if retval != 0 :
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
		return


	def __remove_pkg_recursive(self,pkg,insts,depmaps,rdepmaps):
		ok = True
		self.__callidx += 1
		rmpkgs = []
		if self.__callidx > 50:
			return False,rmpkgs,insts,depmaps,rdepmaps
		allrdeps,depmaps,rdepmaps = tcedep.get_wget_rdep(self.__args,[pkg],depmaps,rdepmaps)
		willremoved = []
		if pkg in allrdeps:
			self.__remove_pkg_inner(allrdeps)
			for p in allrdeps:
				if p in insts:
					insts.remove(p)
					if p not in rmpkgs:
						rmpkgs.append(p)
		else:
			for p in allrdeps:
				if p in insts:
					if p not in willremoved:
						willremoved.append(p)
		while len(willremoved) > 0 and ok :
			curpkg = willremoved.pop(0)
			ok,removed , insts,depmaps,rdepmaps = self.__remove_pkg_recursive(curpkg,insts,depmaps,rdepmaps)
			for p in removed:
				if p not in rmpkgs:
					rmpkgs.append(p)
				if p in insts:
					insts.remove(p)
				if p in willremoved:
					willremoved.remove(p)

		if ok and pkg in insts:
			self.__remove_pkg_inner(pkg)
			if pkg not in rmpkgs:
				rmpkgs.append(pkg)
			insts.remove(pkg)
		self.__callidx -= 1
		return ok,rmpkgs,insts,depmaps,rdepmaps



	def rm_pkg(self,pkgs,parser):
		depmaps = tcedep.get_alldep_from_file(self.__args)
		rdepmaps = dict()
		depmaps,rdepmaps = tcedep.transform_to_rdep(depmaps,rdepmaps)
		insts = tcedep.inst_tce(self.__args,parser)
		removed = []
		for p in pkgs:
			ok , curremoved,insts,depmaps,rdepmaps = self.__remove_pkg_recursive(p,insts,depmaps,rdepmaps)
			if not ok :
				raise dbgexp.DebugException(dbgexp.ERROR_DOWNLOAD_ERROR,'can not remove error(%s)'%(p))
			for cp in curremoved:
				if cp not in removed:
					removed.append(cp)
		return removed

class TceExtract(tcebase.TceBase):
	def __init__(self,args):
		super(TceExtract,self).__init__()
		self.set_tce_attrs(args)
		self.__args = args
		self.__mountdir = None
		self.__mkdirs = []
		self.__cpfiles = []
		return

	def extract_pkg(self,pkg):
		# now first 
		self.__mkdirs = []
		self.__cpfiles = []
		success = False
		try:
			self.umount_dir()
			self.__mountdir = tempfile.mkdtemp(prefix='%s.tcz'%(pkg))		
			cmd = '"%s" "%s" -o loop "%s/optional/%s.tcz" "%s"'%(self.tce_sudoprefix,self.tce_mount,self.tce_optional_dir,pkg,self.__mountdir)
			retval = cmdpack.run_command_callback(cmd,None,None)
			if retval != 0 :
				raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
			# now we should get the list file
			for root,dirs,files in os.walk(self.__mountdir):
				curroot = root.replace(self.__mountdir,'')
				rootext = '%s/%s'%(self.tce_root,curroot)
				for curf in files:
					fromf = '%s/%s'%(root,curf)
					tof = '%s/%s'%(rootext,curf)
					logging.info('cp (%s) => (%s)'%(fromf,tof))
					if not self.tce_trymode and not os.path.isdir(rootext):
						cmd = '"%s" "%s" -p "%s"'%(self.tce_sudoprefix,self.tce_mkdir,rootext)
						retval = cmdpack.run_command_callback(cmd,None,None)
						if retval != 0:
							raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
						if rootext not in self.__mkdirs:
							self.__mkdirs.append(rootext)
						dstat = os.stat(root)
						uowner = pwd.getpwuid(dstat.st_uid).pw_name
						gowner = pwd.getpwuid(dstat.st_gid).pw_name
						cmd = '"%s" "%s" %s:%s %s'%(self.tce_sudoprefix,self.tce_chown,uowner,gowner,rootext)
						logging.info('mkdir %s mode (%s:%s)'%(rootext,uowner,gowner))
						retval = cmdpack.run_command_callback(cmd,None,None)
						if retval != 0:
							raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
					if not self.tce_trymode:
						cmd = '"%s" "%s" -a "%s" "%s"'%(self.tce_sudoprefix,self.tce_cp,fromf,tof)
						retval = cmdpack.run_command_callback(cmd,None,None)
						if retval != 0:
							raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
						if tof not in self.__cpfiles:
							self.__cpfiles.append(tof)				
			success = True
		finally:
			if self.tce_rollback and not success:
				cmd = '"%s" "%s" -f '%(self.tce_sudoprefix,self.tce_rm)
				removed = 0
				for p in self.__cpfiles:
					cmd += ' "%s"'%(p)
					removed += 1

				if removed > 0 :
					cmdpack.run_command_callback(cmd,None,None)
				cmd = '"%s" "%s" -rf '%(self.tce_sudoprefix,self.tce_rm)
				removed = 0
				for p in self.__mkdirs:
					cmd += ' "%s"'%(p)
					removed += 1
				if removed > 0 :
					cmdpack.run_command_callback(cmd ,None,None)
			self.umount_dir()
		return

	def extract_pkg_with_test(self,pkg):
		# now first 
		self.__mkdirs = []
		self.__cpfiles = []
		success = False
		try:
			self.umount_dir()
			self.__mountdir = tempfile.mkdtemp(prefix='%s.tcz'%(pkg))		
			cmd = '"%s" "%s" -o loop "%s/optional/%s.tcz" "%s"'%(self.tce_sudoprefix,self.tce_mount,self.tce_optional_dir,pkg,self.__mountdir)
			retval = cmdpack.run_command_callback(cmd,None,None)
			if retval != 0 :
				raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
			# now we should get the list file
			for root,dirs,files in os.walk(self.__mountdir):
				curroot = root.replace(self.__mountdir,'')
				rootext = '%s/%s'%(self.tce_root,curroot)
				for curf in files:
					fromf = '%s/%s'%(root,curf)
					tof = '%s/%s'%(rootext,curf)
					if not self.tce_trymode and not os.path.isdir(rootext):
						cmd = '"%s" "%s" -p "%s"'%(self.tce_sudoprefix,self.tce_mkdir,rootext)
						retval = cmdpack.run_command_callback(cmd,None,None)
						if retval != 0:
							raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
						if rootext not in self.__mkdirs:
							self.__mkdirs.append(rootext)
						dstat = os.stat(root)
						uowner = pwd.getpwuid(dstat.st_uid).pw_name
						gowner = pwd.getpwuid(dstat.st_gid).pw_name
						cmd = '"%s" "%s" %s:%s %s'%(self.tce_sudoprefix,self.tce_chown,uowner,gowner,rootext)
						logging.info('mkdir %s mode (%s:%s)'%(rootext,uowner,gowner))
						retval = cmdpack.run_command_callback(cmd,None,None)
						if retval != 0:
							raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
					if not self.tce_trymode:
						if os.path.isfile(tof):
							# this 
							if len(self.__cpfiles) == 0 and len(self.__mkdirs) == 0 :
								logging.info('guess %s alread installed'%(pkg))
								success = True
								return
						logging.info('cp (%s) => (%s)'%(fromf,tof))
						cmd = '"%s" "%s" -a "%s" "%s"'%(self.tce_sudoprefix,self.tce_cp,fromf,tof)
						retval = cmdpack.run_command_callback(cmd,None,None)
						if retval != 0:
							raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
						if tof not in self.__cpfiles:
							self.__cpfiles.append(tof)				
			success = True
		finally:
			if self.tce_rollback and not success:
				cmd = '"%s" "%s" -f '%(self.tce_sudoprefix,self.tce_rm)
				removed = 0
				for p in self.__cpfiles:
					cmd += ' "%s"'%(p)
					removed += 1

				if removed > 0 :
					cmdpack.run_command_callback(cmd,None,None)
				cmd = '"%s" "%s" -rf '%(self.tce_sudoprefix,self.tce_rm)
				removed = 0
				for p in self.__mkdirs:
					cmd += ' "%s"'%(p)
					removed += 1
				if removed > 0 :
					cmdpack.run_command_callback(cmd ,None,None)
			self.umount_dir()
		return


	def unextract_pkg(self,pkg):
		totallistmap = tcedep.getlist_tce(self.__args)
		if pkg in totallistmap.keys():
			removed = 0
			cmd = '"%s" "%s" -f '%(self.tce_sudoprefix,self.tce_rm)
			for p in totallistmap[pkg]:
				curf = '%s/%s'%(self.tce_root,p)
				if os.path.isfile(curf)  :
					logging.info('remove %s'%(curf))
					if not self.tce_trymode:
						cmd += ' "%s"'%(curf)
						removed += 1
			if removed > 0:
				retval = cmdpack.run_command_callback(cmd,None,None)
				if retval != 0:
					raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
			removedirs = 0
			cmd = '"%s" "%s" -rf'%(self.tce_sudoprefix,self.tce_rm)
			for p in totallistmap[pkg]:
				curd = '%s/%s'%(self.tce_root,p)
				if os.path.isdir(curd):
					if not os.listdir(curd):
						logging.info('remove %s'%(curd))
						if not self.tce_trymode:
							cmd += ' "%s"'%(curd)
							removedirs += 1
			if removedirs > 0:
				retval = cmdpack.run_command_callback(cmd,None,None)
				if retval != 0:
					raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
		return







	def umount_dir(self):
		if self.__mountdir is not None:
			cmd = '"%s" "%s" "%s"'%(self.tce_sudoprefix,self.tce_umount,self.__mountdir)
			retval = cmdpack.run_command_callback(cmd,None,None)
			if retval != 0 :
				logging.warn('run (%s) error(%d)'%(cmd,retval))
			os.removedirs(self.__mountdir)
		self.__mountdir = None
		return

	def __del__(self):
		self.umount_dir()

def Usage(ec,fmt,parser):
	fp = sys.stderr
	if ec == 0 :
		fp = sys.stdout

	if len(fmt) > 0:
		fp.write('%s\n'%(fmt))
	parser.print_help(fp)
	sys.exit(ec)
	return

def download_handler(args,context):
	tcebase.set_log_level(args)
	logging.info('download %s'%(args.subnargs))
	tcedownload = TceDownload(args)
	for p in args.subnargs:
		tcedownload.download_pkg(p,context)
	sys.exit(0)
	return

def install_handler(args,context):
	tcebase.set_log_level(args)
	logging.info('install %s'%(args.subnargs))
	tceinstall = TceInstPkgBase(args)
	for p in args.subnargs:
		tceinstall.install_pkg(p,context)
	sys.exit(0)
	return

def check_handler(args,context):
	tcebase.set_log_level(args)
	tcecheck = TceCheck(args)
	tcecheck.check_validate()
	sys.exit(0)
	return

def extract_handler(args,context):
	tcebase.set_log_level(args)
	tceex = TceExtract(args)
	for p in args.subnargs:
		tceex.extract_pkg(p)
	sys.exit(0)
	return

def unextract_handler(args,context):
	tcebase.set_log_level(args)
	tceex = TceExtract(args)
	for p in args.subnargs:
		tceex.unextract_pkg(p)
	sys.exit(0)
	return

def extractinst_handler(args,context):
	tcebase.set_log_level(args)
	insts = tcedep.inst_tce(args,context)
	tceex = TceExtract(args)
	for p in insts:
		tceex.extract_pkg(p)
	sys.exit(0)
	return

def extractinsttest_handler(args,context):
	tcebase.set_log_level(args)
	insts = tcedep.inst_tce(args,context)
	tceex = TceExtract(args)
	for p in insts:
		tceex.extract_pkg_with_test(p)
	sys.exit(0)
	return

def unextractinst_handler(args,context):
	tcebase.set_log_level(args)
	insts = tcedep.inst_tce(args,context)
	tceex = TceExtract(args)
	for p in insts:
		tceex.unextract_pkg(p)
	sys.exit(0)
	return


def rm_handler(args,context):
	tcebase.set_log_level(args)
	tcerm = TceRmPkgBase(args)
	removed = tcerm.rm_pkg(args.subnargs,context)
	tceinst = tcedep.TceInst(args)
	tceinst.rm_inst(removed)
	sys.exit(0)
	return


tce_inst_command_line={
	'download<download_handler>##download pkg...##' : {
		'$' : '*'
	},
	'install<install_handler>## install packages... ##':{
		'$' : '*'
	},
	'check<check_handler>## check install and make integrition ##' : {
		'$' : 0
	},
	'rm<rm_handler>## remove packages... ##' : {
		'$' : '*'
	},
	'extract<extract_handler>## extract packages... to root ##' : {
		'$' : '*'
	},
	'unextract<unextract_handler>## just opposite fro packages... ##' : {
		'$' : '*'
	},
	'extractinst<extractinst_handler>## to extract all install packages into tce_root ##' :{
		'$' : 0
	},
	'unextractinst<unextractinst_handler>## to unextract all install packages from tce_root ##':{
		'$' : 0
	},
	'extractinsttest<extractinsttest_handler>## test whether packages installed ##' : {
		'$' : 0
	}
}


def main():
	usage_str='%s [options] {commands} pkgs...'%(sys.argv[0])
	parser = extargsparse.ExtArgsParse(description='dpkg encapsulation',usage=usage_str)
	parser = tcebase.add_tce_args(parser)
	parser.load_command_line(tce_inst_command_line)
	args = parser.parse_command_line(None,parser)
	Usage(3,'no command specified',parser)
	return

if __name__ == '__main__':
	main()
