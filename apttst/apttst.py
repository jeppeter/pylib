#! /usr/bin/env python

import logging
import sys
import os
import apt
import json
import itertools, operator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'pythonlib')))
import fileop
import logop
import extargsparse

if sys.hexversion < 0x03000000:
    mapper= itertools.imap # 2.4 ≤ Python < 3
else:
    mapper= map # Python ≥ 3

def sort_uniq(sequence):
    retv = sorted(sequence)
    reto = []
    if len(retv) > 0:
        reto.append(retv[0])
    idx = 0
    while idx < (len(retv) - 1):
        if retv[idx] != retv[idx+1]:
            reto.append(retv[idx+1])
        idx += 1
    return reto


def cachelist_handler(args,parser):
    logop.set_logging(args)
    cache = apt.Cache()
    for p in cache:
        sys.stdout.write('%s %s\ncandidate\ndependencies\n'%(p,dir(p),dir(p.candidate)))
    sys.exit(0)
    return

def depmap_handler(args,parser):
    logop.set_logging(args)
    depmap = dict()
    rdepmap = dict()
    depfile = None
    rdepfile = None
    if len(args.subnargs) > 0:
        depfile = args.subnargs[0]
    if len(args.subnargs) > 1:
        rdepfile = args.subnargs[1]


    cache = apt.Cache()
    for p in cache:
        k = '%s'%(p)
        if not hasattr(p, 'candidate'):
            sys.stderr.write('%s no candidate\n%s\n'%(p,dir(p)))
            if k not in depmap.keys():
                depmap[k] = []
        else:
            if hasattr(p.candidate, 'dependencies'):
                #sys.stdout.write('%s dependency\n'%(p))
                for dps in p.candidate.dependencies:
                    for dp in dps:
                        if k not in depmap.keys():
                            depmap[k] = []
                        if dp.rawtype == 'Depends':
                            depmap[k].append(dp.name)
                        else:
                            logging.info('%s dp [%s] rawtype [%s]'%(k,dp.name,dp.rawtype))
                        #sys.stdout.write('    %s type %s\n'%(dp.name,dp.rawtype))
                #sys.stdout.write('%s dependencies\n%s\n'%(p,p.candidate.dependencies))
            else:
                if k not in depmap.keys():
                    depmap[k] = []
                sys.stderr.write('%s no candidate.dependencies\n%s\n'%(p,dir(p.candidate)))
    for k in depmap.keys():
        for p in depmap[k]:
            if p not in rdepmap.keys():
                rdepmap[p] = []
            rdepmap[p].append(k)
    for k in rdepmap.keys():
        v = sort_uniq(rdepmap[k])
        rdepmap[k] = v

    s = json.dumps(depmap,indent=4)
    fileop.write_file(s,depfile)
    s = json.dumps(rdepmap,indent=4)
    fileop.write_file(s,rdepfile)
    sys.exit(0)
    return

def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "cachelist<cachelist_handler>##to list cache##" : {
            "$" : 0
        },
        "depmap<depmap_handler>## [depmapfile] [rdepmapfile] to format dep map##" : {
            "$" : "+"
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    logop.load_log_commandline(parser)
    parser.parse_command_line(None,parser)
    raise Exception('can not reach here')
    return

if __name__ == '__main__':
    main()