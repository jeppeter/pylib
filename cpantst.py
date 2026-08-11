#! /usr/bin/env python

import os
import sys
import extargsparse

sys.path.insert(0,os.path.join(os.path.dirname(__file__),'pythonlib'))
sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
import extargsparse
from loglib import set_logging,load_log_commandline
from strop import parse_int
import cpanlib



def cpanls_handler(args,parser):
	set_logging(args)
	cpanpkg = cpanlib.CpanPackages(args.cpandir)
	cpanpkg.parse()
	mnlen = 0
	mvlen = 0
	mflen = 0
	keys = cpanpkg.maps.keys()
	keys = sorted(keys)
	for k in keys:
		if len(k) >= mnlen:
			mnlen = len(k) + 1
		cdict = cpanpkg.maps[k]
		if len(cdict[cpanlib.VERSION_KEYWORD]) >= mvlen:
			mvlen = len(cdict[cpanlib.VERSION_KEYWORD]) + 1
		if len(cdict[cpanlib.TARFILE_KEYWORD]) >= mflen:
			mflen = len(cdict[cpanlib.TARFILE_KEYWORD]) + 1

	for k in keys:
		cdict = cpanpkg.maps[k]
		sys.stdout.write('%-*s %-*s %-*s\n'%(mnlen,k,mvlen,cdict[cpanlib.VERSION_KEYWORD],mflen,cdict[cpanlib.TARFILE_KEYWORD]))
	sys.exit(0)
	return

def cpandep_handler(args,parser):
	set_logging(args)
	cpanpkg = cpanlib.CpanPackages(args.cpandir)
	cpanpkg.parse()
	cpandownload = cpanlib.CpanDownload(args.cpandownurl)
	for k in args.subnargs:
		while True:
			deps,missingfiles = cpanpkg.get_dep(k,True)
			if deps is None:
				break
			if len(missingfiles) == 0:
				break
			for ck in missingfiles:
				retval = cpandownload.download_file(ck)
				if not retval :
					sys.stderr.write('down [%s] error [%s]\n'%(ck,cpandownload.get_error()))
					sys.exit(3)

		if deps is None:
			sys.stderr.write('error on [%s] :%s\n'%(k,cpanpkg.get_error()))
		else:
			sys.stdout.write('%s depends\n'%(k))
			for ck in deps:
				sys.stdout.write('    %s\n'%(ck))

	sys.exit(0)
	return

def main():
    commandline_fmt='''
    {
        "input|i" : null,
        "output|o" : null,
        "recursive|R" : false,
        "cpandir|C" : "%s",
        "cpandownurl" : "https://meta.metacpan.org/",
        "cpanls<cpanls_handler>##to list cpan##" : {
        	"$" : 0
        },
        "cpandep<cpandep_handler>##[pkgname] .. to display depends##" : {
        	"$" : "+"
        }
    }
    '''
    defcpandir = '%s/.cpan'%(os.environ['HOME'])
    commandline = commandline_fmt%(defcpandir)
    parser = extargsparse.ExtArgsParse()
    load_log_commandline(parser)
    parser.load_command_line_string(commandline)
    parser.parse_command_line(None,parser)
    raise Exception('can not here for no command handle')
    return


if __name__ == '__main__':
    main()
