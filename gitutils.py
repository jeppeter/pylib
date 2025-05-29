#! /usr/bin/env python

import re
import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import strop
import fileop
import loglib
import extargsparse


SUBMOD_CHECK_SHELL_FMT='''
#! /bin/bash


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






def submodcheckshell_handler(args,parser):
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


def main():
    commandline='''
    {
    	"input|i" : null,
    	"output|o" : null,
    	"dstdir" : null,
    	"submodcheckshell<submodcheckshell_handler>##gitdir to format shell to output##" : {
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