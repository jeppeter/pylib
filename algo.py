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


def set_logging(args):
    loglvl= logging.ERROR
    if args.verbose >= 3:
        loglvl = logging.DEBUG
    elif args.verbose >= 2:
        loglvl = logging.INFO
    curlog = logging.getLogger(args.lognames)
    #sys.stderr.write('curlog [%s][%s]\n'%(args.logname,curlog))
    curlog.setLevel(loglvl)
    if len(curlog.handlers) > 0 :
        curlog.handlers = []
    formatter = logging.Formatter('%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d<%(levelname)s>\t%(message)s')
    if not args.lognostderr:
        logstderr = logging.StreamHandler()
        logstderr.setLevel(loglvl)
        logstderr.setFormatter(formatter)
        curlog.addHandler(logstderr)

    for f in args.logfiles:
        flog = logging.FileHandler(f,mode='w',delay=False)
        flog.setLevel(loglvl)
        flog.setFormatter(formatter)
        curlog.addHandler(flog)
    for f in args.logappends:       
        if args.logrotate:
            flog = logging.handlers.RotatingFileHandler(f,mode='a',maxBytes=args.logmaxbytes,backupCount=args.logbackupcnt,delay=0)
        else:
            sys.stdout.write('appends [%s] file\n'%(f))
            flog = logging.FileHandler(f,mode='a',delay=0)
        flog.setLevel(loglvl)
        flog.setFormatter(formatter)
        curlog.addHandler(flog)
    return

def load_log_commandline(parser):
    logcommand = '''
    {
        "verbose|v" : "+",
        "logname" : "root",
        "logfiles" : [],
        "logappends" : [],
        "logrotate" : true,
        "logmaxbytes" : 10000000,
        "logbackupcnt" : 2,
        "lognostderr" : false
    }
    '''
    parser.load_command_line_string(logcommand)
    return parser

def parse_int(v):
    c = v
    base = 10
    if c.startswith('0x') or c.startswith('0X') :
        base = 16
        c = c[2:]
    elif c.startswith('x') or c.startswith('X'):
        base = 16
        c = c[1:]
    return int(c,base)


def ackman(i,j):
    logging.info('i %d j %d'%(i,j))
    if i == 0:
        return j + 1
    if j == 0:
        return ackman(i-1,1)
    return ackman(i-1,ackman(i,j-1))

def ackman_handler(args,parser):
    set_logging(args)
    i = parse_int(args.subnargs[0])
    j = parse_int(args.subnargs[1])
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
    set_logging(args)
    divisor = parse_int(args.subnargs[0])
    mod = parse_int(args.subnargs[1])
    sys.stdout.write('invmod(%d,%d) = %d\n'%(divisor,mod,invmod(divisor,mod)))
    sys.exit(0)
    return

def multecc_handler(args,parser):
    set_logging(args)
    curve = ecdsa.curves.curve_by_name(args.subnargs[0])
    multval = parse_int(args.subnargs[1])
    retcurve = curve.generator * multval
    sys.stdout.write('curve\n%s\n'%(curve.generator))
    sys.stdout.write('value\n0x%x\n'%(multval))
    sys.stdout.write('retcurve\n%s\n'%(retcurve))
    sys.exit(0)
    return

def addecc_handler(args,parser):
    set_logging(args)
    if len(args.subnargs) < 2:
        raise Exception('need at least eccname multval')
    curve = ecdsa.curves.curve_by_name(args.subnargs[0])
    multval = parse_int(args.subnargs[1])
    retcurve = curve.generator * multval
    for i in args.subnargs[2:]:
        curve = ecdsa.curves.curve_by_name(args.subnargs[0])
        multval = parse_int(i)
        curval = curve.generator * multval
        retcurve = retcurve + curval
    sys.stdout.write('curve\n%s\n'%(curve.generator))
    sys.stdout.write('result\n%s\n'%(retcurve))
    sys.exit(0)
    return

def signbaseecc_handler(args,parser):
    set_logging(args)
    curve = ecdsa.curves.curve_by_name(args.subnargs[0])
    secnum = parse_int(args.subnargs[1])
    hashnumber = parse_int(args.subnargs[2])
    randkey = parse_int(args.subnargs[3])
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
    set_logging(args)
    curve = ecdsa.curves.curve_by_name(args.subnargs[0])
    secnum = parse_int(args.subnargs[1])
    hashnumber = parse_int(args.subnargs[2])
    sigcode = fileop.read_file_bytes(args.input)
    r,s = ecdsa.util.sigdecode_der(sigcode,None)
    ecdsakey = ecdsa.SigningKey.from_secret_exponent(secnum,curve)
    sigv = ecdsa.ecdsa.Signature(r,s)
    valid = ecdsakey.verifying_key.pubkey.verifies(hashnumber,sigv)
    sys.stdout.write('verify %s\n'%(valid))
    sys.exit(0)
    return


def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
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
        "verifybaseecc<verifybaseecc_handler>##name secnum hashnumber to verify##" : {
            "$" : 3
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    load_log_commandline(parser)
    parser.parse_command_line(None,parser)
    raise Exception('can not reach here')
    return

if __name__ == '__main__':
    main()    