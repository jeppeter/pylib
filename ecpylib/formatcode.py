#! /usr/bin/env python

import extargsparse
import logging
import sys
import os
import random
import time
import re

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','python-ecdsa','src')))
import fileop
import loglib

class ECCParams(object):
    def __init__(self,name,order):
        self.name = name
        self.order = order
        return

GL_ECC_PARAMS = None
GL_ECC_NAMES = []

def _init_ecc_params():
    rdict = dict()
    names = []
    rdict['sect163k1'] = ECCParams('sect163k1',0x04000000000000000000020108A2E0CC0D99F8A5EF)
    names.append('sect163k1')
    rdict['secp112r1'] = ECCParams('secp112r1',0xDB7C2ABF62E35E7628DFAC6561C5)  
    names.append('secp112r1')
    rdict['prime192v1'] = ECCParams('prime192v1',0xffffffffffffffffffffffff99def836146bc9b1b4d22831)
    names.append('prime192v1')
    rdict['secp224r1'] = ECCParams('secp224r1',0xffffffffffffffffffffffffffff16a2e0b8f03e13dd29455c5c2a3d)
    names.append('secp224r1')
    rdict['secp384r1'] = ECCParams('secp384r1',0xffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973)
    names.append('secp384r1')
    rdict['secp521r1']= ECCParams('secp521r1',0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409)
    names.append('secp521r1')
    rdict['prime192v2'] = ECCParams('prime192v2',0xfffffffffffffffffffffffe5fb1a724dc80418648d8dd31)
    names.append('prime192v2')
    rdict['prime192v3'] = ECCParams('prime192v3',0xffffffffffffffffffffffff7a62d031c83f4294f640ec13)
    names.append('prime192v3')
    rdict['prime239v1'] = ECCParams('prime239v1',0x7fffffffffffffffffffffff7fffff9e5e9a9f5d9071fbd1522688909d0b)
    names.append('prime239v1')
    return rdict,names

def init_ecc_params():
    global GL_ECC_PARAMS
    global GL_ECC_NAMES
    if GL_ECC_PARAMS is None:
        GL_ECC_PARAMS, GL_ECC_NAMES = _init_ecc_params()
    return GL_ECC_PARAMS,GL_ECC_NAMES

GL_LINES=1

def format_tab_line(tab,s):
    global GL_LINES
    rets = ''
    for i in range(tab):
        rets += '    '
    rets += s
    rets += '\n'
    GL_LINES += 1
    return rets

def get_bits(bn):
    s = '%x'%(bn)
    retv = 0
    if len(s) > 0 and bn != 0:
        retv += (len(s) - 1) * 4
        mostv = retv + 4
        while retv < mostv:
            curn = bn - (1 << retv)
            if curn <= 0:
                break
            retv += 1
    return retv

def get_bytes(bn):
    s = '%x'%(bn)
    retv = 0
    if len(s) > 0 and bn != 0:
        retv += (len(s) >> 1)
        curv = bn - (1 << retv)
        if curv > 0:
            retv += 1
    return retv

def format_bn(bs):
    retbn = 0
    for b in bs:
        curn = int(b)
        retbn <<= 8
        retbn += curn
    return retbn

def get_short_value(val):
    maxbits = get_bits(val)
    retval = val & 0xffffffff
    if maxbits > 32:
        leftbits = maxbits % 32
        if leftbits == 0:
            leftbits = 32
        logging.info('leftbits %d'%(leftbits))
        retval += (((val >> (maxbits - leftbits)) & 0xffffffff ) << 32)
    return retval


class ECCInstance(object):
    def __init__(self,sslbin,outpath,params,privnum,hashnum):
        self.params = params
        self.privnum = privnum % params.order
        self.hashnum = hashnum % params.order
        self.privnumshort = get_short_value(self.privnum)
        self.hashnumshort = get_short_value(self.hashnum)
        self.sslbin = sslbin
        self.outpath = outpath
        self.ecname = params.name
        self.ecprivname = '%s/ecpriv.%s.%x'%(self.outpath,self.params.name,self.privnumshort)
        self.ecpubname = '%s/ecpub.%s.%x'%(self.outpath,self.params.name,self.privnumshort)
        self.genlog = '%s/ecgen.%s.%x.log'%(self.outpath,self.params.name,self.privnumshort)
        self.signlog = '%s/sign.%s.%x.%x.log'%(self.outpath,self.params.name,self.privnumshort,self.hashnumshort)
        self.signbin = '%s/sign.%s.%x.%x.bin'%(self.outpath,self.params.name,self.privnumshort,self.hashnumshort)
        self.vfylog = '%s/vfy.%s.%x.%x.log'%(self.outpath,self.params.name,self.privnumshort,self.hashnumshort)
        return

    def format_code(self,tab=0):
        global GL_LINES
        s = ''
        s += format_tab_line(tab,'')
        s += format_tab_line(tab,'if [ ! -d "%s" ]'%(self.outpath))
        s += format_tab_line(tab,'then')
        s += format_tab_line(tab+1,'mkdir -p "%s"'%(self.outpath))
        s += format_tab_line(tab,'fi')
        s += format_tab_line(tab,'')
        s += format_tab_line(tab,'#TESTCASE ecgen ecname %s privnum 0x%x privnumshort 0x%x'%(self.ecname,self.privnum,self.privnumshort))
        s += format_tab_line(tab,'"%s" ecgen --ecpriv "%s" --ecpub "%s" %s 0x%x 2>"%s" '%(self.sslbin,self.ecprivname,self.ecpubname,self.params.name,self.privnum,self.genlog))
        s += format_tab_line(tab,'if [ $? -ne 0 ]')
        s += format_tab_line(tab,'then')
        s += format_tab_line(tab+1,'echo "[%d]gen %s 0x%x error" >&2'%(GL_LINES,self.params.name,self.privnum))
        s += format_tab_line(tab+1,'exit 4')
        s += format_tab_line(tab,'fi')

        ts = '%x'%(self.hashnum)
        if (len(ts) % 2) != 0:
            ts = '0%s'%(ts)
        tlen = len(ts) >> 1

        s += format_tab_line(tab,'')
        s += format_tab_line(tab,'#TESTCASE ecsignbase ecname %s privnum 0x%x hashnum 0x%x privnumshort 0x%x hashnumshort 0x%x'%(self.ecname,self.privnum,self.hashnum,self.privnumshort,self.hashnumshort))
        s += format_tab_line(tab,'"%s" ecsignbase -o "%s" "%s" 0x%x %d 2>"%s"'%(self.sslbin,self.signbin,self.ecprivname,self.hashnum,tlen,self.signlog))
        s += format_tab_line(tab,'if [ $? -ne 0 ]')
        s += format_tab_line(tab,'then')
        s += format_tab_line(tab+1,'echo "[%d]sign %s 0x%x with hashnumber 0x%x error" >&2'%(GL_LINES,self.params.name,self.privnum,self.hashnum))
        s += format_tab_line(tab+1,'exit 4')
        s += format_tab_line(tab,'fi')
        s += format_tab_line(tab,'')
        s += format_tab_line(tab,'#TESTCASE ecvfybase ecname %s privnum 0x%x hashnum 0x%x privnumshort 0x%x hashnumshort 0x%x'%(self.ecname,self.privnum,self.hashnum,self.privnumshort,self.hashnumshort))
        fmts = '"%s" ecvfybase "%s"'%(self.sslbin,self.params.name)
        fmts += '  "%s" 0x%x "%s" %d'%(self.ecpubname,self.hashnum,self.signbin,tlen)
        fmts += ' 2>"%s"'%(self.vfylog)
        s += format_tab_line(tab,fmts)
        s += format_tab_line(tab,'if [ $? -ne 0 ]')
        s += format_tab_line(tab,'then')
        s += format_tab_line(tab+1,'echo "[%d]verify %s 0x%x with hashnumber 0x%x error" >&2'%(GL_LINES,self.params.name,self.privnum,self.hashnum))
        s += format_tab_line(tab+1,'exit 4')
        s += format_tab_line(tab,'fi')

        return s

class RustInstance(object):

    def _format_win_path(self,*args):
        retp = os.path.join(*args)
        retp = retp.replace('\\','\\\\')
        return retp

    def __init__(self,rustbin,outpath,params,privnum,hashnum):
        self.params = params
        self.privnum = privnum % params.order
        self.hashnum = hashnum % params.order
        self.rustbin = rustbin
        self.rustoutpath = outpath
        self.ecname = params.name
        self.privnumshort = get_short_value(self.privnum)
        self.hashnumshort = get_short_value(self.hashnum)
        self.ecprivname = self._format_win_path(self.rustoutpath,'rust.ecpriv.%s.%x'%(self.params.name,self.privnumshort))
        self.ecpubname = self._format_win_path(self.rustoutpath,'rust.ecpub.%s.%x'%(self.params.name,self.privnumshort))
        self.genlog = self._format_win_path(self.rustoutpath,'rust.ecgen.%s.%x.log'%(self.params.name,self.privnumshort))
        self.signlog = self._format_win_path(self.rustoutpath,'rust.sign.%s.%x.%x.log'%(self.params.name,self.privnumshort,self.hashnumshort))
        self.signbin = self._format_win_path(self.rustoutpath,'rust.sign.%s.%x.%x.bin'%(self.params.name,self.privnumshort,self.hashnumshort))
        self.vfylog = self._format_win_path(self.rustoutpath,'rust.vfy.%s.%x.%x.log'%(self.params.name,self.privnumshort,self.hashnumshort))
        return

    def format_code(self,tab):
        global GL_LINES
        s = ''
        s += format_tab_line(tab,'')
        s += format_tab_line(tab,'REM TESTCASE ecgen ecname %s privnum 0x%x privnumshort 0x%x'%(self.ecname,self.privnum,self.privnumshort))
        s += format_tab_line(tab,'"%s" ecgen --ecpriv "%s" --ecpub "%s" %s 0x%x 2>"%s" || (echo "[%d] run ecgen not succ" && exit /b 4)'%(self.rustbin,self.ecprivname,self.ecpubname,self.ecname,self.privnum,self.genlog,GL_LINES))
        s += format_tab_line(tab,'')
        ts = '%x'%(self.hashnum)
        if (len(ts) % 2) != 0:
            ts = '0%s'%(ts)
        tlen = len(ts) >> 1

        s += format_tab_line(tab,'REM TESTCASE ecsignbase ecname %s privnum 0x%x hashnum 0x%x privnumshort 0x%x hashnumshort 0x%x'%(self.ecname,self.privnum,self.hashnum,self.privnumshort,self.hashnumshort))
        s += format_tab_line(tab,'"%s" ecsignbase -o "%s" %s 0x%x 0x%x %d 2>"%s" || (echo "[%d] run ecsignbase not succ" && exit /b 4)'%(self.rustbin,self.signbin,self.ecname,self.privnum,self.hashnum,tlen,self.signlog,GL_LINES))
        s += format_tab_line(tab,'')
        s += format_tab_line(tab,'REM TESTCASE ecvfybase ecname %s privnum 0x%x hashnum 0x%x privnumshort 0x%x hashnumshort 0x%x'%(self.ecname,self.privnum,self.hashnum,self.privnumshort,self.hashnumshort))
        s += format_tab_line(tab,'"%s" ecvfybase %s "%s" 0x%x "%s" 2>"%s" || (echo "[%d] run ecvfybase not succ" && exit /b 4)'%(self.rustbin,self.ecname,self.ecpubname,self.hashnum,self.signbin,self.vfylog,GL_LINES))
        return s


def fmtsslcode_handler(args,parser):
    global GL_LINES
    loglib.set_logging(args)
    init_ecc_params()
    ecnames = GL_ECC_NAMES
    if len(args.subnargs) > 0:
        ecnames = args.subnargs
        for c in ecnames:
            if c not in GL_ECC_NAMES:
                raise Exception('%s not in ECC names'%(c))
    idx = 0
    s = format_tab_line(0,'#! /bin/sh')
    s += format_tab_line(0,'')
    random.seed(time.time())
    if args.sslbin is None:
        raise Exception('need sslbin')
    if args.outpath is None:
        raise Exception('need outpath')
    if len(args.sslsopath) > 0:
        fmts = ''
        for f in args.sslsopath:
            if len(fmts) > 0:
                fmts += ':%s'%(f)
            else:
                fmts += 'export LD_LIBRARY_PATH=%s'%(f)
        if len(fmts) > 0:
            s += format_tab_line(0,fmts)
    logging.info('ecnames %s'%(ecnames))
    while idx < args.cases:
        curidx = random.randrange(len(ecnames))
        curname = ecnames[curidx]
        curparam = GL_ECC_PARAMS[curname]
        maxb = get_bytes(curparam.order)
        privnum = format_bn(os.urandom(maxb))
        hashnum = format_bn(os.urandom(maxb))
        curinst = ECCInstance(args.sslbin,args.outpath,curparam,privnum,hashnum)        
        s  += curinst.format_code(0)
        idx += 1
    fileop.write_file(s,args.output)
    sys.exit(0)
    return

def getbn_handler(args,parser):
    loglib.set_logging(args)
    bnnum = 10
    bnsize = 10
    if len(args.subnargs) > 0:
        bnnum = fileop.parse_int(args.subnargs[0])
    if len(args.subnargs) > 0:
        bnsize = fileop.parse_int(args.subnargs[0])
    idx = 0
    random.seed(time.time())
    while idx < bnnum:
        nb = random.randbytes(bnsize)
        bn = format_bn(nb)
        sys.stdout.write('%s\n'%(fileop.format_bytes(nb,'nb [%d]'%(bnsize))))
        sys.stdout.write('bn 0x%x\n'%(bn))
        idx += 1
    sys.exit(0)
    return

class RustVerify(object):
    def _format_win_path(self,*args):
        retp = os.path.join(*args)
        retp = retp.replace('\\','\\\\')
        return retp
    def __init__(self,privnum,ecname,rootpath,hashnum,rustbin):
        self.rootpath = rootpath
        self.rustbin = rustbin
        self.rustbin = self.rustbin.replace('\\','\\\\')
        self.privnum = privnum
        self.hashnum = hashnum
        self.ecname = ecname
        self.privnumshort = get_short_value(self.privnum)
        self.hashnumshort = get_short_value(self.hashnum)
        self.signbin = self._format_win_path(rootpath,'sign.%s.%x.%x.bin'%(ecname,self.privnumshort,self.hashnumshort))
        self.ecpubbin = self._format_win_path(rootpath,'ecpub.%s.%x'%(ecname,self.privnumshort))
        self.vfylog = self._format_win_path(rootpath,'rust.vfy.%x.%x.log'%(self.privnumshort,self.hashnumshort))
        return

    def format_code(self,tab=0):
        rets = ''
        rets += format_tab_line(tab,'')
        rets += format_tab_line(tab,'REM TESTCASE ecvfybase ecname %s privnum 0x%x hashnum 0x%x privnumshort 0x%x hashnumshort 0x%x'%(self.ecname,self.privnum,self.hashnum,self.privnumshort,self.hashnumshort))
        rets += format_tab_line(tab,'"%s" ecvfybase -vvvvv %s "%s" 0x%x "%s" 2>"%s" || (ECHO "[%d] error run ecvfybase" && exit /b 4)'%(self.rustbin,self.ecname,self.ecpubbin,self.hashnum,self.signbin,self.vfylog, GL_LINES))
        return rets

class SslVerify(object):
    def __init__(self,privnum,ecname,rootpath,hashnum,sslbin):
        self.rootpath = rootpath
        self.sslbin = sslbin
        self.privnum = privnum
        self.hashnum = hashnum
        self.privnumshort = get_short_value(self.privnum)
        self.hashnumshort = get_short_value(self.hashnum)
        self.ecname = ecname
        self.signbin = os.path.join(rootpath,'rust.sign.%s.%x.%x.bin'%(ecname,self.privnumshort,self.hashnumshort))
        self.ecpubbin = os.path.join(rootpath,'rust.ecpub.%s.%x'%(ecname,self.privnumshort))
        self.vfylog = os.path.join(rootpath,'ssl.vfy.%x.%x.log'%(self.privnumshort,self.hashnumshort))
        return

    def format_code(self,tab=0):
        rets = format_tab_line(tab,'')
        ts = '%x'%(self.hashnum)
        if (len(ts) % 2) != 0:
            ts = '0%s'%(ts)
        tlen = len(ts) >> 1
        rets += format_tab_line(tab,'#TESTCASE ecvfybase ecname %s privnum 0x%x hashnum 0x%x privnumshort 0x%x hashnumshort 0x%x'%(self.ecname,self.privnum,self.hashnum,self.privnumshort,self.hashnumshort))        
        rets += format_tab_line(tab,'"%s" ecvfybase %s "%s" 0x%x "%s" %d 2>"%s"'%(self.sslbin,self.ecname,self.ecpubbin,self.hashnum,self.signbin,tlen,self.vfylog))
        rets += format_tab_line(tab,'if [ $? -ne 0 ]')
        rets += format_tab_line(tab,'then')
        rets += format_tab_line(tab+1,'echo "[%d] can not run ecvfybase succ"'%(GL_LINES))
        rets += format_tab_line(tab+1,'exit 4')
        rets += format_tab_line(tab,'fi')
        return rets

class SslSingle(object):
    def __init__(self,privnum,ecname,rootpath,hashnum,sslbin):
        self.rootpath = rootpath
        self.sslbin = sslbin
        self.privnum = privnum
        self.hashnum = hashnum
        self.ecname = ecname
        self.signbin = os.path.join(rootpath,'rust.sign.%s.%x.%x.bin'%(ecname,privnum,hashnum))
        self.ecpubbin = os.path.join(rootpath,'rust.ecpub.%s.%x'%(ecname,privnum))
        self.vfylog = os.path.join(rootpath,'ssl.vfy.%x.%x.log'%(self.privnum,self.hashnum))
        return

    def format_code(self,tab=0):
        rets = format_tab_line(tab,'')
        ts = '%x'%(self.hashnum)
        if (len(ts) % 2) != 0:
            ts = '0%s'%(ts)
        tlen = len(ts) >> 1
        rets += format_tab_line(tab,'"%s" ecvfybase %s "%s" 0x%x "%s" %d 2>"%s"'%(self.sslbin,self.ecname,self.ecpubbin,self.hashnum,self.signbin,tlen,self.vfylog))
        rets += format_tab_line(tab,'if [ $? -ne 0 ]')
        rets += format_tab_line(tab,'then')
        rets += format_tab_line(tab+1,'echo "[%d] can not run ecvfybase succ"'%(GL_LINES))
        rets += format_tab_line(tab+1,'exit 4')
        rets += format_tab_line(tab,'fi')
        return rets

def fmtrustcode_handler(args,parser):
    loglib.set_logging(args)
    if args.rustbin is None or len(args.rustbin) == 0:
        raise Exception('need rustbin set')
    if args.rustoutpath is None or len(args.rustoutpath) == 0:
        raise Exception('need rustoutpath set')
    # now read dir
    matchbins = dict() 
    ins = fileop.read_file(args.input)   
    sarr = re.split('\n',ins)
    matchexpr = re.compile('ecname\\s+([^ ]+)\\s+privnum\\s+0x([0-9a-fA-F]+)\\s+hashnum\\s+0x([0-9a-fA-F]+)\\s+privnumshort\\s+0x([0-9a-fA-F]+)\\s+hashnumshort\\s+0x([0-9a-fA-F]+)')
    for l in sarr:
        l = l.rstrip('\r')
        if l.startswith('#TESTCASE ecsignbase'):
            logging.info('%s'%(l))
            msarr = matchexpr.findall(l)
            if msarr is not None and len(msarr) > 0 and len(msarr[0]) >= 5:
                ecname = msarr[0][0]
                privnum = int(msarr[0][1],16)
                hashnum = int(msarr[0][2],16)
                privnumshort = get_short_value(privnum)
                hashnumshort = get_short_value(hashnum)
                keyname = '%s_%x_%x'%(ecname,privnumshort,hashnumshort)
                matchbins[keyname] = RustVerify(privnum,ecname,args.rustoutpath,hashnum,args.rustbin)
    s = ''
    for k in matchbins.keys():
        v = matchbins[k]
        s += v.format_code()
        s += format_tab_line(0,' ')
    fileop.write_file(s,args.output)
    sys.exit(0)
    return

def fmtrustsign_handler(args,parser):
    loglib.set_logging(args)
    init_ecc_params()
    ecnames = GL_ECC_NAMES
    if len(args.subnargs) > 0:
        ecnames = args.subnargs
        for c in ecnames:
            if c not in GL_ECC_NAMES:
                raise Exception('%s not in ECC names'%(c))

    if args.rustbin is None:
        raise Exception('need rustbin')
    if args.rustoutpath is None:
        raise Exception('need rustoutpath')

    idx = 0
    s = ''
    s += format_tab_line(0,'if exist "%s" ('%(args.rustoutpath))    
    s += format_tab_line(1,'echo "exist [%s]"'%(args.rustoutpath))
    s += format_tab_line(0,') else (')
    s += format_tab_line(1,'md "%s"'%(args.rustoutpath))
    s += format_tab_line(0,')')
    s += format_tab_line(0,'')
    s += format_tab_line(0,'set ECSIMPLE_LEVEL=50')
    random.seed(time.time())
    logging.info('ecnames %s'%(ecnames))
    while idx < args.cases:
        curidx = random.randrange(len(ecnames))
        curname = ecnames[curidx]
        curparam = GL_ECC_PARAMS[curname]
        maxb = get_bytes(curparam.order)
        privnum = format_bn(os.urandom(maxb))
        hashnum = format_bn(os.urandom(maxb))
        curinst = RustInstance(args.rustbin,args.rustoutpath,curparam,privnum,hashnum)
        s  += curinst.format_code(0)
        idx += 1
    fileop.write_file(s,args.output)
    sys.exit(0)
    return

def fmtsslvfy_handler(args,parser):
    loglib.set_logging(args)
    if args.sslbin is None or len(args.sslbin) == 0:
        raise Exception('need sslbin set')
    if args.outpath is None or len(args.outpath) == 0:
        raise Exception('need outpath set')
    # now read dir
    matchbins = dict()
    ins = fileop.read_file(args.input)
    sarr = re.split('\n',ins)
    matchexpr = re.compile('ecname\\s+([^ ]+)\\s+privnum\\s+0x([0-9a-fA-F]+)\\s+hashnum\\s+0x([0-9a-fA-F]+)\\s+privnumshort\\s+0x([0-9a-fA-F]+)\\s+hashnumshort\\s+0x([0-9a-fA-F]+)')
    for l in sarr:
        l = l.rstrip('\r')
        if l.startswith('REM TESTCASE ecsignbase'):
            logging.info('%s'%(l))
            msarr = matchexpr.findall(l)
            if msarr is not None and len(msarr) > 0 and len(msarr[0]) >= 5:
                ecname = msarr[0][0]
                privnum = int(msarr[0][1],16)
                hashnum = int(msarr[0][2],16)
                privnumshort = get_short_value(privnum)
                hashnumshort = get_short_value(hashnum)
                keyname = '%s_%x_%x'%(ecname,privnumshort,hashnumshort)
                matchbins[keyname] = SslVerify(privnum,ecname,args.outpath,hashnum,args.sslbin)

    s = format_tab_line(0,'#! /bin/sh')
    s += format_tab_line(0,'')
    random.seed(time.time())
    if len(args.sslsopath) > 0:
        fmts = ''
        for f in args.sslsopath:
            if len(fmts) > 0:
                fmts += ':%s'%(f)
            else:
                fmts += 'export LD_LIBRARY_PATH=%s'%(f)
        if len(fmts) > 0:
            s += format_tab_line(0,fmts)
    for k in matchbins.keys():
        v = matchbins[k]
        s += v.format_code()
    fileop.write_file(s,args.output)
    sys.exit(0)
    return

def fmtsslsingle_handler(args,parser):
    loglib.set_logging(args)
    if args.sslbin is None or len(args.sslbin) == 0:
        raise Exception('need sslbin set')
    if args.outpath is None or len(args.outpath) == 0:
        raise Exception('need outpath set')
    # now read dir
    matchbins = dict()
    ins = fileop.read_file(args.input)
    sarr = re.split('\n',ins)
    matchexpr = re.compile('ecname\\s+([^ ]+)\\s+privnum\\s+0x([0-9a-fA-F]+)\\s+hashnum\\s+0x([0-9a-fA-F]+)\\s+privnumshort\\s+0x([0-9a-fA-F]+)\\s+hashnumshort\\s+0x([0-9a-fA-F]+)')
    for l in sarr:
        l = l.rstrip('\r')
        if l.startswith('REM TESTCASE ecsignbase'):
            logging.info('%s'%(l))
            msarr = matchexpr.findall(l)
            if msarr is not None and len(msarr) > 0 and len(msarr[0]) >= 5:
                ecname = msarr[0][0]
                privnum = int(msarr[0][1],16)
                hashnum = int(msarr[0][2],16)
                privnumshort = get_short_value(privnum)
                hashnumshort = get_short_value(hashnum)
                keyname = '%s_%x_%x'%(ecname,privnumshort,hashnumshort)
                matchbins[keyname] = SslVerify(privnum,ecname,args.rustoutpath,hashnum,args.rustbin)

    s = format_tab_line(0,'#! /bin/sh')
    s += format_tab_line(0,'')
    random.seed(time.time())
    if len(args.sslsopath) > 0:
        fmts = ''
        for f in args.sslsopath:
            if len(fmts) > 0:
                fmts += ':%s'%(f)
            else:
                fmts += 'export LD_LIBRARY_PATH=%s'%(f)
        if len(fmts) > 0:
            s += format_tab_line(0,fmts)
    for k in matchbins.keys():
        v = matchbins[k]
        s += v.format_code()
    fileop.write_file(s,args.output)
    sys.exit(0)
    return


def main():
    commandline='''
    {
        "output|o" : null,
        "input|i" : null,
        "rustrand" : null,
        "sslrand" : null,
        "sslbin" : "/mnt/zdisk/clibs/test/ssltst/ssltst",
        "rustbin" : "X:\\\\ecsimple\\\\ecsimple\\\\utest\\\\ectst\\\\target\\\\release\\\\ectst.exe",
        "sslsopath" : ["/mnt/zdisk/clibs/dynamiclib","/home/bt/source/openssl"],
        "outpath" : "/mnt/zdisk/ssllogs",
        "rustoutpath" : "x:\\\\ssllogs",
        "cases|C" : 100,
        "fmtsslcode<fmtsslcode_handler>##to format code##" : {
            "$" : "*"
        },
        "getbn<getbn_handler>##to format bn##" : {
            "$" : "*"
        },
        "fmtrustcode<fmtrustcode_handler>##to format rust code##" : {
            "$" : 0
        },
        "fmtrustsign<fmtrustsign_handler>##to format rust sign code##" : {
            "$" : "*"
        },
        "fmtsslvfy<fmtsslvfy_handler>##to format ssl run code##" : {
            "$" : 0
        },
        "fmtsslsingle<fmtsslsingle_handler>##to format ssl single##" : {
            "$" : 0
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    parser = loglib.load_log_commandline(parser)
    parser.parse_command_line(None,parser)
    raise Exception('can not reach here')
    return

if __name__ == '__main__':
    main()  