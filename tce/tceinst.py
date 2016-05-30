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


class TceDownload(tcebase.TceBase):
	def __init__(self,args):
		super(TceDownload,self).__init__()
		self.set_tce_attrs(args)
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

		cmd = '"%s" -O "%s" "%s/%s/%s/tcz/%s.tcz" '%(self.tce_wget,tczfile,self.tce_mirror,self.tce_tceversion,self.tce_platform,pkg)
		logging.info('run cmd(%s)'%(cmd))
		retval = cmdpack.run_command_callback(cmd,None,None)
		if retval != 0:
			raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
		cmd = '"%s" -O "%s" "%s/%s/%s/tcz/%s.tcz.md5.txt"'%(self.tce_wget,md5file,self.tce_mirror,self.tce_tceversion,self.tce_platform,pkg)
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
		self.__append_file(addpkgs,'%s/copy2fs.lst'%(self.tce_optional_dir))
		self.__append_file(addpkgs,'%s/xbase.lst'%(self.tce_optional_dir))
		self.__append_file(addpkgs,'%s/onboot.lst'%(self.tce_optional_dir))
		return



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


tce_inst_command_line={
	'download<download_handler>##download pkg...##' : {
		'$' : '+'
	},
	'install<install_handler>## install packages... ##':{
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
