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
		l = self.strip_line(l)
		if len(l) > 0:
			if l not in self.__deps:
				self.__deps.append(l)
		return

	def get_depend(self):
		return self.__deps


class TceAvailBase(tcebasic.TceBase):
	def __init__(self):
		self.__avails = []
		self.__started = False
		self.__htmlformat = False
		
		return

	def get_input(self,l):
		l = self.strip_line(l)
		if 


def filter_context(instr,context):
	context.get_input(instr)
	return


class TceDep(TceDepBase):
	def __init__(self,args):
		super(TceDep,self).__init__()
		self.set_tce_attrs(args)
		return

	def get_deps(self,pkg):
		depfile = '%s/%s/%s.tcz.dep'%(self.tce_root,self.tce_optional_dir,pkg)
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

def format_map_list(maps ,pkg):
	retlists = []
	if pkg not in maps.key():
		return retlists
	for p in maps[pkg]:
		if p not in retlists:
			retlists.append(p)
	slen = len(retlists)
	while True:
		for p in retlists:
			if p not in maps.key():
				continue
			for cp in maps[p]:
				if cp not in retlists:
					retlists.append(cp)
		clen = len(retlists)
		if clen == slen:
			break
		slen = clen
	return retlists

def get_available(args):


def get_dep(args,pkgs,depmap):
	scaned = 0
	alldeps = []
	for p in pkgs:
		if p in depmap.keys():
			continue
		tcedep = TceDep(args)
		depmap[p] = tcedep.get_deps(p)

	for p in pkgs:
		retlists = format_map_list(depmap,p)
		for cp in retlists:
			if cp not in alldeps:
				alldeps.append(cp)
	slen = len(alldeps)
	while True:
		for p in alldeps:
			if p not in depmap.key():
				tcedep = TceDep(args)
				depmap[p] = tcedep.get_deps()
		newdeps = []
		for p in alldeps:
			newdeps.append(p)

		for p in alldeps:
			retlists = format_map_list(depmap,p)
			for cp in retlists:
				if cp not in newdeps:
					newdeps.append(cp)
		clen = newdeps
		if clen == slen:
			break
		alldeps = []
		for p in newdeps:
			alldeps.append(p)
		slen = clen
	return alldeps,depmap

def Usage(ec,fmt,parser):
	fp = sys.stderr
	if ec == 0 :
		fp = sys.stdout

	if len(fmt) > 0:
		fp.write('%s\n'%(fmt))
	parser.print_help(fp)
	sys.exit(ec)



def main():
	parser = argparse.ArgumentParser(description='tce encapsulation',usage='%s [options] {commands} pkgs...'%(sys.argv[0]))	
	tcebasic.add_tce_args(parser)
	sub_parser = parser.add_subparsers(help='',dest='command')
	dep_parser = sub_parser.add_parser('dep',help='get depends')
	dep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get depend')
	rdep_parser = sub_parser.add_parser('rdep',help='get rdepends')
	rdep_parser.add_argument('pkgs',metavar='N',type=str,nargs='+',help='package to get rdepend')
	inst_parser = sub_parser.add_parser('inst',help='get installed')
	all_parser = sub_parser.add_parser('all',help='get all available')
	args = parser.parse_args()	
	args = tcebasic.load_tce_jsonfile(args)
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')

	if args.command == 'dep':
	elif args.command == 'rdep':
	elif args.command == 'inst':
	elif args.command == 'all' :
	else:
		raise dbgexp.DebugException(dbgexp.ERROR_INVALID_PARAMETER,'command (%s) not recognized'%(args.command))

	return

if __name__ =='__main__':
	main()
