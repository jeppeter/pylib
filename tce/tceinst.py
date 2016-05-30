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
		retval = cmdpack.run_command_callback(cmd,None,None)
		if retval != 0:
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
		cmd = '"%s" --timeout=%d -O "%s" "%s/%s/%s/tcz/%s.tcz.md5.txt"'%(self.tce_wget,self.tce_timeout,md5file,self.tce_mirror,self.tce_tceversion,self.tce_platform,pkg)
		logging.info('run cmd(%s)'%(cmd))
		retval = cmdpack.run_command_callback(cmd,None,None)
		if retval != 0:
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
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
	tcedep.set_log_level(args)
	logging.info('download %s'%(args.subnargs))
	tcedownload = TceDownload(args)
	for p in args.subnargs:
		tcedownload.download_pkg(p,context)
	sys.exit(0)
	return

def install_handler(args,context):
	tcedep.set_log_level(args)
	logging.info('install %s'%(args.subnargs))
	tceinstall = TceInstPkgBase(args)
	for p in args.subnargs:
		tceinstall.install_pkg(p,context)
	sys.exit(0)
	return

def check_handler(args,context):
	tcedep.set_log_level(args)
	tcecheck = TceCheck(args)
	tcecheck.check_validate()
	sys.exit(0)
	return

def rm_handler(args,context):
	tcedep.set_log_level(args)
	tcerm = TceRmPkgBase(args)
	removed = tcerm.rm_pkg(args.subnargs,context)
	tceinst = tcedep.TceInst(args)
	tceinst.rm_inst(removed)
	sys.exit(0)
	return


tce_inst_command_line={
	'download<download_handler>##download pkg...##' : {
		'$' : '+'
	},
	'install<install_handler>## install packages... ##':{
		'$' : '+'
	},
	'check<check_handler>## check install and make integrition ##' : {
		'$' : 0
	},
	'rm<rm_handler>## remove packages... ##' : {
		'$' : '+'
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
