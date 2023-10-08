#! /usr/bin/env python

import extargsparse
import logging
import sys
import os
import random
import time
import re
import hashlib

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
    rdict['prime239v2'] = ECCParams('prime239v2',0x7fffffffffffffffffffffff800000cfa7e8594377d414c03821bc582063)
    names.append('prime239v2')
    rdict['prime239v3'] = ECCParams('prime239v3',0x7fffffffffffffffffffffff7fffff975deb41b3a6057c3c432146526551)
    names.append('prime239v3')

    rdict['prime256v1'] = ECCParams('prime256v1',0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551)
    names.append('prime256v1')

    rdict['secp112r2'] = ECCParams('secp112r2',0x36df0aafd8b8d7597ca10520d04b)
    names.append('secp112r2')
    rdict['secp128r1'] = ECCParams('secp128r1',0xfffffffe0000000075a30d1b9038a115)
    names.append('secp128r1')
    rdict['secp128r2'] = ECCParams('secp128r2',0x3fffffff7fffffffbe0024720613b5a3)
    names.append('secp128r2')
    rdict['secp160k1'] = ECCParams('secp160k1',0x0100000000000000000001b8fa16dfab9aca16b6b3)
    names.append('secp160k1')

    rdict['secp160r1'] = ECCParams('secp160r1',0x0100000000000000000001f4c8f927aed3ca752257)
    names.append('secp160r1')

    rdict['secp160r2'] = ECCParams('secp160r2',0x0100000000000000000000351ee786a818f3a1a16b)
    names.append('secp160r2')
    rdict['secp192k1'] = ECCParams('secp192k1',0xfffffffffffffffffffffffe26f2fc170f69466a74defd8d)
    names.append('secp192k1')

    rdict['secp224k1'] = ECCParams('secp224k1',0x010000000000000000000000000001dce8d2ec6184caf0a971769fb1f7)
    names.append('secp224k1')

    rdict['secp256k1'] = ECCParams('secp256k1',0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141)
    names.append('secp256k1')

    rdict['wap-wsg-idm-ecid-wtls8'] = ECCParams('wap-wsg-idm-ecid-wtls8',0x0100000000000001ecea551ad837e9)
    names.append('wap-wsg-idm-ecid-wtls8')

    rdict['wap-wsg-idm-ecid-wtls9'] = ECCParams('wap-wsg-idm-ecid-wtls9',0x0100000000000000000001cdc98ae0e2de574abf33)
    names.append('wap-wsg-idm-ecid-wtls9')
    rdict['wap-wsg-idm-ecid-wtls12'] = ECCParams('wap-wsg-idm-ecid-wtls12',0xffffffffffffffffffffffffffff16a2e0b8f03e13dd29455c5c2a3d)
    names.append('wap-wsg-idm-ecid-wtls12')

    rdict['brainpoolP160r1'] = ECCParams('brainpoolP160r1',0xe95e4a5f737059dc60df5991d45029409e60fc09)
    names.append('brainpoolP160r1')

    rdict['brainpoolP160t1'] = ECCParams('brainpoolP160t1',0xe95e4a5f737059dc60df5991d45029409e60fc09)
    names.append('brainpoolP160t1')
    rdict['brainpoolP192r1'] = ECCParams('brainpoolP192r1',0xc302f41d932a36cda7a3462f9e9e916b5be8f1029ac4acc1)
    names.append('brainpoolP192r1')

    rdict['brainpoolP192t1'] = ECCParams('brainpoolP192t1',0xc302f41d932a36cda7a3462f9e9e916b5be8f1029ac4acc1)
    names.append('brainpoolP192t1')

    rdict['brainpoolP224r1'] = ECCParams('brainpoolP224r1',0xd7c134aa264366862a18302575d0fb98d116bc4b6ddebca3a5a7939f)
    names.append('brainpoolP224r1')
    rdict['brainpoolP224t1'] = ECCParams('brainpoolP224t1',0xd7c134aa264366862a18302575d0fb98d116bc4b6ddebca3a5a7939f)
    names.append('brainpoolP224t1')

    rdict['brainpoolP256r1'] = ECCParams('brainpoolP256r1',0xa9fb57dba1eea9bc3e660a909d838d718c397aa3b561a6f7901e0e82974856a7)
    names.append('brainpoolP256r1')
    rdict['brainpoolP256t1'] = ECCParams('brainpoolP256t1',0xa9fb57dba1eea9bc3e660a909d838d718c397aa3b561a6f7901e0e82974856a7)
    names.append('brainpoolP256t1')
    rdict['brainpoolP320r1'] = ECCParams('brainpoolP320r1',0xd35e472036bc4fb7e13c785ed201e065f98fcfa5b68f12a32d482ec7ee8658e98691555b44c59311)
    names.append('brainpoolP320r1')

    rdict['brainpoolP320t1'] =ECCParams('brainpoolP320t1',0xd35e472036bc4fb7e13c785ed201e065f98fcfa5b68f12a32d482ec7ee8658e98691555b44c59311)
    names.append('brainpoolP320t1')

    rdict['brainpoolP384r1'] = ECCParams('brainpoolP384r1',0x8cb91e82a3386d280f5d6f7e50e641df152f7109ed5456b31f166e6cac0425a7cf3ab6af6b7fc3103b883202e9046565)
    names.append('brainpoolP384r1')

    rdict['brainpoolP384t1'] = ECCParams('brainpoolP384t1',0x8cb91e82a3386d280f5d6f7e50e641df152f7109ed5456b31f166e6cac0425a7cf3ab6af6b7fc3103b883202e9046565)
    names.append('brainpoolP384t1')

    rdict['brainpoolP512r1'] =ECCParams('brainpoolP512r1',0xaadd9db8dbe9c48b3fd4e6ae33c9fc07cb308db3b3c9d20ed6639cca70330870553e5c414ca92619418661197fac10471db1d381085ddaddb58796829ca90069)
    names.append('brainpoolP512r1')
    rdict['brainpoolP512t1'] = ECCParams('brainpoolP512t1',0xaadd9db8dbe9c48b3fd4e6ae33c9fc07cb308db3b3c9d20ed6639cca70330870553e5c414ca92619418661197fac10471db1d381085ddaddb58796829ca90069)
    names.append('brainpoolP512t1')

    rdict['SM2'] = ECCParams('SM2',0xfffffffeffffffffffffffffffffffff7203df6b21c6052b53bbf40939d54123)
    names.append('SM2')



    # these are the gf2m coding
    rdict['sect113r1'] = ECCParams('sect113r1',0x0100000000000000d9ccec8a39e56f)
    names.append('sect113r1')
    rdict['sect113r2'] = ECCParams('sect113r2',0x010000000000000108789b2496af93)
    names.append('sect113r2')

    rdict['sect131r1'] = ECCParams('sect131r1',0x0400000000000000023123953a9464b54d)
    names.append('sect131r1')
    rdict['sect131r2'] = ECCParams('sect131r2',0x0400000000000000016954a233049ba98f)
    names.append('sect131r2')

    rdict['sect163k1'] = ECCParams('sect163k1',0x04000000000000000000020108A2E0CC0D99F8A5EF)
    names.append('sect163k1')
    rdict['sect163r1'] = ECCParams('sect163r1',0x03ffffffffffffffffffff48aab689c29ca710279b)
    names.append('sect163r1')
    rdict['sect163r2'] = ECCParams('sect163r2',0x040000000000000000000292fe77e70c12a4234c33)
    names.append('sect163r2')

    rdict['sect193r1'] = ECCParams('sect193r1',0x01000000000000000000000000c7f34a778f443acc920eba49)
    names.append('sect193r1')
    rdict['sect193r2'] = ECCParams('sect193r2',0x010000000000000000000000015aab561b005413ccd4ee99d5)
    names.append('sect193r2')

    rdict['sect233k1'] = ECCParams('sect233k1',0x8000000000000000000000000000069d5bb915bcd46efb1ad5f173abdf)
    names.append('sect233k1')

    rdict['sect233r1'] = ECCParams('sect233r1',0x01000000000000000000000000000013e974e72f8a6922031d2603cfe0d7)
    names.append('sect233r1')
    rdict['sect239k1'] = ECCParams('sect239k1',0x2000000000000000000000000000005a79fec67cb6e91f1c1da800e478a5)
    names.append('sect239k1')

    rdict['sect283k1'] = ECCParams('sect283k1',0x01ffffffffffffffffffffffffffffffffffe9ae2ed07577265dff7f94451e061e163c61)
    names.append('sect283k1')

    rdict['sect283r1'] = ECCParams('sect283r1',0x03ffffffffffffffffffffffffffffffffffef90399660fc938a90165b042a7cefadb307)
    names.append('sect283r1')
    rdict['sect409k1'] = ECCParams('sect409k1',0x007ffffffffffffffffffffffffffffffffffffffffffffffffffe5f83b2d4ea20400ec4557d5ed3e3e7ca5b4b5c83b8e01e5fcf)
    names.append('sect409k1')

    rdict['sect409r1'] = ECCParams('sect409r1',0x010000000000000000000000000000000000000000000000000001e2aad6a612f33307be5fa47c3c9e052f838164cd37d9a21173)
    names.append('sect409r1')

    rdict['sect571k1'] = ECCParams('sect571k1',0x020000000000000000000000000000000000000000000000000000000000000000000000131850e1f19a63e4b391a8db917f4138b630d84be5d639381e91deb45cfe778f637c1001)
    names.append('sect571k1')
    rdict['sect571r1'] = ECCParams('sect571r1',0x03ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe661ce18ff55987308059b186823851ec7dd9ca1161de93d5174d66e8382e9bb2fe84e47)
    names.append('sect571r1')

    rdict['c2pnb163v1'] = ECCParams('c2pnb163v1',0x0400000000000000000001e60fc8821cc74daeafc1);
    names.append('c2pnb163v1')
    rdict['c2pnb163v2'] = ECCParams('c2pnb163v2',0x03fffffffffffffffffffdf64de1151adbb78f10a7)
    names.append('c2pnb163v2')

    rdict['c2tnb191v1'] = ECCParams('c2tnb191v1',0x40000000000000000000000004a20e90c39067c893bbb9a5)
    names.append('c2tnb191v1')

    rdict['c2tnb191v2'] = ECCParams('c2tnb191v2',0x20000000000000000000000050508cb89f652824e06b8173)
    names.append('c2tnb191v2')
    rdict['c2tnb191v3'] = ECCParams('c2tnb191v3',0x155555555555555555555555610c0b196812bfb6288a3ea3)
    names.append('c2tnb191v3')

    rdict['c2pnb208w1'] = ECCParams('c2pnb208w1',0x00000101BAF95C9723C57B6C21DA2EFF2D5ED588BDD5717E212F9D)
    names.append('c2pnb208w1')

    rdict['c2tnb239v1'] = ECCParams('c2tnb239v1',0x2000000000000000000000000000000f4d42ffe1492a4993f1cad666e447)
    names.append('c2tnb239v1')
    rdict['c2tnb239v2'] = ECCParams('c2tnb239v2',0x1555555555555555555555555555553c6f2885259c31e3fcdf154624522d)
    names.append('c2tnb239v2')
    rdict['c2tnb239v3'] = ECCParams('c2tnb239v3',0x0cccccccccccccccccccccccccccccac4912d2d9df903ef9888b8a0e4cff)
    names.append('c2tnb239v3')

    rdict['c2pnb272w1'] = ECCParams('c2pnb272w1',0x0100faf51354e0e39e4892df6e319c72c8161603fa45aa7b998a167b8f1e629521)
    names.append('c2pnb272w1')

    rdict['c2pnb304w1'] = ECCParams('c2pnb304w1',0x0101d556572aabac800101d556572aabac8001022d5c91dd173f8fb561da6899164443051d)
    names.append('c2pnb304w1')

    rdict['c2tnb359v1'] = ECCParams('c2tnb359v1',0x01af286bca1af286bca1af286bca1af286bca1af286bc9fb8f6b85c556892c20a7eb964fe7719e74f490758d3b)
    names.append('c2tnb359v1')

    rdict['c2pnb368w1'] = ECCParams('c2pnb368w1',0x010090512da9af72b08349d98a5dd4c7b0532eca51ce03e2d10f3b7ac579bd87e909ae40a6f131e9cfce5bd967)
    names.append('c2pnb368w1')
    rdict['c2tnb431r1'] = ECCParams('c2tnb431r1',0x0340340340340340340340340340340340340340340340340340340323c313fab50589703b5ec68d3587fec60d161cc149c1ad4a91)
    names.append('c2tnb431r1')

    rdict['wap-wsg-idm-ecid-wtls1'] = ECCParams('wap-wsg-idm-ecid-wtls1',0x00fffffffffffffffdbf91af6dea73)
    names.append('wap-wsg-idm-ecid-wtls1')



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
        s += format_tab_line(tab,'#TESTCASE ecgenbase ecname %s privnum 0x%x privnumshort 0x%x'%(self.ecname,self.privnum,self.privnumshort))
        s += format_tab_line(tab,'"%s" ecgenbase --ecpriv "%s" --ecpub "%s" %s 0x%x 2>"%s" '%(self.sslbin,self.ecprivname,self.ecpubname,self.params.name,self.privnum,self.genlog))
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
        s += format_tab_line(tab,'REM TESTCASE ecgenbase ecname %s privnum 0x%x privnumshort 0x%x'%(self.ecname,self.privnum,self.privnumshort))
        s += format_tab_line(tab,'"%s" ecgenbase --ecpriv "%s" --ecpub "%s" %s 0x%x 2>"%s" || (echo "[%d] run ecgen not succ" && exit /b 4)'%(self.rustbin,self.ecprivname,self.ecpubname,self.ecname,self.privnum,self.genlog,GL_LINES))
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
        self.vfylog = os.path.join(rootpath,'ssl.vfy.%s.%x.%x.log'%(self.ecname,self.privnumshort,self.hashnumshort))
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
    if args.verbose >= 3:
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

def listectypes_handler(args,parser):
    loglib.set_logging(args)
    global GL_ECC_NAMES
    init_ecc_params()
    for n in GL_ECC_NAMES:
        sys.stdout.write('%s\n'%(n))
    sys.exit(0)
    return

class SslEcgenInstance(object):
    def __init__(self,opensslbin,outdir,ecname,partnum):
        self.ecname = ecname
        self.partnum = partnum
        self.opensslbin = opensslbin
        self.outdir = outdir
        self.compressed_file = os.path.join(outdir,'ecgen.%s.%d.compressed.pem'%(ecname,partnum))
        self.compressed_explicit_file = os.path.join(outdir,'ecgen.%s.%d.compressed.explicit.pem'%(ecname,partnum))
        self.uncompressed_file = os.path.join(outdir,'ecgen.%s.%d.uncompressed.pem'%(ecname,partnum))
        self.uncompressed_explicit_file = os.path.join(outdir,'ecgen.%s.%d.uncompressed.explicit.pem'%(ecname,partnum))
        self.hybrid_file = os.path.join(outdir,'ecgen.%s.%d.hybrid.pem'%(ecname,partnum))
        self.hybrid_explicit_file = os.path.join(outdir,'ecgen.%s.%d.hybrid.explicit.pem'%(ecname,partnum))
        return

    def _formaat_base(self,tab):
        rets = ''
        rets += format_tab_line(tab,'')
        rets += format_tab_line(tab,'#TESTCASE ecname %s partnum %d'%(self.ecname,self.partnum))
        privfile = os.path.join(self.outdir,'ecgen.%s.%d.base.pem'%(self.ecname,self.partnum))
        privlogfile = os.path.join(self.outdir,'ecgen.priv.%s.%d.base.log'%(self.ecname,self.partnum))
        pubfile = os.path.join(self.outdir,'ecpub.%s.%d.base.pem'%(self.ecname,self.partnum))
        publogfile = os.path.join(self.outdir,'ecpub.priv.%s.%d.base.log'%(self.ecname,self.partnum))
        rets += format_tab_line(tab,'"%s" ecparam -genkey -name %s -noout -out "%s" 2>"%s"'%(self.opensslbin,self.ecname,privfile,privlogfile))
        rets += format_tab_line(tab,'if [ $? -ne 0 ]')
        rets += format_tab_line(tab,'then')
        rets += format_tab_line(tab+1,'echo "[%d] can not make %s partnum %d base error" >&2'%(GL_LINES,self.ecname,self.partnum))
        rets += format_tab_line(tab+1,'exit 4')
        rets += format_tab_line(tab,'fi')
        rets += format_tab_line(tab,'"%s" ec -in "%s" -pubout -out "%s"  2> "%s"'%(self.opensslbin,privfile,pubfile,publogfile))
        rets += format_tab_line(tab,'if [ $? -ne 0 ]')
        rets += format_tab_line(tab,'then')
        rets += format_tab_line(tab+1,'echo "[%d] can not make pubout %s partnum %d error" >&2'%(GL_LINES,self.ecname,self.partnum))
        rets += format_tab_line(tab+1,'exit 4')
        rets += format_tab_line(tab,'fi')

        return rets

    def _format_ecgen(self,cmprtype,paramenc,tab=0):
        types = '%s'%(cmprtype)
        if paramenc is not None:
            types += '.%s'%(paramenc)
        infile = os.path.join(self.outdir,'ecgen.%s.%d.base.pem'%(self.ecname,self.partnum))
        privfile = os.path.join(self.outdir,'ecgen.%s.%d.%s.pem'%(self.ecname,self.partnum,types))
        pubfile = os.path.join(self.outdir,'ecpub.%s.%d.%s.pem'%(self.ecname,self.partnum,types))
        privlogfile = os.path.join(self.outdir,'ecgen.priv.%s.%d.%s.log'%(self.ecname,self.partnum,types))
        publogfile = os.path.join(self.outdir,'ecgen.pub.%s.%d.%s.log'%(self.ecname,self.partnum,types))
        outs = ''
        outs += format_tab_line(tab,'')
        #outs += format_tab_line(tab,'#TESTCASE ecname %s partnum %d %s'%(self.ecname,self.partnum,types))
        appends = '-conv_form %s'%(cmprtype)
        if paramenc is not None:
            appends += ' -param_enc %s'%(paramenc)
        outs += format_tab_line(tab,'"%s" ec -in "%s" -out "%s" %s 2> "%s"'%(self.opensslbin,infile,privfile,appends,privlogfile))
        outs += format_tab_line(tab,'if [ $? -ne 0 ]')
        outs += format_tab_line(tab,'then')
        outs += format_tab_line(tab+1,'echo "[%d] can not make %s partnum %d %s error" >&2'%(GL_LINES,self.ecname,self.partnum,types))
        outs += format_tab_line(tab+1,'exit 4')
        outs += format_tab_line(tab,'fi')
        outs += format_tab_line(tab,'"%s" ec -in "%s" -pubout -out "%s" %s 2> "%s"'%(self.opensslbin,infile,pubfile,appends,publogfile))
        outs += format_tab_line(tab,'if [ $? -ne 0 ]')
        outs += format_tab_line(tab,'then')
        outs += format_tab_line(tab+1,'echo "[%d] can not make pubout %s partnum %d %s error" >&2'%(GL_LINES,self.ecname,self.partnum,types))
        outs += format_tab_line(tab+1,'exit 4')
        outs += format_tab_line(tab,'fi')
        return outs


    def format_code(self,tab):
        outs = ''
        outs += self._formaat_base(tab)
        outs += self._format_ecgen('compressed',None,tab)
        outs += self._format_ecgen('uncompressed',None,tab)
        outs += self._format_ecgen('hybrid',None,tab)
        outs += self._format_ecgen('compressed','explicit',tab)
        outs += self._format_ecgen('uncompressed','explicit',tab)
        outs += self._format_ecgen('hybrid','explicit',tab)
        return outs

class SslSM2genInstance(object):
    def __init__(self,opensslbin,outdir,ecname,partnum):
        self.ecname = ecname
        self.partnum = partnum
        self.opensslbin = opensslbin
        self.outdir = outdir
        return

    def _format_nbase(self,tab):
        rets = ''
        rets += format_tab_line(tab,'')
        rets += format_tab_line(tab,'#TESTCASE ecname %s partnum %d'%(self.ecname,self.partnum))
        privfile = os.path.join(self.outdir,'ecgen.%s.%d.base.pem'%(self.ecname,self.partnum))
        privlogfile = os.path.join(self.outdir,'ecgen.priv.%s.%d.base.log'%(self.ecname,self.partnum))
        pubfile = os.path.join(self.outdir,'ecpub.%s.%d.base.pem'%(self.ecname,self.partnum))
        publogfile = os.path.join(self.outdir,'ecpub.priv.%s.%d.base.log'%(self.ecname,self.partnum))
        rets += format_tab_line(tab,'"%s" ecparam -genkey -name %s -noout -out "%s" 2>"%s"'%(self.opensslbin,self.ecname,privfile,privlogfile))
        rets += format_tab_line(tab,'if [ $? -ne 0 ]')
        rets += format_tab_line(tab,'then')
        rets += format_tab_line(tab+1,'echo "[%d] can not make %s partnum %d   error" >&2'%(GL_LINES,self.ecname,self.partnum))
        rets += format_tab_line(tab+1,'exit 4')
        rets += format_tab_line(tab,'fi')
        rets += format_tab_line(tab,'"%s" ec -in "%s" -pubout -out "%s" 2> "%s"'%(self.opensslbin,privfile,pubfile,publogfile))
        rets += format_tab_line(tab,'if [ $? -ne 0 ]')
        rets += format_tab_line(tab,'then')
        rets += format_tab_line(tab+1,'echo "[%d] can not make pubout %s partnum %d error" >&2'%(GL_LINES,self.ecname,self.partnum))
        rets += format_tab_line(tab+1,'exit 4')
        rets += format_tab_line(tab,'fi')

        return rets
        return rets

    def _formaat_base(self,tab,cmprtype,paramenc):
        rets = ''
        types = '%s'%(cmprtype)
        appends = '-conv_form %s'%(cmprtype)
        if paramenc is not None and len(paramenc) > 0:
            types += '.%s'%(paramenc)
            appends += ' -param_enc %s'%(paramenc)

        rets += format_tab_line(tab,'')
        rets += format_tab_line(tab,'#TESTCASE ecname %s partnum %d %s'%(self.ecname,self.partnum,types))
        privfile = os.path.join(self.outdir,'ecgen.%s.%d.base.%s.pem'%(self.ecname,self.partnum,types))
        privlogfile = os.path.join(self.outdir,'ecgen.priv.%s.%d.base.%s.log'%(self.ecname,self.partnum,types))
        pubfile = os.path.join(self.outdir,'ecpub.%s.%d.base.%s.pem'%(self.ecname,self.partnum,types))
        publogfile = os.path.join(self.outdir,'ecpub.priv.%s.%d.base.%s.log'%(self.ecname,self.partnum,types))
        rets += format_tab_line(tab,'"%s" ecparam -genkey -name %s -noout -out "%s" %s 2>"%s"'%(self.opensslbin,self.ecname,privfile,appends,privlogfile))
        rets += format_tab_line(tab,'if [ $? -ne 0 ]')
        rets += format_tab_line(tab,'then')
        rets += format_tab_line(tab+1,'echo "[%d] can not make %s partnum %d  base %s error" >&2'%(GL_LINES,self.ecname,self.partnum,types))
        rets += format_tab_line(tab+1,'exit 4')
        rets += format_tab_line(tab,'fi')
        rets += format_tab_line(tab,'"%s" ec -in "%s" -pubout -out "%s" %s 2> "%s"'%(self.opensslbin,privfile,pubfile,appends,publogfile))
        rets += format_tab_line(tab,'if [ $? -ne 0 ]')
        rets += format_tab_line(tab,'then')
        rets += format_tab_line(tab+1,'echo "[%d] can not make pubout %s partnum %d %s error" >&2'%(GL_LINES,self.ecname,self.partnum,types))
        rets += format_tab_line(tab+1,'exit 4')
        rets += format_tab_line(tab,'fi')

        return rets



    def format_code(self,tab):
        outs = ''
        outs += self._format_nbase(tab)
        outs += self._formaat_base(tab,'compressed',None)
        outs += self._formaat_base(tab,'uncompressed',None)
        outs += self._formaat_base(tab,'hybrid',None)
        outs += self._formaat_base(tab,'compressed','explicit')
        outs += self._formaat_base(tab,'uncompressed','explicit')
        outs += self._formaat_base(tab,'hybrid','explicit')
        return outs

class Asn1SM2Instance(object):
    def __init__(self,asn1bin,outdir,ecname,partnum):
        self.ecname = ecname
        self.partnum = partnum
        self.asn1bin = asn1bin
        self.outdir = outdir
        return

    def _formaat_base(self,tab,cmprtype,paramenc):
        rets = ''
        types = ''
        if cmprtype is not None and len(cmprtype) > 0:
            types += '%s'%(cmprtype)
        if paramenc is not None and len(paramenc) > 0:
            if len(types) > 0:
                types += '.%s'%(paramenc)
            else:
                types += '%s'%(paramenc)

        rets += format_tab_line(tab,'')
        if len(types) > 0:
            rets += format_tab_line(tab,'REM ASN1PARSE ecname %s partnum %d %s'%(self.ecname,self.partnum,types))
            privfile = os.path.join(self.outdir,'ecgen.%s.%d.base.%s.pem'%(self.ecname,self.partnum,types))
            privlogfile = os.path.join(self.outdir,'asn1.priv.%s.%d.base.%s.dump'%(self.ecname,self.partnum,types))
            pubfile = os.path.join(self.outdir,'ecpub.%s.%d.base.%s.pem'%(self.ecname,self.partnum,types))
            publogfile = os.path.join(self.outdir,'asn1.priv.%s.%d.base.%s.dump'%(self.ecname,self.partnum,types))
            rets += format_tab_line(tab,'"%s" asn1parse "%s" >"%s" || (echo "[%d] dump %s.%d %s error" >&2 && exit /b 4)'%(self.asn1bin,privfile,privlogfile,GL_LINES,self.ecname,self.partnum,types))
            rets += format_tab_line(tab,'"%s" asn1parse "%s" > "%s" || (echo "[%d] dump %s.%d %s error" >&2 && exit /b 4)'%(self.asn1bin,pubfile,publogfile,GL_LINES,self.ecname,self.partnum,types))
        else:
            rets += format_tab_line(tab,'REM ASN1PARSE ecname %s partnum %d'%(self.ecname,self.partnum))
            privfile = os.path.join(self.outdir,'ecgen.%s.%d.base.pem'%(self.ecname,self.partnum))
            privlogfile = os.path.join(self.outdir,'asn1.priv.%s.%d.base.dump'%(self.ecname,self.partnum))
            pubfile = os.path.join(self.outdir,'ecpub.%s.%d.base.pem'%(self.ecname,self.partnum))
            publogfile = os.path.join(self.outdir,'asn1.priv.%s.%d.base.dump'%(self.ecname,self.partnum))
            rets += format_tab_line(tab,'"%s" asn1parse "%s" >"%s" || (echo "[%d] dump %s.%d error" >&2 && exit /b 4)'%(self.asn1bin,privfile,privlogfile,GL_LINES,self.ecname,self.partnum))
            rets += format_tab_line(tab,'"%s" asn1parse "%s" > "%s" || (echo "[%d] dump %s.%d error" >&2 && exit /b 4)'%(self.asn1bin,pubfile,publogfile,GL_LINES,self.ecname,self.partnum))

        return rets



    def format_code(self,tab):
        outs = ''
        outs += self._formaat_base(tab,None,None)
        outs += self._formaat_base(tab,'compressed',None)
        outs += self._formaat_base(tab,'uncompressed',None)
        outs += self._formaat_base(tab,'hybrid',None)
        outs += self._formaat_base(tab,'compressed','explicit')
        outs += self._formaat_base(tab,'uncompressed','explicit')
        outs += self._formaat_base(tab,'hybrid','explicit')
        return outs


def fmtsslecgen_handler(args,parser):
    global GL_ECC_NAMES
    loglib.set_logging(args)
    init_ecc_params()
    ecnames = args.subnargs
    if len(ecnames) == 0:
        ecnames = GL_ECC_NAMES

    for n in ecnames:
        if n not in GL_ECC_NAMES:
            raise Exception('%s not in GL_ECC_NAMES'%(n))

    if args.outpath is None or len(args.outpath) == 0:
        raise Exception('need outpath set')

    opensslbin = args.opensslbin
    if opensslbin is None or len(opensslbin) == 0:
        opensslbin = 'openssl'
    idx = 0
    random.seed(time.time())
    s = ''
    s += format_tab_line(0,'#! /bin/bash')
    if len(args.sslsopath) > 0:
        sopaths = ''

        for f in args.sslsopath:
            if len(sopaths) > 0:
                sopaths += ':%s'%(f)
            else:
                sopaths = 'export LD_LIBRARY_PATH=%s'%(f)
        s += format_tab_line(0,'')
        s += format_tab_line(0,'%s'%(sopaths))
    s += format_tab_line(0,'')
    s += format_tab_line(0,'if [ ! -d "%s" ] '%(args.outpath))
    s += format_tab_line(0,'then')
    s += format_tab_line(1,'mkdir -p "%s"'%(args.outpath))
    s += format_tab_line(0,'fi')


    idx = 0
    while idx < args.cases:
        curidx = random.randrange(len(ecnames))
        curname = ecnames[curidx]
        nb = random.randbytes(8)
        bn = format_bn(nb)        
        inst = SslEcgenInstance(opensslbin,args.outpath,curname,bn)
        s += inst.format_code(0)
        if idx > 0 and (idx % 50) == 0 and args.verbose == 0:
            s += format_tab_line(0,'')
            if (idx % 500) == 0:
                s += format_tab_line(0,'echo "."')
            else:
                s += format_tab_line(0,'echo -n "."')
        idx += 1

    fileop.write_file(s,args.output)
    sys.exit(0)
    return

class RustEcprivExport(object):
    def __init__(self,rustbin,outdir,ecname,partnum):
        self.rustbin = rustbin
        self.outdir = outdir
        self.ecname = ecname
        self.partnum = partnum
        return

    def _format_rust_code(self,tab,outcmprtype,outparamenc):
        infile = os.path.join(self.outdir,'ecgen.%s.%d.base.pem'%(self.ecname,self.partnum))
        outtypes = '%s'%(outcmprtype)
        appends = '--eccmprtype %s'%(outcmprtype)
        if outparamenc is None or len(outparamenc) == 0:
            appends += ' --ecparamenc ""'
        else:
            outtypes += '.%s'%(outparamenc)
            appends += ' --ecparamenc %s'%(outparamenc)
        outfile = os.path.join(self.outdir,'rust.ecprivload.%s.%d.base.out.%s.pem'%(self.ecname,self.partnum,outtypes))
        logfile = os.path.join(self.outdir,'rust.ecprivload.%s.%d.base.out.%s.log'%(self.ecname,self.partnum,outtypes))
        rets = ''
        rets += format_tab_line(tab,'')
        rets += format_tab_line(tab,'REM RUSTECPRIV TESTCASE from ecname %s partnum %d %s'%(self.ecname,self.partnum,outtypes))
        rets += format_tab_line(tab,'"%s" ecprivload -o "%s" "%s" %s 2>"%s" || (echo "[%d]make %s error" && exit /b 4)'%(self.rustbin,outfile,infile,appends,logfile,GL_LINES,outfile))
        return rets

    def format_code(self,tab):
        rets = ''
        rets += self._format_rust_code(tab,'compressed','explicit')
        rets += self._format_rust_code(tab,'uncompressed','explicit')
        rets += self._format_rust_code(tab,'hybrid','explicit')
        rets += self._format_rust_code(tab,'compressed',None)
        rets += self._format_rust_code(tab,'uncompressed',None)
        rets += self._format_rust_code(tab,'hybrid',None)
        return rets

def fmtrustecprivload_handler(args,parser):
    loglib.set_logging(args)
    ins = fileop.read_file(args.input)
    if args.rustbin is None or len(args.rustbin) == 0:
        raise Exception('must specified rustbin')
    if args.rustoutpath is None or len(args.rustoutpath) == 0:
        raise Exception('must specified rustoutpath')
    sarr = re.split('\n',ins)
    lidx = 0
    mexpr = re.compile('^#TESTCASE\\s+ecname\\s+([^\\s]+)\\s+partnum\\s+([0-9]+)')
    outexps = dict()
    for l in sarr:
        lidx += 1
        l = l.rstrip('\r')
        if len(l) == 0:
            continue
        m = mexpr.findall(l)
        if m is not None and len(m) > 0 and len(m[0]) > 1:
            logging.info('%s'%(l))
            partnum = fileop.parse_int(m[0][1])
            ecname = m[0][0]
            ecprivexp = RustEcprivExport(args.rustbin,args.rustoutpath,ecname,partnum)
            ntypes = '%s.%d'%(ecname,partnum)
            logging.info('ntype %s'%(ntypes))
            outexps[ntypes] = ecprivexp
    s = ''
    s += format_tab_line(0,'echo off')
    s += format_tab_line(0,'if exist "%s" ('%(args.rustoutpath))    
    s += format_tab_line(1,'echo "exist [%s]"'%(args.rustoutpath))
    s += format_tab_line(0,') else (')
    s += format_tab_line(1,'md "%s"'%(args.rustoutpath))
    s += format_tab_line(0,')')
    s += format_tab_line(0,'')

    if args.verbose > 0:
        s += format_tab_line(0,'set ECSIMPLE_LEVEL=50')
        s += format_tab_line(0,'')

    idx = 0
    for k in outexps.keys():
        idx += 1
        e = outexps[k]
        s += format_tab_line(0,'')
        s += e.format_code(0)
        if (idx % 50) == 0 and args.verbose == 0:
            if (idx % 500) == 0:
                s += format_tab_line(0,'python -c "import sys;sys.stdout.write(\'.\\n\');sys.stdout.flush();"')
            else:
                s += format_tab_line(0,'python -c "import sys;sys.stdout.write(\'.\');sys.stdout.flush();"')

    fileop.write_file(s,args.output)
    sys.exit(0)
    return


class RustEcpubExport(object):
    def __init__(self,rustbin,outdir,ecname,partnum):
        self.rustbin = rustbin
        self.outdir = outdir
        self.ecname = ecname
        self.partnum = partnum
        return

    def _format_rust_code(self,tab,outcmprtype,outparamenc):
        infile = os.path.join(self.outdir,'ecpub.%s.%d.base.pem'%(self.ecname,self.partnum))
        outtypes = '%s'%(outcmprtype)
        appends = '--eccmprtype %s'%(outcmprtype)
        if outparamenc is None or len(outparamenc) == 0:
            appends += ' --ecparamenc ""'
        else:
            outtypes += '.%s'%(outparamenc)
            appends += ' --ecparamenc %s'%(outparamenc)
        outfile = os.path.join(self.outdir,'rust.ecpubload.%s.%d.base.out.%s.pem'%(self.ecname,self.partnum,outtypes))
        logfile = os.path.join(self.outdir,'rust.ecpubload.%s.%d.base.out.%s.log'%(self.ecname,self.partnum,outtypes))
        rets = ''
        rets += format_tab_line(tab,'')
        rets += format_tab_line(tab,'REM RUSTECPUB TESTCASE  from ecname %s partnum %d %s'%(self.ecname,self.partnum,outtypes))
        rets += format_tab_line(tab,'"%s" ecpubload -o "%s" "%s" %s 2>"%s" || (echo "[%d]make %s error" && exit /b 4)'%(self.rustbin,outfile,infile,appends,logfile,GL_LINES,outfile))
        return rets

    def format_code(self,tab):
        rets = ''
        rets += self._format_rust_code(tab,'compressed','explicit')
        rets += self._format_rust_code(tab,'uncompressed','explicit')
        rets += self._format_rust_code(tab,'hybrid','explicit')
        rets += self._format_rust_code(tab,'compressed',None)
        rets += self._format_rust_code(tab,'uncompressed',None)
        rets += self._format_rust_code(tab,'hybrid',None)
        return rets


def fmtrustecpubload_handler(args,parser):
    loglib.set_logging(args)
    ins = fileop.read_file(args.input)
    if args.rustbin is None or len(args.rustbin) == 0:
        raise Exception('must specified rustbin')
    if args.rustoutpath is None or len(args.rustoutpath) == 0:
        raise Exception('must specified rustoutpath')
    sarr = re.split('\n',ins)
    lidx = 0
    mexpr = re.compile('^#TESTCASE\\s+ecname\\s+([^\\s]+)\\s+partnum\\s+([0-9]+)')
    outexps = dict()
    for l in sarr:
        lidx += 1
        l = l.rstrip('\r')
        if len(l) == 0:
            continue
        m = mexpr.findall(l)
        if m is not None and len(m) > 0 and len(m[0]) > 1:
            logging.info('%s'%(l))
            partnum = fileop.parse_int(m[0][1])
            ecname = m[0][0]
            ecprivexp = RustEcpubExport(args.rustbin,args.rustoutpath,ecname,partnum)
            ntypes = '%s.%d'%(ecname,partnum)
            logging.info('ntype %s'%(ntypes))
            outexps[ntypes] = ecprivexp
    s = ''
    s += format_tab_line(0,'echo off')
    s += format_tab_line(0,'if exist "%s" ('%(args.rustoutpath))    
    s += format_tab_line(1,'echo "exist [%s]"'%(args.rustoutpath))
    s += format_tab_line(0,') else (')
    s += format_tab_line(1,'md "%s"'%(args.rustoutpath))
    s += format_tab_line(0,')')
    s += format_tab_line(0,'')

    if args.verbose > 0:
        s += format_tab_line(0,'set ECSIMPLE_LEVEL=50')
        s += format_tab_line(0,'')
    idx = 0
    for k in outexps.keys():
        idx += 1
        e = outexps[k]
        s += format_tab_line(0,'')
        s += e.format_code(0)
        if (idx % 50) == 0 and args.verbose == 0:
            if (idx % 500) == 0:
                s += format_tab_line(0,'python -c "import sys;sys.stdout.write(\'.\\n\');sys.stdout.flush();"')
            else:
                s += format_tab_line(0,'python -c "import sys;sys.stdout.write(\'.\');sys.stdout.flush();"')
    fileop.write_file(s,args.output)
    sys.exit(0)
    return



def diffpem_handler(args,parser):
    loglib.set_logging(args)
    sslpem = args.subnargs[0]
    rustpem = args.subnargs[1]
    sslb = fileop.read_file_bytes(sslpem)
    rustb = fileop.read_file_bytes(rustpem)
    sslmd5 = hashlib.md5(sslb)
    rustmd5 = hashlib.md5(rustb)
    if sslmd5.hexdigest() != rustmd5.hexdigest():
        sys.stderr.write('%s %s differd\n'%(sslpem,rustpem))
        sys.exit(1)
    sys.exit(0)
    return

class SslDiffPemLib(object):
    def __init__(self,outdir,ecname,partnum):
        self.outdir = outdir
        self.ecname = ecname
        self.partnum = partnum
        return

    def _format_diff(self,tab,cmprtype,paramenc):
        outs = ''
        types = '%s'%(cmprtype)
        if paramenc is not None and len(paramenc) > 0:
            types += '.%s'%(paramenc)
        sslfile = os.path.join(self.outdir,'ecgen.%s.%d.%s.pem'%(self.ecname,self.partnum,types))
        rustfile = os.path.join(self.outdir,'rust.ecprivload.%s.%d.base.out.%s.pem'%(self.ecname,self.partnum,types))
        pyfile = os.path.abspath(__file__)
        outs += format_tab_line(tab,'')
        outs += format_tab_line(tab,'python "%s" diffpem "%s" "%s"'%(pyfile,sslfile,rustfile))
        outs += format_tab_line(tab,'if [ $? -ne 0 ]')
        outs += format_tab_line(tab,'then')
        outs += format_tab_line(tab+1,'echo "[%d] diff %s %s error"'%(GL_LINES,sslfile,rustfile))
        outs += format_tab_line(tab+1,'exit 4')
        outs += format_tab_line(tab,'fi')
        return outs

    def format_code(self,tab):
        outs = ''
        outs += self._format_diff(tab,'compressed',None)
        outs += self._format_diff(tab,'uncompressed',None)
        outs += self._format_diff(tab,'hybrid',None)
        outs += self._format_diff(tab,'compressed','explicit')
        outs += self._format_diff(tab,'uncompressed','explicit')
        outs += self._format_diff(tab,'hybrid','explicit')
        return outs

class RustDiffPemLib(object):
    def __init__(self,outdir,ecname,partnum):
        self.outdir = outdir
        self.ecname = ecname
        self.partnum = partnum
        return

    def _format_diff(self,tab,cmprtype,paramenc):
        outs = ''
        types = '%s'%(cmprtype)
        if paramenc is not None and len(paramenc) > 0:
            types += '.%s'%(paramenc)
        sslfile = os.path.join(self.outdir,'ecgen.%s.%d.%s.pem'%(self.ecname,self.partnum,types))
        rustfile = os.path.join(self.outdir,'rust.ecprivload.%s.%d.base.out.%s.pem'%(self.ecname,self.partnum,types))
        pyfile = os.path.abspath(__file__)
        outs += format_tab_line(tab,'')
        outs += format_tab_line(tab,'python "%s" diffpem "%s" "%s" || (echo "[%d]diff %s %s error" && exit /b 4)'%(pyfile,sslfile,rustfile,GL_LINES,sslfile,rustfile))
        return outs

    def format_code(self,tab):
        outs = ''
        outs += self._format_diff(tab,'compressed',None)
        outs += self._format_diff(tab,'uncompressed',None)
        outs += self._format_diff(tab,'hybrid',None)
        outs += self._format_diff(tab,'compressed','explicit')
        outs += self._format_diff(tab,'uncompressed','explicit')
        outs += self._format_diff(tab,'hybrid','explicit')
        return outs

class RustDiffPemPubLib(object):
    def __init__(self,outdir,ecname,partnum):
        self.outdir = outdir
        self.ecname = ecname
        self.partnum = partnum
        return

    def _format_diff(self,tab,cmprtype,paramenc):
        outs = ''
        types = '%s'%(cmprtype)
        if paramenc is not None and len(paramenc) > 0:
            types += '.%s'%(paramenc)
        sslfile = os.path.join(self.outdir,'ecpub.%s.%d.%s.pem'%(self.ecname,self.partnum,types))
        rustfile = os.path.join(self.outdir,'rust.ecpubload.%s.%d.base.out.%s.pem'%(self.ecname,self.partnum,types))
        pyfile = os.path.abspath(__file__)
        outs += format_tab_line(tab,'')
        outs += format_tab_line(tab,'python "%s" diffpem "%s" "%s" || (echo "[%d]diff %s %s error" && exit /b 4)'%(pyfile,sslfile,rustfile,GL_LINES,sslfile,rustfile))
        return outs

    def format_code(self,tab):
        outs = ''
        outs += self._format_diff(tab,'compressed',None)
        outs += self._format_diff(tab,'uncompressed',None)
        outs += self._format_diff(tab,'hybrid',None)
        outs += self._format_diff(tab,'compressed','explicit')
        outs += self._format_diff(tab,'uncompressed','explicit')
        outs += self._format_diff(tab,'hybrid','explicit')
        return outs

def fmtssldiff_handler(args,parser):
    loglib.set_logging(args)
    ins = fileop.read_file(args.input)
    sarr = re.split('\n',ins)
    lidx = 0
    mexpr = re.compile('^#TESTCASE\\s+ecname\\s+([^\\s]+)\\s+partnum\\s+([0-9]+)')
    outexps = dict()
    for l in sarr:
        lidx += 1
        l = l.rstrip('\r')
        if len(l) == 0:
            continue
        m = mexpr.findall(l)
        if m is not None and len(m) > 0 and len(m[0]) > 1:
            logging.info('%s'%(l))
            partnum = fileop.parse_int(m[0][1])
            ecname = m[0][0]
            ecprivexp = SslDiffPemLib(args.outpath,ecname,partnum)
            ntypes = '%s.%d'%(ecname,partnum)
            logging.info('ntype %s'%(ntypes))
            outexps[ntypes] = ecprivexp
    s = ''
    s += format_tab_line(0,'#! /bin/bash')
    s += format_tab_line(0,'')

    for k in outexps.keys():
        e = outexps[k]
        s += format_tab_line(0,'')
        s += e.format_code(0)
    fileop.write_file(s,args.output)
    sys.exit(0)
    return

def fmtrustdiff_handler(args,parser):
    loglib.set_logging(args)
    ins = fileop.read_file(args.input)
    sarr = re.split('\n',ins)
    lidx = 0
    mexpr = re.compile('^#TESTCASE\\s+ecname\\s+([^\\s]+)\\s+partnum\\s+([0-9]+)')
    outexps = dict()
    for l in sarr:
        lidx += 1
        l = l.rstrip('\r')
        if len(l) == 0:
            continue
        m = mexpr.findall(l)
        if m is not None and len(m) > 0 and len(m[0]) > 1:
            logging.info('%s'%(l))
            partnum = fileop.parse_int(m[0][1])
            ecname = m[0][0]
            ecprivexp = RustDiffPemLib(args.rustoutpath,ecname,partnum)
            ntypes = '%s.%d'%(ecname,partnum)
            logging.info('ntype %s'%(ntypes))
            outexps[ntypes] = ecprivexp
    s = ''
    s += format_tab_line(0,'')
    s += format_tab_line(0,'echo off')

    idx = 0
    for k in outexps.keys():
        idx += 1
        e = outexps[k]
        s += format_tab_line(0,'')
        s += e.format_code(0)
        if (idx % 50) == 0 and args.verbose == 0:
            if (idx % 500) == 0:
                s += format_tab_line(0,'python -c "import sys;sys.stdout.write(\'.\\n\');sys.stdout.flush();"')
            else:
                s += format_tab_line(0,'python -c "import sys;sys.stdout.write(\'.\');sys.stdout.flush();"')
    fileop.write_file(s,args.output)
    sys.exit(0)
    return

def fmtrustdiffpub_handler(args,parser):
    loglib.set_logging(args)
    ins = fileop.read_file(args.input)
    sarr = re.split('\n',ins)
    lidx = 0
    mexpr = re.compile('^#TESTCASE\\s+ecname\\s+([^\\s]+)\\s+partnum\\s+([0-9]+)')
    outexps = dict()
    for l in sarr:
        lidx += 1
        l = l.rstrip('\r')
        if len(l) == 0:
            continue
        m = mexpr.findall(l)
        if m is not None and len(m) > 0 and len(m[0]) > 1:
            logging.info('%s'%(l))
            partnum = fileop.parse_int(m[0][1])
            ecname = m[0][0]
            ecprivexp = RustDiffPemPubLib(args.rustoutpath,ecname,partnum)
            ntypes = '%s.%d'%(ecname,partnum)
            logging.info('ntype %s'%(ntypes))
            outexps[ntypes] = ecprivexp
    s = ''
    s += format_tab_line(0,'')
    s += format_tab_line(0,'echo off')

    idx = 0
    for k in outexps.keys():
        idx += 1
        e = outexps[k]
        s += format_tab_line(0,'')
        s += e.format_code(0)
        if (idx % 50) == 0 and args.verbose == 0:
            if (idx % 500) == 0:
                s += format_tab_line(0,'python -c "import sys;sys.stdout.write(\'.\\n\');sys.stdout.flush();"')
            else:
                s += format_tab_line(0,'python -c "import sys;sys.stdout.write(\'.\');sys.stdout.flush();"')
    fileop.write_file(s,args.output)
    sys.exit(0)
    return

def fmtsslsm2gen_handler(args,parser):
    loglib.set_logging(args)
    init_ecc_params()
    ecnames = ['SM2']

    if args.outpath is None or len(args.outpath) == 0:
        raise Exception('need outpath set')

    opensslbin = args.opensslbin
    if opensslbin is None or len(opensslbin) == 0:
        opensslbin = 'openssl'
    idx = 0
    random.seed(time.time())
    s = ''
    s += format_tab_line(0,'#! /bin/bash')
    if len(args.sslsopath) > 0:
        sopaths = ''

        for f in args.sslsopath:
            if len(sopaths) > 0:
                sopaths += ':%s'%(f)
            else:
                sopaths = 'export LD_LIBRARY_PATH=%s'%(f)
        s += format_tab_line(0,'')
        s += format_tab_line(0,'%s'%(sopaths))
    s += format_tab_line(0,'')
    s += format_tab_line(0,'if [ ! -d "%s" ] '%(args.outpath))
    s += format_tab_line(0,'then')
    s += format_tab_line(1,'mkdir -p "%s"'%(args.outpath))
    s += format_tab_line(0,'fi')


    idx = 0
    while idx < args.cases:
        curidx = random.randrange(len(ecnames))
        curname = ecnames[curidx]
        nb = random.randbytes(8)
        bn = format_bn(nb)
        inst = SslSM2genInstance(opensslbin,args.outpath,curname,bn)
        s += inst.format_code(0)
        if idx > 0 and (idx % 50) == 0 and args.verbose == 0:
            s += format_tab_line(0,'')
            s += format_tab_line(0,'echo -n "."')
        idx += 1

    fileop.write_file(s,args.output)
    sys.exit(0)
    return

def fmtsm2asn1_handler(args,parser):
    loglib.set_logging(args)
    ins = fileop.read_file(args.input)
    if args.asn1parsebin is None or len(args.asn1parsebin) == 0:
        raise Exception('must specified asn1parsebin')
    if args.rustoutpath is None or len(args.rustoutpath) == 0:
        raise Exception('must specified rustoutpath')
    sarr = re.split('\n',ins)
    lidx = 0
    mexpr = re.compile('^#TESTCASE\\s+ecname\\s+([^\\s]+)\\s+partnum\\s+([0-9]+)')
    outexps = dict()
    for l in sarr:
        lidx += 1
        l = l.rstrip('\r')
        if len(l) == 0:
            continue
        m = mexpr.findall(l)
        if m is not None and len(m) > 0 and len(m[0]) > 1:
            logging.info('%s'%(l))
            partnum = fileop.parse_int(m[0][1])
            ecname = m[0][0]
            ecprivexp = Asn1SM2Instance(args.asn1parsebin,args.rustoutpath,ecname,partnum)
            ntypes = '%s.%d'%(ecname,partnum)
            logging.info('ntype %s'%(ntypes))
            outexps[ntypes] = ecprivexp
    s = ''
    s += format_tab_line(0,'echo off')
    s += format_tab_line(0,'if exist "%s" ('%(args.rustoutpath))    
    s += format_tab_line(1,'echo "exist [%s]"'%(args.rustoutpath))
    s += format_tab_line(0,') else (')
    s += format_tab_line(1,'md "%s"'%(args.rustoutpath))
    s += format_tab_line(0,')')
    s += format_tab_line(0,'')

    if args.verbose > 0:
        s += format_tab_line(0,'set ECSIMPLE_LEVEL=50')
        s += format_tab_line(0,'')

    for k in outexps.keys():
        e = outexps[k]
        s += format_tab_line(0,'')
        s += e.format_code(0)
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
        "opensslbin" : "/home/bt/source/openssl/apps/openssl",
        "sslbin" : "/mnt/zdisk/clibs/test/ssltst/ssltst",
        "rustbin" : "X:\\\\ecsimple\\\\ecsimple\\\\utest\\\\ectst\\\\target\\\\release\\\\ectst.exe",
        "asn1parsebin" : "X:\\\\ssllib-rs\\\\utest\\\\utest\\\\target\\\\release\\\\utest.exe",
        "sslsopath" : ["/mnt/zdisk/clibs/dynamiclib","/home/bt/source/openssl"],
        "outpath" : "/mnt/zdisk/ssllogs",
        "rustoutpath" : "x:\\\\ssllogs",
        "cases|C" : 100,
        "listectypes<listectypes_handler>##to list supported ectypes##" : {
            "$" : 0
        },
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
        },
        "fmtsslecgen<fmtsslecgen_handler>##ecnames ... to format ecnames##" : {
            "$" : "*"
        },
        "fmtrustecprivload<fmtrustecprivload_handler>##to load from input and give output##" : {
            "$" : 0
        },
        "fmtrustecpubload<fmtrustecpubload_handler>##to load from input and give output##" : {
            "$" : 0
        },
        "fmtrustecgen<fmtrustecgen_handler>##ecnames ... to format ecnames ecgen##" : {
            "$" : "*"
        },
        "fmtsslecprivload<fmtsslecprivload_handler>##to load from input and give output##" : {
            "$" : 0
        },
        "fmtsslecpubload<fmtsslecpubload_handler>##to load from input and give output##" : {
            "$" : 0
        },
        "diffpem<diffpem_handler>##sslpem rustpem to diff##" : {
            "$" : 2
        },
        "fmtssldiff<fmtssldiff_handler>##format ssl input as rust diff##" : {
            "$" : 0
        },
        "fmtrustdiff<fmtrustdiff_handler>##format ssl input as rust diff##"  : {
            "$" : 0
        },
        "fmtrustdiffpub<fmtrustdiffpub_handler>##format ssl input as rust diff##"  : {
            "$" : 0
        },
        "fmtsslsm2gen<fmtsslsm2gen_handler>##format ssl sm2 pem##" : {
            "$" : 0
        },
        "fmtsm2asn1<fmtsm2asn1_handler>##format dump##" : {
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