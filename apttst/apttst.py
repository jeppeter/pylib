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
    pidx = 0
    outs = ''
    totallen = len(cache)
    for p in cache:
        pidx += 1
        if (pidx % 100 ) == 0:
            cidx = 0
            while cidx < len(outs):
                sys.stdout.write('\b')
                cidx += 1
            outs = '%d/%d'%(pidx,totallen)
            sys.stdout.write('%s'%(outs))
            sys.stdout.flush()
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
                        elif dp.rawtype == 'PreDepends':
                            pass
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

def unicode_to_str(s):
    rets = s
    if sys.version[0] == '2':
        rets = s.encode('utf8')
    return rets

def array_unicode_to_str(sarr):
    retarr = []
    for s in sarr:
        retarr.append(unicode_to_str(s))
    return retarr

def get_filelist_inner():
    filemap = dict()

    cache = apt.Cache()
    for p in cache:
        k = '%s'%(p.name)
        #logging.info('[%s]\n%s'%(k,dir(p)))
        if p.installed:
            instfiles = array_unicode_to_str(p.installed_files)
            logging.info('[%s] installed_files\n%s'%(k,instfiles))
            filemap[k] = instfiles

    return filemap


def formfilelist_handler(args,parser):
    logop.set_logging(args)
    fmap = get_filelist_inner()
    s = json.dumps(fmap,indent=4)
    fileop.write_file(s,args.output)
    sys.exit(0)
    return

def filelist_handler(args,parser):
    logop.set_logging(args)
    cache = apt.Cache()
    retval = True
    for f in args.subnargs:
        try:
            p = cache[f]
            if p.installed:
                files = array_unicode_to_str(p.installed_files)
                msize = Maxsize()
                for cf in files:
                    msize.set_max_length(cf)
                sys.stdout.write('%s installed files'%(f))
                idx = 0
                while idx < len(files):
                    if (idx % 3) == 0:
                        sys.stdout.write('\n   ')
                    sys.stdout.write(' %-*s'%(msize.maxsize,files[idx]))
                    idx += 1
                sys.stdout.write('\n')
        except:
            retval = False
            sys.stdout.write('no %s package in cache\n'%(f))
    if not retval:
        sys.exit(5)
    sys.exit(0)
    return


def dpkgcp_handler(args,parser):
    logop.set_logging(args)
    if args.dest is None:
        raise Exception('must set --dest')
    depjson = get_depmap(args.depmap)
    depmap = AccessMap(depjson)
    if len(args.subnargs) > 0 :
        s = fileop.read_file(args.subnargs[0])
    else:
        s = fileop.read_file(None)
    sarr = re.split('\n',s)
    pkgs = []
    for l in sarr:
        l = l.rstrip('\r\n')
        if len(l) == 0:
            continue
        pkgs.extend(depmap.get_map(l,True))
        pkgs = sort_uniq(pkgs)

    cache = apt.Cache()
    retval = True
    for f in pkgs:
        try:
            p = cache[f]
            if p.installed:
                files = array_unicode_to_str(p.installed_files)
                for sf in files:
                    if  not os.path.exists(sf)  or os.path.isdir(sf):
                        continue
                    dstf = os.path.abspath(os.path.join(args.dest,sf))
                    srcf = sf
                    if not os.path.exists(dstf) or args.force:
                        dstd = os.path.dirname(dstf)
                        if not os.path.isdir(dstd):
                            os.makedirs(dstd)
                        if os.path.isfile(sf):
                            shutil.copyfile(srcf,dstf)
                        elif os.path.islink(sf):
                            if os.path.exists(dstf):
                                os.unlink(dstf)
                            srclink = os.readlink(sf)
                            os.link(srclink,dstf)
                        else:
                            logging.error('%s not recognize'%(srcf))
            else:
                sys.stderr.write('[%s] not installed\n')
                retval = False
                break
        except:
            sys.stderr.write('can not get [%s] package\n'%(f))
            retval = False

    if not retval:
        sys.exit(5)

    sys.exit(0)
    return


def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "depmap|D" : null,
        "rdepmap|R" : null,
        "dest|d" : null,
        "force|F" : false,
        "depmap<depmap_handler>## to format dep map out depmap to depmap rdepmap to rdepmap##" : {
            "$" : 0
        },
        "depends<depends_handler>##pkgnames ... to give depends##" : {
            "$" : "+"
        },
        "rdepends<rdepends_handler>##pkgname ... to give rdepends##" : {
            "$" : "+"
        },
        "formfilelist<formfilelist_handler>##to list file to installed##" : {
            "$" : 0
        },
        "filelist<filelist_handler>##pkgnames ... to list installed files##" : {
            "$" : "+"
        },
        "dpkgcp<dpkgcp_handler>##[pkgfile] to copy to dest of pkgs##" : {
            "$" : "?"
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