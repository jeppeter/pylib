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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import dbgexp
import cmdpack
import tcebasic


class TceDepBase(tcebasic.TceBase):
	def __init__(self):
		self.__deps = []
		return

	def get_input(self,l):
		l = l.rstrip(' \t')
		l = l.rstrip('\r\n')
		l = l.strip(' \t')
		if len(l) > 0:
			if l not in self.__deps:
				self.__deps.append(l)
		return

	def get_depend(self):
		return self.__deps


def filter_context(instr,context):
	context.get_input(instr)
	return


class TceDep(TceDepBase):
	def __init__(self,args):
		super(TceDep,self).__init__()
		self.set_tce_attrs(args)
		return

	def get_deps(self,pkg):
		depfile = '%s/%s.tcz.dep'%(self.tce_optional,pkg)
		cmd = ''
		if os.path.isfile(deffile):
			cmd += '"%s" "%s" "%s"'%(self.tce_sudoprefix,self.tce_cat,depfile)
		elif:
			# nothing is ,so we download from the file
			cmd += '"%s" -q -O - %s/%s/%s/tcz/%s.tcz.dep'%(self.tce_mirror,self.tce_version,self.tce_platform,pkg)
		retval = cmdpack.run_command_callback(cmd,filter_context,self)
		if retval != 0:
			if retval != 8 :
				raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd(%s) error(%d)'%(cmd,retval))
			else:
				logging.warn('%s not dep')
				return []
		return self.get_depend()

def Usage(ec,fmt,parser):
	fp = sys.stderr
	if ec == 0 :
		fp = sys.stdout

	if len(fmt) > 0:
		fp.write('%s\n'%(fmt))
	parser.print_help(fp)
	sys.exit(ec)

def add_tce_args(parser):
	parser.add_argument('-v','--verbose',default=0,action='count')
	parser.add_argument('-r','--root',dest='tce_root',default=None,action='store',help='root of dpkg specified')
	parser.add_argument('-M','--mirror',dest='tce_mirror',default=None,action='store',help='mirror site specify')
	parser.add_argument('-c','--cat',dest='tce_cat',default=None,action='store',help='cat specified')
	parser.add_argument('-C','--chroot',dest='tce_chroot',default=None,action='store',help='chroot specified')
	parser.add_argument('-t','--try',dest='tce_trymode',default=None,action='store_true',help='try mode')
	parser.add_argument('-m','--mount',dest='tce_mount',default=None,action='store',help='mount specified')
	parser.add_argument('-u','--umount',dest='tce_umount',default=None,action='store',help='umount specified')
	parser.add_argument('--chown',dest='tce_chown',default=None,action='store',help='chown specified')
	parser.add_argument('--chmod',dest='tce_chmod',default=None,action='store',help='chmod specified')
	parser.add_argument('-j','--json',dest='tce_jsonfile',default=None,action='store',help='to make json file as input args')
	return parser


def load_tce_jsonfile(args):
	if args.tce_jsonfile is None:
		# now we should 


def main():
	parser = argparse.ArgumentParser(description='tce encapsulation',usage='%s [options] {commands} pkgs...'%(sys.argv[0]))	
	add_tce_args(parser)
	sub_parser = parser.add_subparsers(help='',dest='command')
	dep_parser = sub_parser.add_parser('dep',help='get depends')
	dep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get depend')
	rdep_parser = sub_parser.add_parser('rdep',help='get rdepends')
	rdep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get rdepend')
	inst_parser = sub_parser.add_parser('inst',help='get installed')
	all_parser = sub_parser.add_parser('all',help='get all available')
	args = parser.parse_args()	
	load_tce_jsonfile(args)

	return

if __name__ =='__main__':
	main()
