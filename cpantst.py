#! /usr/bin/env python

import os
import sys
import extargsparse
import logging
import cmdpack
import re

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
from loglib import set_logging,load_log_commandline
from fileop import read_file
from strop import parse_int
import cpanlib


def get_perl_inc_paths(args):
    paths = re.split(':',os.environ['PATH'])
    perlbin = None
    for p in paths:
        cperl = os.path.join(p,'perl')
        if os.path.isfile(cperl):
            perlbin = cperl
            break
    if perlbin is None:
        raise Exception('cannot find perl')

    logging.info('perlbin %s'%(perlbin))
    retpaths = []
    for l in cmdpack.run_cmd_output([perlbin,'-e','foreach(@INC){print "$_\\n";}'],shellmode=False):
        retpaths.append(l.rstrip('\r\n'))
    return retpaths


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

def _check_all_is_filter(cpanpkg,missingfiles):
    retval = True
    for k in missingfiles:
        if cpanpkg.check_filter_not(k):
            continue
        logging.info('k [%s] set False'%(k))
        retval = False
    logging.info('_check_all_is_filter %s'%(retval))
    return 

def cpandep_handler(args,parser):
    set_logging(args)
    cpanpkg = cpanlib.CpanPackages(args.cpandir)
    cpanpkg.parse()
    cpandownload = cpanlib.CpanDownload(args.cpandownurl)
    for k in args.subnargs:
        deps = None
        missingfiles = []
        cont = True
        while cont:
            cont = False
            deps,missingfiles = cpanpkg.get_dep(k,True)
            logging.info('missingfiles %s'%(missingfiles))
            if deps is None:
                continue
            if _check_all_is_filter(cpanpkg,missingfiles):
                logging.info('break')
                continue
            logging.info('download missingfiles %s'%(missingfiles))
            for ck in missingfiles:
                if ck != 'perl':
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

def get_perl_module_files(incdirs,mod):
    modname = mod
    modname = re.sub('::','/',modname)
    rdict = dict()
    for d in incdirs :
        isfile = False
        isdir = False
        isauto = False
        basepath = None
        cmode = '%s/%s'%(d,modname)
        if os.path.islink(cmode) or os.path.isdir(cmode):
            basepath = d
            isdir = True
            logging.info('isdir [%s] for [%s]'%(cmode,mod))
        ccmode = '%s/%s.pm'%(d,modname)
        if os.path.isfile(ccmode):
            basepath = d
            isfile = True
            logging.info('isfile [%s] for [%s]'%(ccmode,mod))
        partmode = os.path.basename(modname)
        automode = '%s/auto/%s'%(d,modname)
        logging.info('check automode [%s]'%(automode))
        if os.path.isdir(automode):
            basepath = d
            isauto = True
            logging.info('auto [%s] ok'%(automode))

        if isfile or isdir or isauto:
            files = []
            if isdir:
                for (root,ds,fs) in os.walk('%s/%s'%(basepath,modname)):
                    logging.info('root %s ds %s fs %s'%(root,ds,fs))
                    partp = root.replace(basepath,'')
                    # to remove the first /
                    partp = partp.strip('/')
                    for f in ds:
                        files.append('%s/%s'%(partp,f))
                    for f in fs:
                        files.append('%s/%s'%(partp,f))
            if isfile:
                files.append('%s.pm'%(modname))
            if isauto:
                for (root,ds,fs) in os.walk('%s/auto/%s'%(basepath,modname)):
                    logging.info('root %s ds %s fs %s'%(root,ds,fs))
                    partp = root.replace(basepath,'')
                    # to remove the first /
                    partp = partp.strip('/')                
                    for f in ds:
                        if f.endswith('.packlist'):
                            continue
                        files.append('%s/%s'%(partp,f))
                    for f in fs:
                        if f.endswith('.packlist'):
                            continue
                        files.append('%s/%s'%(partp,f))

            files = list(set(files))
            files = sorted(files)
            rdict[basepath] = files
    return rdict


def cpanfile_handler(args,parser):
    set_logging(args)
    incs = get_perl_inc_paths(args)
    for d in args.subnargs:
        rdict = get_perl_module_files(incs,d)
        for k in rdict.keys():
            sys.stdout.write('[%s] directory [%s]\n'%(d,k))
            for f in rdict[k]:
                sys.stdout.write('    %s\n'%(f))
    sys.exit(0)

def main():
    commandline_fmt='''
    {
        "input|i" : null,
        "output|o" : null,
        "recursive|R" : false,
        "cpandir|C" : "%s",
        "cpandownurl" : "https://cpan.org/",
        "cpanls<cpanls_handler>##to list cpan##" : {
            "$" : 0
        },
        "cpandep<cpandep_handler>##[pkgname] .. to display depends##" : {
            "$" : "+"
        },
        "cpanfile<cpanfile_handler>##[mod] ... to list file in cpan file##" : {
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
