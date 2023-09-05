#! /usr/bin/env python

import extargsparse
import logging
import sys
import os
import random
import time

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


class ECCInstance(object):
    def __init__(self,sslbin,outpath,params,privnum,hashnum):
        self.params = params
        self.privnum = privnum
        self.hashnum = hashnum
        self.sslbin = sslbin
        self.outpath = outpath
        self.ecprivname = '%s/ecpriv.%s.%x'%(self.outpath,self.params.name,self.privnum)
        self.ecpubname = '%s/ecpub.%s.%x'%(self.outpath,self.params.name,self.privnum)
        self.genlog = '%s/ecgen.%s.%x.log'%(self.outpath,self.params.name,self.privnum)
        self.signlog = '%s/sign.%s.%x.%x.log'%(self.outpath,self.params.name,self.privnum,self.hashnum)
        self.signbin = '%s/sign.%s.%x.%x.bin'%(self.outpath,self.params.name,self.privnum,self.hashnum)
        self.vfylog = '%s/vfy.%s.%x.%x.log'%(self.outpath,self.params.name,self.privnum,self.hashnum)
        return

    def format_code(self,tab=0):
        global GL_LINES
        s = ''
        s += format_tab_line(tab,'')
        s += format_tab_line(tab,'if [ ! -d "%s" ]'%(self.outpath))
        s += format_tab_line(tab,'then')
        s += format_tab_line(tab+1,'mkdir -p "%s"'%(self.outpath))
        s += format_tab_line(tab,'fi')
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
        s += format_tab_line(tab,'"%s" ecsignbase -o "%s" "%s" 0x%x 0x%x 2>"%s"'%(self.sslbin,self.signbin,self.ecprivname,self.hashnum,tlen,self.signlog))
        s += format_tab_line(tab,'if [ $? -ne 0 ]')
        s += format_tab_line(tab,'then')
        s += format_tab_line(tab+1,'echo "[%d]sign %s 0x%x with hashnumber 0x%x error" >&2'%(GL_LINES,self.params.name,self.privnum,self.hashnum))
        s += format_tab_line(tab+1,'exit 4')
        s += format_tab_line(tab,'fi')
        s += format_tab_line(tab,'')
        fmts = '"%s" ecvfybase "%s"'%(self.sslbin,self.params.name)
        fmts += ' 0x%x "%s" "%s" 0x%x'%(self.hashnum,self.ecpubname,self.signbin,tlen)
        fmts += ' 2>"%s"'%(self.vfylog)
        s += format_tab_line(tab,fmts)
        s += format_tab_line(tab,'if [ $? -ne 0 ]')
        s += format_tab_line(tab,'then')
        s += format_tab_line(tab+1,'echo "[%d]verify %s 0x%x with hashnumber 0x%x error" >&2'%(GL_LINES,self.params.name,self.privnum,self.hashnum))
        s += format_tab_line(tab+1,'exit 4')
        s += format_tab_line(tab,'fi')

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
    while idx < args.cases:
        curidx = random.randrange(len(ecnames))
        curname = GL_ECC_NAMES[curidx]
        curparam = GL_ECC_PARAMS[curname]
        maxb = get_bytes(curparam.order)
        privnum = format_bn(random.randbytes(maxb))
        hashnum = format_bn(random.randbytes(maxb))
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


def main():
    commandline='''
    {
        "output|o" : null,
        "input:i" : null,
        "sslbin" : null,
        "rustbin" : null,
        "sslsopath" : ["/mnt/zdisk/clibs/dynamiclib","/home/bt/source/openssl"],
        "outpath" : null,
        "cases|C" : 100,
        "fmtsslcode<fmtsslcode_handler>##to format code##" : {
            "$" : "*"
        },
        "getbn<getbn_handler>##to format bn##" : {
            "$" : "*"
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