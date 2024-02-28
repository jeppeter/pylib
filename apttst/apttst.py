#! /usr/bin/env python

import logging
import sys
import os
import apt
import json
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'pythonlib')))
import fileop
import logop
import extargsparse


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

def filter_name(seq,k):
    reto = []
    for v in seq:
        if v != k:
            reto.append(v)
    return reto

class Maxsize:
    def __init__(self):
        self.maxsize = 0
        return

    def set_max_length(self,s):
        if len(s) > self.maxsize:
            self.maxsize = len(s)
        return


def get_depmap_rdepmap_inner():
    depmap = dict()
    rdepmap = dict()

    cache = apt.Cache()
    for p in cache:
        k = '%s'%(p)
        if not hasattr(p, 'candidate'):
            logging.debug('%s no candidate\n%s'%(p,dir(p)))
            if k not in depmap.keys():
                depmap[k] = []
        else:
            if hasattr(p.candidate, 'dependencies'):
                for dps in p.candidate.dependencies:
                    for dp in dps:
                        if k not in depmap.keys():
                            depmap[k] = []
                        if dp.rawtype == 'Depends':
                            depmap[k].append(dp.name)
                        else:
                            logging.info('%s dp [%s] rawtype [%s]'%(k,dp.name,dp.rawtype))
            else:
                if k not in depmap.keys():
                    depmap[k] = []
                logging.debug('%s no candidate.dependencies\n%s'%(p,dir(p.candidate)))

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
    return depmap,rdepmap


def depmap_handler(args,parser):
    logop.set_logging(args)
    depmap, rdepmap = get_depmap_rdepmap_inner()
    s = json.dumps(depmap,indent=4)
    fileop.write_file(s,args.depmap)
    s = json.dumps(rdepmap,indent=4)
    fileop.write_file(s,args.rdepmap)
    sys.exit(0)
    return

def get_depmap(depfile):
    if depfile  is not None:
        ds = fileop.read_file(depfile)
        depmap = json.loads(ds)
    else:
        depmap,_ = get_depmap_rdepmap_inner()
    return depmap

def get_rdepmap(rdepfile):
    if rdepfile is not None:
        rs = fileop.read_file(rdepfile)
        rdepmap = json.loads(rs)
    else:
        _ , rdepmap = get_depmap_rdepmap_inner()
    return rdepmap


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

    def get_keys(self,k):
        retval = []
        kexpr = re.compile('%s.*'%(k))
        matchedkey = False
        for k1 in self.__map.keys():
            if k1 == k:
                retval.append(k1)
                matchedkey = True
            elif kexpr.match(k1):
                retval.append(k1)
        if matchedkey:
            # if we matched ,so we should give this only one
            retval = sorted(retval)
            nv = []
            nv.append(retval[0])
            retval = []
            retval.extend(nv)

        return retval

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
        retval = filter_name(retval,k)
        return retval





def depends_handler(args,parser):
    logop.set_logging(args)
    depjson = get_depmap(args.depmap)
    depmap = AccessMap(depjson)
    for k1 in args.subnargs:
        karr = depmap.get_keys(k1)
        if len(karr) != 1:
            raise Exception('%s matches %s not 1 key'%(k1,karr))
        k = karr[0]
        deps = depmap.get_map(k,True)
        msize = Maxsize()
        for v in deps:
            msize.set_max_length(v)
        sys.stdout.write('[%s]%s deps'%(k1,k))
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
    rdepjson = get_rdepmap(args.rdepmap)
    rdepmap = AccessMap(rdepjson)
    for k1 in args.subnargs:
        karr = rdepmap.get_keys(k1)
        if len(karr) > 1:
            raise Exception('%s matches %s not 1 key'%(k1,karr))
        elif len(karr) == 1:
            k = karr[0]
            rdeps = rdepmap.get_map(k,True)
        else:
            k = k1
            # we used zero length
            rdeps = []
        msize = Maxsize()
        for v in rdeps:
            msize.set_max_length(v)
        sys.stdout.write('[%s]%s rdeps'%(k1,k))
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
        "depmap<depmap_handler>## to format dep map out depmap to depmap rdepmap to rdepmap##" : {
            "$" : 0
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