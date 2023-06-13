#! /usr/bin/env python

import extargsparse
import sys
import os
import logging
import re
import shutil
import logging.handlers
import time
import struct
import inspect
import json


sys.path.insert(0,os.path.join(os.path.abspath(os.path.dirname(__file__)),'..','python-ecdsa','src'))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import ecdsa
import fileop




def ackman(i,j):
    logging.info('i %d j %d'%(i,j))
    if i == 0:
        return j + 1
    if j == 0:
        return ackman(i-1,1)
    return ackman(i-1,ackman(i,j-1))

def ackman_handler(args,parser):
    fileop.set_logging(args)
    i = fileop.parse_int(args.subnargs[0])
    j = fileop.parse_int(args.subnargs[1])
    sys.stdout.write('ackman (%d , %d) = %d\n'%(i,j,ackman(i,j)))
    sys.exit(0)
    return

def invmod(x,n):
    """
    Extended Euclidean Algorithm. It's the 'division' in elliptic curves
    :param x: Divisor
    :param n: Mod for division
    :return: Value representing the division
    """
    if x == 0:
        return 0
    lm = 1
    hm = 0
    low = x % n
    high = n
    logging.info('lm %d hm %d low %d hight %d'%(lm,hm,low,high))
    while low > 1:
        r = high // low
        nm = hm - lm * r
        nw = high - low * r
        high = low
        hm = lm
        low = nw
        lm = nm
        logging.info('lm %d hm %d low %d hight %d'%(lm,hm,low,high))
    return lm % n

def invmod_handler(args,parser):
    fileop.set_logging(args)
    divisor = fileop.parse_int(args.subnargs[0])
    mod = fileop.parse_int(args.subnargs[1])
    sys.stdout.write('invmod(%d,%d) = %d\n'%(divisor,mod,invmod(divisor,mod)))
    sys.exit(0)
    return

def multecc_handler(args,parser):
    fileop.set_logging(args)
    curve = ecdsa.curves.curve_by_name(args.subnargs[0])
    multval = fileop.parse_int(args.subnargs[1])
    retcurve = curve.generator * multval
    sys.stdout.write('curve\n%s\n'%(curve.generator))
    sys.stdout.write('value\n0x%x\n'%(multval))
    sys.stdout.write('retcurve\n%s\n'%(retcurve))
    sys.exit(0)
    return

def addecc_handler(args,parser):
    fileop.set_logging(args)
    if len(args.subnargs) < 2:
        raise Exception('need at least eccname multval')
    curve = ecdsa.curves.curve_by_name(args.subnargs[0])
    multval = fileop.parse_int(args.subnargs[1])
    retcurve = curve.generator * multval
    for i in args.subnargs[2:]:
        curve = ecdsa.curves.curve_by_name(args.subnargs[0])
        multval = fileop.parse_int(i)
        curval = curve.generator * multval
        retcurve = retcurve + curval        
    sys.stdout.write('curve\n%s\n'%(curve.generator))
    sys.stdout.write('result\n%s\n'%(retcurve))
    sys.exit(0)
    return

def signbaseecc_handler(args,parser):
    fileop.set_logging(args)
    curve = ecdsa.curves.curve_by_name(args.subnargs[0])
    secnum = fileop.parse_int(args.subnargs[1])
    hashnumber = fileop.parse_int(args.subnargs[2])
    randkey = fileop.parse_int(args.subnargs[3])
    ecdsakey = ecdsa.SigningKey.from_secret_exponent(secnum,curve)
    sig = ecdsakey.privkey.sign(hashnumber,randkey)
    code = ecdsa.util.sigencode_der(sig.r,sig.s,None)
    if args.output is None:
        sys.stdout.write('%s\n'%(fileop.format_bytes(code,'signing code')))
    else:
        fileop.write_file_bytes(code,args.output)
    sys.exit(0)
    return

def verifybaseecc_handler(args,parser):
    fileop.set_logging(args)
    hashnumber = fileop.parse_int(args.subnargs[0])
    derpubk = fileop.read_file_bytes(args.subnargs[1])
    sigcode = fileop.read_file_bytes(args.input)
    r,s = ecdsa.util.sigdecode_der(sigcode,None)
    ecpubkey = ecdsa.VerifyingKey.from_der(derpubk)
    #ecdsakey = ecdsa.SigningKey.from_secret_exponent(secnum,curve)
    sigv = ecdsa.ecdsa.Signature(r,s)
    valid = ecpubkey.pubkey.verifies(hashnumber,sigv)
    #valid = ecdsakey.verifying_key.pubkey.verifies(hashnumber,sigv)
    sys.stdout.write('verify %s\n'%(valid))
    sys.exit(0)
    return


def modsquareroot_handler(args,parser):
    fileop.set_logging(args)
    a = fileop.parse_int(args.subnargs[0])
    prime = fileop.parse_int(args.subnargs[1])
    val = ecdsa.numbertheory.square_root_mod_prime(a,prime)
    sys.stdout.write('a [0x%x] prime [0x%x] ret [0x%x]\n'%(a,prime,val))
    sys.exit(0)
    return

def impecpubkey_handler(args,parser):
    fileop.set_logging(args)
    fname = args.subnargs[0]
    cpubk = fileop.read_file_bytes(fname)
    ecpubkey = ecdsa.VerifyingKey.from_der(cpubk)
    sys.exit(0)
    return

def expecpubkey_handler(args,parser):
    fileop.set_logging(args)
    if len(args.subnargs) < 2:
        raise Exception('need ecname secnum')
    curve = ecdsa.curves.curve_by_name(args.subnargs[0])
    secnum = fileop.parse_int(args.subnargs[1])
    ecdsakey = ecdsa.SigningKey.from_secret_exponent(secnum,curve)
    types = 'uncompressed'
    exps = None
    if len(args.subnargs) > 2:
        types = args.subnargs[2]
    if len(args.subnargs) > 3:
        exps = args.subnargs[3]
    #cpubk = ecdsakey.verifying_key.to_der('compressed',curve_parameters_encoding='explicit')
    cpubk = ecdsakey.verifying_key.to_der(types,exps)
    sys.stdout.write('%s\n'%(fileop.format_bytes(cpubk,'publickey %s %s'%(types,exps))))
    fileop.write_file_bytes(cpubk,args.output)
    sys.exit(0)
    return

def encecc_handler(args,parser):
    fileop.set_logging(args)
    ecname = args.subnargs[0]
    secnum = fileop.parse_int(args.subnargs[1])
    encnumber = fileop.parse_int(args.subnargs[2])
    randnumber = fileop.parse_int(args.subnargs[3])
    basenumber = encnumber << 32
    maxnumber = basenumber + (1 << 32)
    curnumber = basenumber
    curve = ecdsa.curves.curve_by_name(args.subnargs[0])
    p = curve.generator.curve().p()
    a = curve.generator.curve().a()
    b = curve.generator.curve().b()
    curnumber = encnumber
    ecdsakey = ecdsa.SigningKey.from_secret_exponent(secnum,curve)
    pubkey = ecdsakey.verifying_key.pubkey;

    r = randnumber * curve.generator
    cs =  randnumber * pubkey.point
    rs = r.to_affine()
    css = cs.to_affine()
    rx = rs.x()
    csx = css.x()
    sx = csx + curnumber
    #s = cs + M
    #sys.stdout.write('x 0x%x y 0x%x\n'%(curnumber,y))
    sys.stdout.write('x 0x%x\n'%(curnumber))
    #sys.stdout.write('M %s\n'%(M))
    sys.stdout.write('r %s\n'%(r))
    #sys.stdout.write('s %s\n'%(s))
    sys.stdout.write('rs %s\n'%(rs))
    sys.stdout.write('css %s\n'%(css))

    sys.stdout.write('rx 0x%x 0x%x ry 0x%x csx 0x%x mx 0x%x\n'%(rx,rs.x(),rs.y(),csx,sx))

    #alpha = (pow(rx, 3, p) + (a * rx)  + b) % p
    alpha = (rx ** 3 + a * rx + b) %p
    ry = ecdsa.numbertheory.square_root_mod_prime(alpha,p)
    cc = ry + rs.y()
    sys.stdout.write('ry 0x%x + 0x%x ?= p 0x%x 0x%x\n'%(ry,rs.y(),p,cc))
    nrp = ecdsa.ellipticcurve.Point(curve.generator.curve(),rx,ry,curve.order)
    nrj = ecdsa.ellipticcurve.PointJacobi.from_affine(nrp,False)
    orr = secnum * nrj
    opt = orr.to_affine()
    nv = sx - opt.x()
    sys.stdout.write('orr %s nv 0x%x\n'%(orr,nv))
    sys.stdout.write('rx 0x%x mx 0x%x nv 0x%x curnumber 0x%x'%(rx,sx,nv,curnumber))



    sys.exit(0)
    return

def expecprivkey_handler(args,parser):
    fileop.set_logging(args)
    ecname = args.subnargs[0]
    curve = ecdsa.curves.curve_by_name(ecname)
    types = 'uncompressed'
    asn1s = 'ssleay'
    exps = None
    if len(args.subnargs) > 1:
        secnum = fileop.parse_int(args.subnargs[1])
        privkey = ecdsa.SigningKey.from_secret_exponent(secnum,curve)
    else:
        privkey = ecdsa.SigningKey.generate(curve)

    pubkey = privkey.verifying_key
    if len(args.subnargs) > 2:
        types = args.subnargs[2]
    if len(args.subnargs) > 3:
        asn1s = args.subnargs[3]
    if len(args.subnargs) > 4:
        exps = args.subnargs[4]
    privbin = privkey.to_der(types,asn1s,exps)
    if args.ecprivkey is not None:
        fileop.write_file_bytes(privbin,args.ecprivkey)
    else:
        sys.stdout.write('%s\n'%(fileop.format_bytes(privbin,'private key %s %s %s'%(types,asn1s,exps))))

    pubbin = pubkey.to_der(types,exps)
    if args.ecpubkey is not None:
        fileop.write_file_bytes(pubbin,args.ecpubkey)
    else:
        sys.stdout.write('%s\n'%(fileop.format_bytes(pubbin,'public key %s %s'%(types,exps))))


    sys.exit(0)
    return

def ecdhgen_handler(args,parser):
    fileop.set_logging(args)
    ecname = args.subnargs[0]
    sec1 = fileop.parse_int(args.subnargs[1])
    sec2 = fileop.parse_int(args.subnargs[2])
    curve = ecdsa.curves.curve_by_name(ecname)
    priv1 = ecdsa.SigningKey.from_secret_exponent(sec1,curve)
    priv2 = ecdsa.SigningKey.from_secret_exponent(sec2,curve)
    ecdhv1 = ecdsa.ECDH(curve,priv1,priv2.verifying_key)
    ecdhv2 = ecdsa.ECDH(curve,priv2,priv1.verifying_key)
    kv1 = ecdhv1.generate_sharedsecret()
    kv2 = ecdhv2.generate_sharedsecret()
    sys.stdout.write('kv1 0x%x\n'%(kv1))
    sys.stdout.write('kv2 0x%x\n'%(kv2))
    sys.exit(0)
    return


def signdigestecc_handler(args,parser):
    fileop.set_logging(args)
    ecname = args.subnargs[0]
    secnum = fileop.parse_int(args.subnargs[1])
    binfile = fileop.read_file_bytes(args.subnargs[2])
    curve = ecdsa.curves.curve_by_name(ecname)
    privkey = ecdsa.SigningKey.from_secret_exponent(secnum,curve)
    sigv = privkey.sign(binfile)
    #sigder = sigv.to_der()
    r,s = ecdsa.util.sigdecode_string(sigv,curve.generator.order())
    sig = ecdsa.ecdsa.Signature(r,s)
    sigder = ecdsa.util.sigencode_der(sig.r,sig.s,None)
    if args.output is not None:
        fileop.write_file_bytes(sigder,args.output)
    else:
        sys.stdout.write('%s\n'%(fileop.format_bytes(sigder,'signing code')))
    if args.ecprivkey is not None:
        privder = privkey.to_der()
        fileop.write_file_bytes(privder, args.ecprivkey)
    if args.ecpubkey is not None:
        pubder = privkey.verifying_key.to_der()
        fileop.write_file_bytes(pubder,args.ecpubkey)
    sys.exit(0)
    return


def verifydigestecc_handler(args,parser):
    fileop.set_logging(args)
    if args.ecpubkey is None:
        raise Exception('no ecpubkey set')
    pubbin = fileop.read_file_bytes(args.ecpubkey)
    pubkey = ecdsa.VerifyingKey.from_der(pubbin)
    binfile = fileop.read_file_bytes(args.subnargs[0])
    sigbin = fileop.read_file_bytes(args.subnargs[1])
    r,s = ecdsa.util.sigdecode_der(sigbin,pubkey.curve.order)
    sigv = ecdsa.util.sigencode_string(r,s,pubkey.curve.order)
    retval = pubkey.verify(sigv,binfile)
    sys.stdout.write('verfiy %s\n'%(retval))
    sys.exit(0)
    return

def gcd_inner(bnum,anum):
    u = anum
    v = bnum
    x1 = 1
    y1 = 0
    x2 = 0
    y2 = 1
    while u != 0:
        logging.info('u %d v %d'%(u,v))
        q = int(v/u)
        r = v - q * u
        x = x2 - q * x1
        y = y2 - q * y1
        v = u
        u = r
        x2 = x1
        x1 = x
        y2 = y1
        y1 = y
    cnum = v
    return cnum

def gcd_handler(args,parser):
    fileop.set_logging(args)
    anum = fileop.parse_int(args.subnargs[0])
    bnum = fileop.parse_int(args.subnargs[1])
    cnum = gcd_inner(anum,bnum)
    sys.stdout.write('gcd(%d,%d) = %d\n'%(anum,bnum,cnum))
    sys.exit(0)
    return

def bingcd(a,b):
    u = a
    v = b
    e = 1
    while True:
        if (u % 2) != 0 or (v % 2 )!= 0:
            break
        if u == 0 and v == 0:
            break
        u = u >> 1
        v = v >> 1
        e <<= 1
        logging.info('u %d v %d e %d'%(u,v,e))

    while u != 0:
        if (u% 2) == 0:
            u = u >> 1
        if (v % 2) == 0:
            v = v >> 1
        if u >= v:
            u = u - v
            logging.info('u %d v %d'%(u,v))
        else:
            v = v - u
            logging.info('v %d u %d'%(v,u))
    return e * v

def bingcd_handler(args,parser):
    fileop.set_logging(args)
    a = fileop.parse_int(args.subnargs[0])
    b = fileop.parse_int(args.subnargs[1])
    c = bingcd(a,b)
    sys.stdout.write('bingcd (%d,%d) = %d\n'%(a,b,c))
    sys.exit(0)
    return

def bininv(a,p):
    u = a
    v = p
    x1 = 1
    x2 = 0
    while u != 1 and v != 1:
        while (u & 1) == 0:
            u = u >> 1
            if (x1 & 1) == 0:
                x1 = x1 >> 1
            else:
                x1 = (x1 + p) >> 1
            logging.info('u %d x1 %d'%(u,x1))
        while (v & 1) == 0:
            v = v >> 1
            if (x2 & 1) == 0:
                x2 = x2 >> 1
            else:
                x2 = (x2 + p) >> 1
            logging.info('v %d x2 %d'%(v,x2))
        if u >= v :
            u = u - v
            x1 = x1 - x2
            if x1 < 0:
                x1 += p
        else:
            v = v - u
            x2 = x2 -x1
            if x2 < 0:
                x2 += p
        logging.info('u %d v %d x1 %d x2 %d'%(u,v,x1,x2))
    if u == 1:
        return x1 % p
    return x2 % p

def bininv_handler(args,parser):
    fileop.set_logging(args)
    a = fileop.parse_int(args.subnargs[0])
    b = fileop.parse_int(args.subnargs[1])
    c = bininv(a,b)
    sys.stdout.write('bininv (%d,%d) = %d\n'%(a,b,c))
    sys.exit(0)
    return

def bit_length(val):
    retcnt = 0
    while val != 0:
        val >>= 1
        retcnt += 1
    return retcnt

def polmulmod(a,b,f,blen):
    ca = a
    cb = b
    c = 0
    if (ca & 1) != 0:
        c = b
    ca = ca >> 1
    logging.info('ca 0x%x c 0x%x'%(ca,c))
    for i in range(blen):
        cb = cb << 1
        cb = cb % f
        if (ca & 1) != 0:
            logging.info('cb 0x%x'%(cb))
            c = c + cb
        ca = ca >> 1
        logging.info('ca 0x%x cb 0x%x c 0x%x'%(ca,cb,c))
    return c



def polmulmod_handler(args,parser):
    fileop.set_logging(args)
    a = fileop.parse_int(args.subnargs[0])
    b = fileop.parse_int(args.subnargs[1])
    f = fileop.parse_int(args.subnargs[2])
    blen = fileop.parse_int(args.subnargs[3])
    c = polmulmod(a,b,f,blen)
    sys.stdout.write('polmulmod (0x%x,0x%x,0x%x,%d) = 0x%x\n'%(a,b,f,blen,c))
    sys.exit(0)
    return

def is_residu_sqrt(a,p):
    if a % p == 0:
        return True
    return pow(a, (p - 1) // 2 , p) == 1


def tonelli_shanks(a,p):
    if a % p == 0:
        return 0
    if not is_residu_sqrt(a,p):
        return None

    if (p % 4) == 3:
        logging.info('p ')
        return pow(a,(p + 1) // 4 ,p)

    Q = p - 1
    S = 0
    while Q % 2 == 0:
        Q = Q >> 1
        S += 1

    logging.info('Q %d S %d'%(Q,S))
    z = 2
    while is_residu_sqrt(z,p):
        z += 1

    logging.info('z %d'%(z))

    M = S
    c = pow(z,Q,p)
    t = pow(a,Q,p)
    R = pow(a,(Q + 1) >> 1,p)
    logging.info('M %d c %d t %d R %d'%(M,c,t,R))
    while t != 1:
        i = 0
        tempt = t
        while tempt != 1:
            i += 1
            tempt = (tempt * tempt) % p
            logging.info('tempt %d'%(tempt))
        pow2 = 2 ** (M - i - 1)
        logging.info('i %d pow2 %d'%(i,pow2))
        b = pow(c ,pow2,p)
        M = i
        c = (b * b) % p
        t = (t * b * b) % p
        R = (R * b) % p
        logging.info('b %d M %d c %d t %d R %d'%(b,M,c,t,R))
    return R

def modsqrt_handler(args,parser):
    fileop.set_logging(args)
    a = fileop.parse_int(args.subnargs[0])
    p = fileop.parse_int(args.subnargs[1])
    c = tonelli_shanks(a,p)
    if c is None:
        sys.stdout.write('tonelli_shanks(%d,%d) none\n'%(a,p))
    else:
        sys.stdout.write('tonelli_shanks(%d,%d) = %d\n'%(a,p,c))
    sys.exit(0)
    return


def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "ecprivkey" : null,
        "ecpubkey" : null,
        "ackman<ackman_handler>##i j to calculate ackman##" :  {
            "$" : 2
        },
        "invmod<invmod_handler>##divisor mod to calculate inversion modular##" : {
            "$" : 2
        },
        "multecc<multecc_handler>##name multval to calculate values##" : {
            "$" : 2
        },
        "addecc<addecc_handler>##name multval ... to calculate values##" : {
            "$" : "+"
        },
        "signbaseecc<signbaseecc_handler>##name secnum hashnumber randkey to sign to output##" : {
            "$" : 4
        },
        "verifybaseecc<verifybaseecc_handler>##hashnumber ecpubbin to verify##" : {
            "$" : 2
        },
        "modsquareroot<modsquareroot_handler>##a prime to mod prime##" : {
            "$" : 2
        },
        "expecpubkey<expecpubkey_handler>##name secname [types] [exptypes]  to export ec pubkey##" : {
            "$" : "+"
        },
        "impecpubkey<impecpubkey_handler>##keybin to import ecpubkey##" : {
            "$" : 1
        },
        "encecc<encecc_handler>##ecname secnum encnumber randnumer##" : {
            "$" : 4
        },
        "expecprivkey<expecprivkey_handler>##ecname [secnum] [types] [ssleay] [exps]##" : {
            "$" : "+"
        },
        "ecdhgen<ecdhgen_handler>##ecname secnum1 secnum2 to generate dh##" : {
            "$" : 3
        },
        "signdigestecc<signdigestecc_handler>##ecnamae secnum binfile to sign digest##" : {
            "$" : 3
        },
        "verifydigestecc<verifydigestecc_handler>##binfile signbin to verify signature##" : {
            "$" : 2
        },
        "gcd<gcd_handler>##anum bnum for gcd(anum,bnum)##" : {
            "$" : 2
        },
        "bingcd<bingcd_handler>##anum bnum for bingcd(anum,bnum)##" : {
            "$" : 2
        },
        "bininv<bininv_handler>##anum pnum for bininv(anum,pnum) p is prime##" : {
            "$" : 2
        },
        "polmulmod<polmulmod_handler>##anum bnum fnum blen for binary multiple mod##" : {
            "$" : 4
        },
        "modsqrt<modsqrt_handler>##anum pnum for tonelli_shanks algorithm##" : {
            "$" : 2
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    fileop.load_log_commandline(parser)
    parser.parse_command_line(None,parser)
    raise Exception('can not reach here')
    return

if __name__ == '__main__':
    main()    