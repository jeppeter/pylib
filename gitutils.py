#! /usr/bin/env python

import re
import sys
import os
import traceback
import extargsparse
import logging

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import strop
import fileop
import loglib


SUBMOD_CHECK_SHELL_FMT='''#! /bin/bash


function add_rust_repo()
{
	local _repo=$1;
	local _dir=$2;

	if [ ! -d "$_dir" ]
	then
		gitclonesucc "$_repo"  "$_dir" ;
	fi
}



pushd $PWD


BASEDIR=%BASEDIRNAME%

if [ ! -d $BASEDIR ]
then
	mkdir -p $BASEDIR
fi

%CHCKE_OUT_SHELL%

popd

'''

class GitModule(object):
	def __init__(self,url,path,branch=None):
		self.url = url
		self.path = path
		self.branch = branch
		if branch is None:
			self.branch = 'master'
		return

class GitModuleParse(object):
	def __init__(self,gitmodfile):
		self.fname = gitmodfile
		self.mods = []
		self._parse_file()
		return
	def _parse_file(self):
		fh = fileop.ReadFileLarge(self.fname)
		curpath = None
		cururl = None
		curbr = None
		self.mods = []
		headerexpr = re.compile('^\\s*\\[\\s*submodule\\s+([^\\]]+)\\]',re.I)
		pathexpr = re.compile('^\\s+path\\s*=\\s*(.*)$',re.I)
		urlexpr = re.compile('^\\s+url\\s*=\\s*(.*)$',re.I)
		branchexpr = re.compile('^\\s+branch\\s*=\\s*(.*)$',re.I)
		for l in fh.fh:
			l = l.rstrip('\r\n')
			m = headerexpr.findall(l)
			if m is not None and len(m) > 0:
				if curpath is not None and cururl is not None:
					self.mods.append(GitModule(cururl,curpath,curbr))				
				cururl = None
				curpath = None
				curbr = None
				continue
			m = pathexpr.findall(l)
			if m is not None and len(m) > 0:
				curpath = m[0]
				continue
			m = urlexpr.findall(l)
			if m is not None and len(m) > 0:
				cururl = m[0]
				continue
			m = branchexpr.findall(l)
			if m is not None and len(m) > 0:
				curbr = m[0]
				continue

		if cururl is not None and curpath is not None:
			self.mods.append(GitModule(cururl,curpath,curbr))
		cururl = None
		curpath = None
		curbr = None
		return






def cloneshell_handler(args,parser):
	loglib.set_logging(args)
	if args.dstdir is None:
		raise Exception('please specified dstdir for git check out')

	gitdir = args.subnargs[0]
	# now to give 
	gitsubmodfile = os.path.join(gitdir,'.gitmodules')
	if os.path.isfile(gitsubmodfile):
		# now to get the files
		gitmods = GitModuleParse(gitsubmodfile)
		# now we should give the module
		shellscript = ''
		if len(gitmods.mods) > 0:
			shellscript += 'cd $BASEDIR && \\\n'
			idx = 0
			while idx < (len(gitmods.mods) - 1):
				curmod = gitmods.mods[idx]
				shellscript += 'add_rust_repo "%s" "%s" && \\\n'%(curmod.url,os.path.basename(curmod.path))
				idx += 1
			if idx < len(gitmods.mods):
				curmod = gitmods.mods[-1]
				shellscript += 'add_rust_repo "%s" "%s"\n'%(curmod.url,os.path.basename(curmod.path))

		outs = SUBMOD_CHECK_SHELL_FMT.replace('%BASEDIRNAME%',args.dstdir)
		outs = outs.replace('%CHCKE_OUT_SHELL%',shellscript)
		fileop.write_file(outs,args.output)
	else:
		sys.stdout.write('%s no .gitmodules\n'%(gitdir))
		sys.exit(5)
	sys.exit(0)

CHECK_OUT_FMT='''#! /bin/bash

function check_out_dir()
{
	local _repo=$1;
	local _br=$2;

	pushd $PWD;

	cd $_repo && git checkout --force $_br
	popd $PWD;
}

%CHECKOUT_COMMAND%

'''


def modchkout_handler(args,parser):
	loglib.set_logging(args)
	if args.dstdir is None:
		raise Exception('please specified dstdir for git check out')
	gitdir = args.subnargs[0]
	gitsubmodfile = os.path.join(gitdir,'.gitmodules')
	if os.path.isfile(gitsubmodfile):
		# now to get the files
		gitmods = GitModuleParse(gitsubmodfile)
		# now we should give the module
		shells = ''
		if len(gitmods.mods) > 0:
			idx = 0
			while idx < (len(gitmods.mods) - 1):
				curmod = gitmods.mods[idx]
				cpath = '%s/%s'%(args.dstdir,os.path.basename(curmod.path))
				shells += 'check_out_dir "%s" "%s" && \\\n'%(cpath,curmod.branch)
				idx += 1
			curmod = gitmods.mods[-1]
			cpath = '%s/%s'%(args.dstdir,os.path.basename(curmod.path))
			shells += 'check_out_dir "%s" "%s"'%(cpath,curmod.branch)

		outs = CHECK_OUT_FMT.replace('%CHECKOUT_COMMAND%',shells)
		fileop.write_file(outs,args.output)
	else:
		sys.stdout.write('%s no .gitmodules\n'%(gitdir))
		sys.exit(5)

	sys.exit(0)
	return

CLEAN_DIR_FMT='''#! /bin/bash

function clean_dir()
{
	local _repo=$1;
	pushd $PWD;
	cd $_repo && (find . -maxdepth 1 | grep -v '^\\./\\.git$' | grep -v '^\\.$' | xargs -I {} rm -rf {});
	popd;
}

%CLEANDIR_COMMAND%

'''


def cleandir_handler(args,parser):
	loglib.set_logging(args)
	if args.dstdir is None:
		raise Exception('please specified dstdir for git check out')
	gitdir = args.subnargs[0]
	gitsubmodfile = os.path.join(gitdir,'.gitmodules')
	if os.path.isfile(gitsubmodfile):
		# now to get the files
		gitmods = GitModuleParse(gitsubmodfile)
		# now we should give the module
		shells = ''
		if len(gitmods.mods) > 0:
			idx = 0
			while idx < (len(gitmods.mods) - 1):
				curmod = gitmods.mods[idx]
				cpath = '%s/%s'%(args.dstdir,os.path.basename(curmod.path))
				shells += 'clean_dir "%s" && \\\n'%(cpath)
				idx += 1
			curmod = gitmods.mods[-1]
			cpath = '%s/%s'%(args.dstdir,os.path.basename(curmod.path))
			shells += 'clean_dir "%s"\n'%(cpath)

		outs = CLEAN_DIR_FMT.replace('%CLEANDIR_COMMAND%',shells)
		fileop.write_file(outs,args.output)
	else:
		sys.stdout.write('%s no .gitmodules\n'%(gitdir))
		sys.exit(5)

	sys.exit(0)
	return


def main():
    commandline='''
    {
    	"input|i" : null,
    	"output|o" : null,
    	"dstdir" : null,
    	"cloneshell<cloneshell_handler>##gitdir to format shell to output##" : {
    		"$" : 1
    	},
    	"modchkout<modchkout_handler>##gitdir to checkout##" : {
    		"$" : 1
    	},
    	"cleandir<cleandir_handler>##gitdir to clean all dest##" : {
    		"$" : 1
    	}
    }
    '''
    parser = extargsparse.ExtArgsParse()
    loglib.load_log_commandline(parser)
    parser.load_command_line_string(commandline)
    parser.parse_command_line(None,parser)
    raise Exception('can not reach here')
    return

if __name__ == '__main__':
    main()