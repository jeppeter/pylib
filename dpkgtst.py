#! /usr/bin/env python

import os
import sys
import extargsparse

sys.path.insert(0,os.path.join(os.path.dirname(__file__),'pythonlib'))
sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
import extargsparse
from loglib import set_logging,load_log_commandline
from strop import parse_int
import dpkglib


def dep_handler(args,parser):
	set_logging(args)
	dpkgfile = args.dpkgfile
	if dpkgfile is None:
		dpkgfile = '/var/lib/dpkg/status'		
	db = dpkglib.DpkgDeps(dpkgfile)
	maxline = 1
	for d in args.subnargs:
		deps = db.get_dep(d,args.recursive)
		idx = 0
		while idx < len(deps):
			if len(deps[idx]) >= maxline:
				maxline = len(deps[idx]) + 1
			idx += 1

	for d in args.subnargs:
		deps = db.get_dep(d,args.recursive)
		sys.stdout.write('%s deps [%d]:'%(d,len(deps)))
		idx = 0
		while idx < len(deps):
			if (idx % 5) == 0:
				sys.stdout.write('\n    ')
			sys.stdout.write(' %-*s'%(maxline,deps[idx]))
			idx += 1
		sys.stdout.write('\n')
	sys.exit(0)
	return

def listfile_handler(args,parser):
	set_logging(args)
	dpkgfile = args.dpkgfile
	if dpkgfile is None:
		dpkgfile = '/var/lib/dpkg/status'		
	datadir = args.datadir
	if datadir is None:
		datadir = '/var/lib/dpkg/info'
	db = dpkglib.DpkgDeps(dpkgfile)
	fdb = dpkglib.DpkgFiles(datadir)
	deps = []
	for d in args.subnargs:
		deps.append(d)
		if args.recursive:
			deps.extend(db.get_dep(d,args.recursive))
	deps = list(set(deps))
	deps = sorted(deps)
	for d in deps:
		files = fdb.get_files(d)
		sys.stdout.write('[%s] files [%d]:\n'%(d,len(files)))
		idx = 0
		while idx < len(files):
			sys.stdout.write('\t%s\n'%(files[idx]))
			idx += 1
	sys.exit(0)
	return

def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "recursive|R" : false,
        "infodir##default is /var/lib/dpkg/info ##" : null,
        "dpkgfile##default is /var/lib/dpkg/status ##" : null,
        "dep<dep_handler>##pkg ... to list dep##" : {
        	"$" : "+"
        },
        "listfile<listfile_handler>##pkg ... to list files##" : {
        	"$" : "+"
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    load_log_commandline(parser)
    parser.load_command_line_string(commandline)
    parser.parse_command_line(None,parser)
    raise Exception('can not here for no command handle')
    return


if __name__ == '__main__':
    main()
