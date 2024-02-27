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

class Maxsize:
    def __init__(self):
        self.maxsize = 0
        return

    def set_max_length(self,s):
        if len(s) > self.maxsize:
            self.maxsize = len(s)
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
        v = sort_uniq(depmap[k])
        depmap[k] = v

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

class AccessMap(object):
    def __init__(self,rdict):
        self.__map = rdict
        self.__accessmap = dict()
        for k in self.__map.keys():
            self.__accessmap[k] = False
        return

    def get_value(self,k):
        retval = []
        if k in self.__map.keys():
            retval.extend(self.__map[k])
            self.__accessmap[k] = True
        return retval

    def is_accessed(self,k):
        retval = False
        if k in self.__accessmap.keys():
            retval = self.__accessmap[k]
        return retval

    def access(self,k):
        if k in self.__accessmap.keys():
            self.__accessmap[k] = True
        return

    def _get_map(self,k):
        retval = []
        logging.info('k %s'%(k))
        if k in self.__map.keys():
            if not self.__accessmap[k]:
                logging.info('extend [%s] %s'%(k,self.__map[k]))
                retval.extend(self.__map[k])
                self.__accessmap[k] = True
        logging.info('retval %s'%(retval))
        return retval

    def _reset_access(self):
        for k in self.__map.keys():
            self.__accessmap[k] = False


    def get_map(self,k,recur=False):
        retval = []
        self._reset_access()
        retval.extend(self._get_map(k))
        cont = True
        while cont and recur:
            cont = False
            oldpkgs = []
            oldpkgs.extend(retval)
            logging.info('oldpkgs %s'%(oldpkgs))
            for v in oldpkgs:
                nval = self._get_map(v)
                if len(nval) != 0:
                    cont = True
                    retval.extend(nval)
                    retval = sort_uniq(retval)

        return retval





def depends_handler(args,parser):
    logop.set_logging(args)
    ds = fileop.read_file(args.depmap)
    depjson = json.loads(ds)
    depmap = AccessMap(depjson)
    for k in args.subnargs:
        deps = depmap.get_map(k,True)
        msize = Maxsize()
        for v in deps:
            msize.set_max_length(v)
        sys.stdout.write('%s deps'%(k))
        idx = 0
        while idx < len(deps):
            if (idx % 5) == 0:
                sys.stdout.write('\n   ')
                sys.stdout.flush()
            sys.stdout.write(' %-*s'%(msize.maxsize,deps[idx]))
            idx += 1
        sys.stdout.write('\n')

    sys.exit(0)
    return

def rdepends_handler(args,parser):
    logop.set_logging(args)
    rs = fileop.read_file(args.rdepmap)
    rdepjson = json.loads(rs)
    rdepmap = AccessMap(rdepjson)
    for k in args.subnargs:
        rdeps = rdepmap.get_map(k,True)
        msize = Maxsize()
        for v in rdeps:
            msize.set_max_length(v)
        sys.stdout.write('%s rdeps'%(k))
        idx = 0
        while idx < len(rdeps):
            if (idx % 5) == 0:
                sys.stdout.write('\n   ')
                sys.stdout.flush()
            sys.stdout.write(' %-*s'%(msize.maxsize,rdeps[idx]))
            idx += 1
        sys.stdout.write('\n')

    sys.exit(0)
    return


def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "depmap|D" : null,
        "rdepmap|R" : null,
        "depmap<depmap_handler>## [depmapfile] [rdepmapfile] to format dep map##" : {
            "$" : "+"
        },
        "depends<depends_handler>##pkgnames ... to give depends##" : {
            "$" : "+"
        },
        "rdepends<rdepends_handler>##pkgname ... to give rdepends##" : {
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