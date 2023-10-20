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
import subprocess
import traceback


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


def read_file(infile=None):
    fin = sys.stdin
    if infile is not None:
        fin = open(infile,'r+b')
    rets = ''
    for l in fin:
        s = l
        if 'b' in fin.mode:
            if sys.version[0] == '3':
                s = l.decode('utf-8')
        rets += s

    if fin != sys.stdin:
        fin.close()
    fin = None
    return rets


def read_file_bytes(infile=None):
    fin = sys.stdin
    if infile is not None:
        fin = open(infile,'rb')
    retb = b''
    while True:
        if fin != sys.stdin:
            curb = fin.read(1024 * 1024)
        else:
            curb = fin.buffer.read()
        if curb is None or len(curb) == 0:
            break
        retb += curb
    if fin != sys.stdin:
        fin.close()
    fin = None
    return retb


def write_file(s,outfile=None):
    fout = sys.stdout
    if outfile is not None:
        fout = open(outfile, 'w+b')
    outs = s
    if 'b' in fout.mode:
        outs = s.encode('utf-8')
    fout.write(outs)
    if fout != sys.stdout:
        fout.close()
    fout = None
    return 

def write_file_bytes(sarr,outfile=None):
    fout = sys.stdout
    if outfile is not None:
        fout = open(outfile, 'wb')
    if 'b' not in fout.mode:
        fout.buffer.write(sarr)
    else:        
        fout.write(sarr)
    if fout != sys.stdout:
        fout.close()
    fout = None
    return 

def get_strval(v):
    base = 10
    iv = v
    if v.startswith('x') or v.startswith('X') :
        base= 16
        iv = v[1:]
    elif v.startswith('0x') or v.startswith('0X'):
        base = 16
        iv = v[2:]
    return int(iv,base)

def makedir_safe(d):
    if os.path.isdir(d):
        return
    os.makedirs(d)
    return

def xcopy_handler(args,parser):
    set_logging(args)
    s = read_file(args.input)
    destd = args.subnargs[0]
    srcd = os.getcwd()
    if len(args.subnargs) > 1:
        srcd = args.subnargs[1]
    sarr = re.split('\n',s)
    for l in sarr:
        l = l.rstrip('\r\n')
        srcf = os.path.join(srcd,l)
        dstf = os.path.join(destd,l)
        logging.info('[%s] => [%s]'%(srcf,dstf))
        dstd = os.path.dirname(dstf)
        makedir_safe(dstd)
        if os.path.isfile(srcf):
            shutil.copyfile(srcf,dstf)
        elif os.path.isdir(srcf):
            makedir_safe(dstf)
        else:
            logging.error('%s not valid type'%(srcf))
    sys.exit(0)
    return

def bin_to_bytes(ins):
    retb = b''
    sarr = re.split('\n',ins)
    for s in sarr:
        s = s.rstrip('\r\n')
        s = s.strip(' \t')
        ns = re.sub('^\\[0x[a-fA-F0-9]+\\][:]?\\s+','',s)
        if ns == s:
            ns = re.sub('^0x[a-fA-F0-9]+[:]?\\s+','',s)
        s = ns
        if len(s) > (16 * 5)+1:
            s = s[:(16*5)+1]
        logging.info('s [%s]'%(s))
        cursarr = re.split('\\s+',s)
        idx = 0 
        while idx < (len(cursarr) - 1):
            c = cursarr[idx]
            logging.info('c [%s]'%(c))
            if c.startswith('0x') or c.startswith('0X'):
                retb += bytes([int(c[2:],16)])
            idx += 1
    return retb

def bin_to_hex(ins):
    rets = ''
    sarr = re.split('\n',ins)
    for s in sarr:
        s = s.rstrip('\r\n')
        s = s.strip(' \t')
        ns = re.sub('^\\[0x[a-fA-F0-9]+\\][:]?\\s+','',s)
        if ns == s:
            ns = re.sub('^0x[a-fA-F0-9]+[:]?\\s+','',s)
        s = ns
        if len(s) > (16 * 5)+1:
            s = s[:(16*5)+1]
        logging.info('s [%s]'%(s))
        cursarr = re.split('\\s+',s)
        idx = 0 
        while idx < (len(cursarr) - 1):
            c = cursarr[idx]
            logging.info('c [%s]'%(c))
            rb = 0
            if c.startswith('0x') or c.startswith('0X'):
                rb = int(c[2:],16)
            rets += '%02x'%(rb)
            idx += 1
    return rets


def binhex_to_bytes(ins):
    retb = b''
    sarr = re.split('\n',ins)
    for s in sarr:
        s = s.rstrip('\r\n')
        s = s.strip(' \t')
        ns = re.sub('^\\[0x[a-fA-F0-9]+\\][:]?\\s+','',s)
        if ns == s:
            ns = re.sub('^0x[a-fA-F0-9]+[:]?\\s+','',s)
        s = ns
        if len(s) > (16 * 3)+1:
            s = s[:(16*3)+1]
        logging.info('s [%s]'%(s))
        cursarr = re.split(':',s)
        idx = 0 
        while idx < (len(cursarr)):
            c = cursarr[idx]
            if c.startswith('0x') or c.startswith('0X'):
                c = c[2:]
            retb += bytes([int(c,16)])
            idx += 1
    return retb


def bin_to_string(args,ins):
    rets = ''
    retb = bin_to_bytes(ins)
    if args.utf8mode:
        rets = retb.decode('utf-8')
    else:
        rets = retb.decode('ascii')
    return rets

def bintostr_handler(args,parser):
    set_logging(args)
    for f in args.subnargs:
        logging.info('read [%s]'%(f))
        bins = read_file(f)
        s = bin_to_string(args,bins)
        write_file(s,args.output)

    sys.exit(0)
    return


def testlog_handler(args,parser):
    set_logging(args)
    timeval = 10
    if len(args.subnargs) > 0:
        timeval = int(args.subnargs[0])
    for i in range(timeval):
        logging.info('[%d] value'%(i))
        logging.fatal('[%d] value'%(i))
        logging.error('[%d] value'%(i))
        logging.debug('[%d] value'%(i))
        if sys.version[0] == '3':
            logging.warning('[%d] value'%(i))
        else:
            logging.warn('[%d] value'%(i))
    sys.exit(0)
    return

def testout_handler(args,parser):
    set_logging(args)
    timeval = 1.0
    if len(args.subnargs) > 0:
        timeval = float(args.subnargs[0])
    for l in sys.stdin:
        sys.stdout.write('%s'%(l))
        sys.stderr.write('%s'%(l))
        time.sleep(timeval)
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(timeval)
    sys.exit(0)
    return

def utf8touni_handler(args,parser):
    set_logging(args)
    outb = []
    inb = []
    for v in args.subnargs:
        inb.append(get_strval(v))
    idx = 0
    while idx < len(inb):
        if inb[idx] <= 0x7f:
            outb.append(inb[idx])
            idx += 1
        elif ((inb[idx] & 0xe0) == 0xc0)  :
            if (idx + 1) >= len(inb):
                raise Exception('%d out'%(idx))
            if inb[idx+1] & 0xc0 != 0x80:
                raise Exception('%d not valid 0b10'%(idx))
            cv1 = inb[idx] & 0x1f
            cv2 = inb[idx+1] & 0x3f
            tv = (cv1 << 6) | cv2
            outb.append((tv >> 8) & 0xff)
            outb.append((tv & 0xff))
            idx += 2
        elif ((inb[idx] & 0xf0) == 0xe0):
            if (idx + 2)  >= len(inb):
                raise Exception('%d out'%(idx))
            if inb[idx+1] & 0xc0 != 0x80 or inb[idx+2] & 0xc0 != 0x80:
                raise Exception('%d not valid 0b10'%(idx))
            cv1 = inb[idx] & 0xf
            cv2 = inb[idx+1] & 0x3f
            cv3 = inb[idx+2] & 0x3f
            tv = (cv1 << 12) | (cv2 << 6)  | cv3 
            outb.append((tv >> 8) & 0xff)
            outb.append((tv & 0xff))
            idx += 3
        elif ((inb[idx] & 0xf1) == 0xf0):
            if (idx + 3) >= len(inb):
                raise Exception('%d out'%(idx))
            if inb[idx+1] & 0xc0 != 0x80 or inb[idx+2] & 0xc0 != 0x80 or inb[idx+3] & 0xc0 != 0x80:
                raise Exception('%d not valid 0b10'%(idx))
            cv1 = inb[idx] & 0xf
            cv2 = inb[idx+1] & 0x3f
            cv3 = inb[idx+2] & 0x3f
            cv4 = inb[idx+3] & 0x3f
            tv = (cv1 << 18) | (cv2 << 12)  | (cv3  << 6) | cv4
            outb.append((tv >> 8) & 0xff)
            outb.append((tv & 0xff))
            idx += 4
        else:
            raise Exception('%d not valid'%(idx))
    idx = 0
    sys.stdout.write('trans out:')
    while idx < len(outb):
        if (idx % 16) == 0:
            sys.stdout.write('\n')
        if (idx % 16) != 0:
            sys.stdout.write(' ')
        sys.stdout.write('0x%x'%(outb[idx]))
        idx += 1
    sys.stdout.write('\n')
    sys.exit(0)
    return


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


def getval_handler(args,parser):
    set_logging(args)
    for s in args.subnargs:
        val = parse_int(s)
        exp = (val >> 11) & 0x1f
        base = (val & 0x3ff)
        sys.stdout.write('%s base[0x%x] exp[0x%x] [%d]\n'%(s,base,exp, (base << exp)))
    sys.exit(0)
    return

def pec_check(data,initval = 0):
    retcrc = initval
    for b in data:
        for _ in range(0,8):
            if (retcrc >> 7) ^ (b & 0x1):
                retcrc = ((retcrc << 1) ^0x07) & 0xff
            else:
                retcrc = (retcrc << 1) & 0xff
            b = b >> 1
    return retcrc

def peccheck_handler(args,parser):
    set_logging(args)
    data = []
    for s in args.subnargs:
        data.append(parse_int(s))
    crc = pec_check(data)
    sys.stdout.write('%s crc 0x%x\n'%(data,crc))
    sys.exit(0)
    return

def walt_handler(args,parser):
    set_logging(args)
    for s in args.subnargs:
        val = parse_int(s)
        highval = (val >> 11) & ((1 << 5) -1)
        exp = highval & 0xf
        leftshift = ((( highval >> 4 ) & 0x1) == 0x0)
        logging.info('highval 0x%x exp 0x%x'%(highval,exp))
        base = (val & ((1 << 11) - 1))
        if leftshift :
            walt = base * exp
        else:
            walt = int(base / exp)
        sys.stdout.write('%s walt [%d] [0x%x:0x%x] leftshift [%s]\n'%(s,walt,highval, base,leftshift))
    sys.exit(0)
    return


def bin_to_rustvec(args,ins):
    rets = 'vec!['
    retb = b''
    sarr = re.split('\n',ins)
    tidx = 0
    for s in sarr:
        s = s.rstrip('\r\n')
        ns = re.sub('^\\[0x[a-fA-F0-9]+\\][:]?\\s+','',s)
        if ns == s:
            ns = re.sub('^0x[a-fA-F0-9]+[:]?\\s+','',s)
        s = ns
        logging.info('s [%s]'%(s))
        cursarr = re.split('\\s+',s)
        for c in cursarr:
            if c.startswith('0x') or c.startswith('0X'):
                if tidx > 0 :
                    rets += ','
                rets += '%s'%(c)
                tidx += 1
                if (tidx % 16) == 0 :
                    rets += '\n'
    rets += ']'
    return rets

def bintorustvec_handler(args,parser):
    set_logging(args)
    logging.info('read [%s]'%(args.input))
    bins = read_file(args.input)
    s = bin_to_rustvec(args,bins)
    write_file(s,args.output)
    sys.exit(0)
    return


def bintofile_handler(args,parser):
    set_logging(args)
    logging.info('read [%s]'%(args.input))
    bins = read_file(args.input)
    retb = bin_to_bytes(bins)
    write_file_bytes(retb,args.output)
    sys.exit(0)
    return
    
def binhextofile_handler(args,parser):
    set_logging(args)
    logging.info('read [%s]'%(args.input))
    bins = read_file(args.input)
    retb = binhex_to_bytes(bins)
    write_file_bytes(retb,args.output)
    sys.exit(0)
    return

def bintohex_handler(args,parser):
    set_logging(args)
    logging.info('read [%s]'%(args.input))
    bins = read_file(args.input)
    retb = bin_to_hex(bins)
    write_file(retb,args.output)
    sys.exit(0)
    return

def filetohex_handler(args,parser):
    set_logging(args)
    logging.info('read [%s]'%(args.input))
    bins = read_file_bytes(args.input)
    s = ''
    for v in bins:
        s += '%02x'%(v)
    write_file(s,args.output)
    sys.exit(0)
    return

class Utf8Encode(object):
    def __dict_utf8(self,val):
        newdict =dict()
        for k in val.keys():
            newk = self.__encode_utf8(k)
            newv = self.__encode_utf8(val[k])
            newdict[newk] = newv
        return newdict

    def __list_utf8(self,val):
        newlist = []
        for k in val:
            newk = self.__encode_utf8(k)
            newlist.append(newk)
        return newlist

    def __encode_utf8(self,val):
        retval = val

        if sys.version[0]=='2' and isinstance(val,unicode):
            retval = val.encode('utf8')
        elif isinstance(val,dict):
            retval = self.__dict_utf8(val)
        elif isinstance(val,list):
            retval = self.__list_utf8(val)
        return retval

    def __init__(self,val):
        self.__val = self.__encode_utf8(val)
        return

    def __str__(self):
        return self.__val

    def __repr__(self):
        return self.__val
    def get_val(self):
        return self.__val

def get_buffer_value(c):
    if sys.version[0] == '3':
        return c
    return struct.unpack('B', c)[0]


def dump_buffer(buf,fmt='',stkidx=1):
    i = 0
    lasti = 0
    s = ''
    _,fn,ln,_,_,_ = inspect.stack()[stkidx]
    s += '[%s:%d] '%(fn,ln)
    s += fmt

    while buf is not None and i < len(buf):
        if (i % 16) == 0 :
            if i > 0:
                s += ' ' * 4
                while lasti != i:
                    iv = get_buffer_value(buf[lasti])
                    if iv >= ord(' ') and iv <= ord('~'):
                        s += '%c'%(buf[lasti])
                    else:
                        s += '.'
                    lasti += 1
                s += '\n'
            elif len(fmt) > 0:
                s += '\n'
            s += '0x%08x:'%(i)
        iv = get_buffer_value(buf[i])
        s += ' 0x%02x'%(iv)
        i += 1

    if i != lasti:
        while (i % 16) != 0:
            s += ' ' * 5
            i += 1
        s += ' ' * 4
        while lasti != len(buf):
            iv = get_buffer_value(buf[lasti])
            if iv >= ord(' ') and iv <= ord('~'):
                s += '%c'%(buf[lasti])
            else:
                s += '.'
            lasti += 1
    return s

class JSONPack(object):
    def __init__(self,jdict=None):
        if jdict is not None:
            if isinstance(jdict, dict):
                self.__jdict = jdict
            elif isinstance(jdict, str):
                try:
                    self.__jdict = json.loads(jdict)
                    self.__jdict = Utf8Encode(self.__jdict).get_val()
                except:
                    raise Exception(dbgexp.I2CPROTO_EXCEPTION,'unparsable str [%s]'%(jdict))
            else:
                self.__jdict = dict()
        else:
            self.__jdict = dict()
        return

    def pack(self):
        retb = b'JSON'
        s = json.dumps(self.__jdict)
        if sys.version[0] == '3':
            sb = s.encode('utf-8')
        else:
            sb = bytes(s)
        size = len(sb) + 8
        retb += struct.pack('>I',size)
        retb += sb
        return retb

    def __str__(self):
        retb = self.pack()
        return dump_buffer(retb,'',2)

    def __repr__(self):
        retb = self.pack()
        return dump_buffer(retb,'',2)

    def __setattr__(self,k,v):
        if not k.startswith('_'):
            self.__jdict[k] = v
            return
        self.__dict__[k] = v
        return
    def __getattr__(self,k):
        if not k.startswith('_'):
            if k in self.__jdict.keys():
                return self.__jdict[k]
            return None
        return self.__dict__[k]

JSONUNPACK_STKIDX = 3

class JSONUnpack(object):
    def __parse_retb(self,retb):
        self.__djson = dict()
        if len(retb) < 8:
            raise Exception(dump_buffer(retb,'len[%d] < 8'%(len(retb)),JSONUNPACK_STKIDX))
        if retb[:4] != b'JSON':
            raise Exception(dump_buffer(retb,'not start with JSON',JSONUNPACK_STKIDX))
        size = struct.unpack('>I',retb[4:8])[0]
        if size != len(retb):
            raise Exception(dump_buffer(retb,'size [%d] != len[%d]'%(size,len(retb)),JSONUNPACK_STKIDX))
        sb = retb[8:]
        try:
            if sys.version[0] == '3':
                js = sb.decode('utf-8')
            else:
                js = str(sb)
            self.__djson = json.loads(js)
            self.__djson = Utf8Encode(self.__djson).get_val()
        except:
            raise Exception(dump_buffer(sb,'not valid string',JSONUNPACK_STKIDX))
        self.__retb = retb
        return

    def __init__(self,retb):
        self.__parse_retb(retb)
        return

    def __getattr__(self,key):
        if not key.startswith('_'):
            if key not in self.__djson.keys():
                raise Exception(dump_buffer(self.__retb,'not valid key [%s]'%(key),(JSONUNPACK_STKIDX-1)))
            return self.__djson[key]
        return self.__dict__[key]

    def pack(self):
        return self.__retb

    def keys(self):
        return self.__djson.keys()

    def __str__(self):
        return dump_buffer(self.__retb,'',2)

    def __repr__(self):
        return dump_buffer(self.__retb,'',2)

def jsonget_handler(args,parser):
    set_logging(args)
    s = read_file(args.subnargs[0])
    cfg = json.loads(s)
    jpack = JSONPack()
    for k in cfg.keys():
        jpack.__setattr__(k,cfg[k])
    retb = jpack.pack()
    junpack = JSONUnpack(retb)
    for k in args.subnargs[1:]:
        sys.stdout.write('%s=[%s]\n'%(k,junpack.__getattr__(k)))
    sys.exit(0)
    return

def hextostr_handler(args,parser):
    set_logging(args)
    ins = read_file(args.input)
    sarr = re.split('\n',ins)
    outs = '0x'
    for l in sarr:
        l = l.rstrip('\r')
        l = l.strip(' \t')
        carr = re.split('\\s+',l)
        if len(carr) > 0 :
            barr = re.split(':',carr[0])
            for k in barr:
                outs += '%s'%(k)
    write_file(outs,args.output)
    sys.exit(0)
    return

def egcd(a, b):
    logging.info('a = %d b = %d'%(a,b))
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        logging.info('g = [%d] y [%d] x [%d]'%(g,y,x))
        logging.info('a = %d b = %d'%(a,b))
        logging.info('ret (%d,%d,%d)'%(g , x - (b // a) * y , y))
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


def modinv_handler(args,parser):
    set_logging(args)
    anum = parse_int(args.subnargs[0])
    bnum = parse_int(args.subnargs[1])
    cnum = modinv(anum,bnum)
    sys.stdout.write('anum %s bnum %s a^-1 = %d [0x%x]\n'%(anum,bnum,cnum,cnum))
    sys.exit(0)
    return

def _get_primes(maxnum,primes=[]):
    retval = primes
    if maxnum <= 1:
        return retval
    if len(retval) < 1:
        retval.append(2)
    if maxnum <= 2:
        return retval

    curval = retval[-1] + 1
    while curval <= maxnum:
        isprime = True
        for k in retval:
            if (curval % k) == 0:
                isprime = False
                break
        if isprime:
            retval.append(curval)
        curval += 1
    return retval

def format_primes(primes,num=5,note=''):
    rets = '%s'%(note)
    idx = 0
    maxlen = 0
    while idx < len(primes):
        s = '%d'%(primes[idx])
        if len(s) >= maxlen:
            maxlen = len(s) + 1
        idx += 1

    idx = 0
    while idx < len(primes):
        if (idx % num) == 0:
            rets += '\n'
            rets += '    '
        rets += '%-*d'%(maxlen,primes[idx])
        idx += 1
    rets += '\n'
    return rets





def primelist_handler(args,parser):
    set_logging(args)
    maxnum = parse_int(args.subnargs[0])
    primes = _get_primes(maxnum)
    rets = format_primes(primes,5,'primes')
    sys.stdout.write('%s'%(rets))
    sys.exit(0)
    return

def ec_y_map(primenum):
    ymap = dict()
    for k in range(primenum):
        ci  = (k **2) % primenum
        if ci not in ymap.keys():
            ymap[ci] = [k]
        else:
            ymap[ci].append(k)            
    return ymap

def ec_x_map(primenum,a,b):
    xmap = dict()
    for k in range(primenum):
        ci = (k ** 3 + a * k + b) % primenum
        if ci not in xmap.keys():
            xmap[ci] = [k]
        else:
            xmap[ci].append(k)
    return xmap


def ecfind_handler(args,parser):
    set_logging(args)
    prime = parse_int(args.subnargs[0])
    ymap = ec_y_map(prime)
    xmap = dict()
    for k in range(prime):
        for i in range(prime):
            xmap[(k,i)] = ec_x_map(prime,k,i)

    for k in range(prime):
        if k in ymap.keys():
            sys.stdout.write('ymap[%d] %s\n'%(k,ymap[k]))
        else:
            sys.stdout.write('%d not in ymap\n'%(k))

    for c in range(prime):
        for k in range(prime):
            for i in range(prime):
                curxmap = xmap[(k,i)]
                for kk in curxmap.keys():
                    sys.stdout.write('%d match in [%d,%d] %s\n'%(kk,k,i, curxmap[kk]))

    for k in range(prime):
        for i in range(prime):
            curxmap = xmap[(k,i)]
            for kk in curxmap.keys():
                if kk in ymap.keys():
                    sys.stdout.write('[(%d,%d)] [%d] %s  ymap %s\n'%(k,i,kk, curxmap[kk],ymap[kk]))
                    pass
    sys.exit(0)
    return

def egcd(a,b):
    u = a
    v = b
    x1 = 1
    y1 = 0
    x2 = 0
    y2 = 1
    while u != 0:
        q = v // u
        r = v - q * u
        x = x2 - q * x1
        y = y2 - q * y1
        v = u
        u = r
        x2 = x1
        x1 = x
        y2 = y1
        y1 = y
        logging.info('u %d v %d x1 %d x2 %d y1 %d y2 %d'%(u,v,x1,x2,y1,y2))
    d = v
    x = x2
    y = y2
    return d,x,y


def egcd_handler(args,parser):
    set_logging(args)
    a = parse_int(args.subnargs[0])
    b = parse_int(args.subnargs[1])
    d,x,y = egcd(a,b)
    sys.stdout.write('d %d x %d y %d\n'%(d,x,y))
    sys.exit(0)
    return

def montgomery_value(a,p):
    n = 1
    np = p
    while np != 0:
        n += 1
        np >>= 1
    u = a
    v = p
    x1 = 1
    x2 = 0
    k = 0
    while v > 0:
        if (v % 2) == 0:
            v = v / 2
            x1 = 2 * x1
        elif (u % 2) == 0:
            u = u / 2
            x2 = 2* x2
        elif (v >= u):
            v = (v - u) / 2
            x2 = x2 + x1
            x1 = 2 * x1
        else:
            u = (u - v) / 2
            x1 = x2 + x1
            x2 = 2 * x2
        k = k + 1
    if u != 1:
        raise Exception('not invertible %d %d'%(a,p))
    if x1 > p:
        x1 = x1 - p
    return x1,k


def mont_handler(args,parser):
    set_logging(args)
    a = parse_int(args.subnargs[0])
    p = parse_int(args.subnargs[1])
    if (p % 2) == 0:
        raise Exception('p must odd')
    x,k = montgomery_value(a,p)
    sys.stdout.write('montgomery value for (%d,%d) = (%d,%d)\n'%(a,p,x,k))
    sys.exit(0)
    return

def get_naf(knum):
    vals = []
    while knum >= 1:
        if (knum % 2) == 1:
            ki = 2 - (knum % 4)
            vals.append(ki)
            knum = knum - ki
        else:
            vals.append(0)
        knum = knum // 2
    return vals


def nafk_handler(args,parser):
    set_logging(args)
    for k in args.subnargs:
        knum = parse_int(k)
        val = get_naf(knum)
        sys.stdout.write('%s => %s\n'%(k,val))
    sys.exit(0)
    return

def get_nafw(knum,w):
    modw = 2 ** w
    vals = []
    while knum >= 1:
        if (knum % 2) != 0:
            ki = knum % modw
            knum = knum - ki
            vals.append(ki)
        else:
            vals.append(0)
        knum = knum // 2
    return vals

def nafw_handler(args,parser):
    set_logging(args)
    knum = parse_int(args.subnargs[0])
    w = parse_int(args.subnargs[1])
    vals = get_nafw(knum,w)
    sys.stdout.write('%s w %s => %s\n'%(knum,w,vals))
    sys.exit(0)
    return

def filter_rust(ins):
    sarr = re.split('\n',ins)
    rets = ''
    for l in sarr:
        l = l.rstrip('\r\n')
        carr = re.split('\\s+',l,2)
        if len(carr) > 2:
            curs = carr[2]
            curs = curs.strip(' \t')
            rets += '%s\n'%(curs)
    return rets

def filter_python(ins):
    sarr = re.split('\n',ins)
    rets = ''
    for l in sarr:
        l = l.rstrip('\r\n')
        carr = re.split(r'\s+',l,2)
        if len(carr) > 2:
            curs = carr[2]
            curs = curs.strip(' \t')
            rets += '%s\n'%(curs)
    return rets


def filterlog_handler(args,parser):
    set_logging(args)
    types = 'python'
    if len(args.subnargs) > 0:
        types = args.subnargs[0]
    ins = read_file(args.input)
    if types == 'rust':
        outs = filter_rust(ins)
    elif types == 'python':
        outs = filter_python(ins)
    else:
        raise Exception('not supported [%s]'%(types))
    write_file(outs,args.output)
    sys.exit(0)

def trans_byte(numbers):
    retb = b''
    for c in numbers:
        cstr = '%x'%(c)
        if (len(cstr) % 2) != 0:
            cstr = '0%s'%(cstr)
        idx = 0
        while idx < len(cstr):
            cint = int(cstr[idx:idx+2],16)
            logging.info('cint [0x%x]'%(cint))
            retb += struct.pack('B',cint)
            idx += 2
    return retb



def randwr_handler(args,parser):
    set_logging(args)
    numbers = []
    for c in args.subnargs:
        numbers.append(parse_int(c))
    obytes = trans_byte(numbers)
    write_file_bytes(obytes,args.output)
    sys.exit(0)
    return

def get_patch_file(specfile,patchdir):
    s = read_file(specfile)
    sarr = re.split('\n',s)
    mexpr = re.compile('^Patch[0-9]+:\\s+(.*)')
    patchfiles = []
    for l in sarr:
        l = l.rstrip('\r')
        m = mexpr.findall(l)
        if m is not None and len(m) > 0:
            patchfiles.append(os.path.join(patchdir,m[0]))
    return patchfiles


def rpmpatch_handler(args,parser):
    set_logging(args)
    specfile = args.subnargs[0]
    srcdir = args.subnargs[1]
    srcdir = os.path.abspath(srcdir)
    patchdir = os.path.abspath(os.path.join(srcdir,'..'))
    patchfiles = get_patch_file(specfile,patchdir)
    retval = True
    cwddir = os.getcwd()
    for f in patchfiles:
        os.chdir(srcdir)
        try:
            logging.info('cur dir [%s]'%(os.getcwd()))
            cmds = 'git apply -p1 <%s'%(f)
            logging.info('run %s'%(cmds))
            fout= open(os.devnull,'w+')
            ret = subprocess.call(cmds,shell=True,stdout=fout)
            if ret != 0:
                logging.error('%s retval %d'%(cmds,ret))
                retval = False
        except:
            logging.error('%s'%(traceback.format_exc()))
            logging.error('run [%s] error'%(cmds))
            retval = False
        os.chdir(cwddir)
    if not retval:
        sys.exit(5)

    sys.exit(0)
    return

class SimpleFile(object):
    def __init__(self,fname):
        self.fname = fname
        self.bname = os.path.basename(fname)
        return


def TakeSimpleBase(elem):
    logging.info('%s'%(elem.bname))
    return elem.bname

def compact_simple_file(s):
    sarr = re.split('\n',s)
    rsvec = []
    for l in sarr:
        l = l.rstrip('\r')
        if len(l) == 0:
            continue
        rsvec.append(SimpleFile(l))
    return rsvec


def rpmfiles_handler(args,parser):
    set_logging(args)
    rs = read_file(args.subnargs[0])
    cs = read_file(args.subnargs[1])
    rsvec = compact_simple_file(rs)
    csvec = compact_simple_file(cs)
    rsvec.sort(key=TakeSimpleBase)
    csvec.sort(key=TakeSimpleBase)
    idx = 0
    jdx = 0
    hashvec = []
    while idx < len(rsvec) and jdx < len(csvec):
        if rsvec[idx].bname < csvec[jdx].bname:
            logging.info('idx[%d]%s < jdx[%d] %s'%(idx,rsvec[idx].bname,jdx,csvec[jdx].bname))
            idx += 1
        elif rsvec[idx].bname > csvec[jdx].bname:
            logging.info('idx[%d]%s > jdx[%d] %s'%(idx,rsvec[idx].bname,jdx,csvec[jdx].bname))
            jdx += 1
        else:
            logging.info('idx[%d]jdx[%d] %s [%s]'%(idx,jdx,csvec[jdx].bname,csvec[jdx].fname))
            hashvec.append(csvec[jdx])
            jdx += 1
            while jdx < len(csvec):
                if csvec[jdx].bname != rsvec[idx].bname:
                    break
                logging.info('idx[%d]jdx[%d] %s [%s]'%(idx,jdx,csvec[jdx].bname,csvec[jdx].fname))
                hashvec.append(csvec[jdx])
                jdx += 1
            idx += 1
    for l in hashvec:
        sys.stdout.write('%s\n'%(l.fname))
    sys.exit(0)
    return

def format_tab_line(tab,s):
    rets = ''
    for i in range(tab):
        rets += '    '
    rets += s
    rets += '\n'
    return rets

def format_one_cp_line(srcfile,dstfile,tabs=0,retline=0):
    logging.info('retline [%d]'%(retline))
    rets = format_tab_line(tabs,'if [ -f "%s" ]'%(dstfile))
    retline += 1
    rets += format_tab_line(tabs,'then')
    retline += 1
    rets += format_tab_line(tabs+1,'if [ -f "%s" ]'%(srcfile))
    retline += 1
    rets += format_tab_line(tabs+1,'then')
    retline += 1
    rets += format_tab_line(tabs+2,'cp -f "%s" "%s" && echo "[line:%d] cp [%s] => [%s] succ" || (echo "[line:%d]cp [%s] => [%s] error" >&2)'%(srcfile,dstfile,retline,srcfile,dstfile,retline,srcfile,dstfile))
    retline += 1
    rets += format_tab_line(tabs+1,'else')
    retline += 1
    rets += format_tab_line(tabs+2,'echo "[line:%d]no [%s] srcfile" >&2'%(retline,srcfile))
    retline += 1
    rets += format_tab_line(tabs+1,'fi')
    retline += 1
    rets += format_tab_line(tabs,'else')
    retline += 1
    rets += format_tab_line(tabs+1,'echo "[line:%d]no [%s] dstfile" >&2'%(retline,dstfile))
    retline += 1
    rets += format_tab_line(tabs,'fi')
    retline += 1
    return rets,retline

def append_dir_files(s,ds):
    sarr = re.split('\n',s)
    rsvec = []
    for l in sarr:
        l = l.rstrip('\r')
        if len(l) == 0:
            continue
        curf = '%s/%s'%(ds,l)
        #logging.info('cf %s ds[%s]'%(curf,ds))
        curf = os.path.abspath(curf)
        #logging.info('abs cf %s'%(curf))
        rsvec.append(SimpleFile(curf))
    return rsvec


def formatcp_handler(args,parser):
    set_logging(args)
    srcdir = os.path.abspath('.')
    if args.srcdir is not None:
        srcdir = os.path.abspath(args.srcdir)
    dstdir = '/'
    if args.dstdir is not None:
        dstdir = os.path.abspath(args.dstdir)
    srcs = read_file(args.subnargs[0])
    dsts = read_file(args.subnargs[1])
    outs = format_tab_line(0,'#! /bin/sh')
    # we set 2 because count from 1 not 0
    retline = 2
    srcfiles = append_dir_files(srcs,srcdir)
    dstfiles = append_dir_files(dsts,dstdir)
    idx = 0
    jdx = 0

    while jdx < len(dstfiles) and idx < len(srcfiles):
        if dstfiles[jdx].bname == srcfiles[idx].bname:
            outs += '\n'
            retline += 1
            s, retline= format_one_cp_line(srcfiles[idx].fname,dstfiles[jdx].fname,0,retline)
            outs += s
            jdx += 1
            while jdx < len(dstfiles):
                if dstfiles[jdx].bname != srcfiles[idx].bname:
                    break
                outs += '\n'
                retline += 1
                s , retline= format_one_cp_line(srcfiles[idx].fname,dstfiles[jdx].fname,0,retline)
                outs += s                
                jdx += 1
            idx += 1
        elif dstfiles[jdx].bname < srcfiles[idx].bname:
            logging.error('skip jdx[%d] %s (%s)'%(jdx,dstfiles[jdx].bname,dstfiles[jdx].fname))
            jdx += 1
        else:
            logging.error('skip idx[%d] %s (%s)'%(idx,srcfiles[idx].bname,srcfiles[idx].fname))
            idx += 1

    write_file(outs,args.output)
    sys.exit(0)
    return

def runtime_handler(args,parser):
    set_logging(args)
    stime = time.time()
    retval = subprocess.call(args.subnargs,shell=args.shellmode)
    etime = time.time()
    sys.stdout.write('run %s retval %d time %s\n'%(args.subnargs,retval,etime - stime))
    sys.exit(0)
    return

def rustdoc_handler(args,parser):
    set_logging(args)
    outs = format_tab_line(args.tab,'//!    ```%s'%(args.mdnote))
    for f in args.subnargs:
        ins = read_file(f)
        sarr = re.split('\n',ins)
        for l in sarr:
            l = l.rstrip('\r')
            outs += format_tab_line(args.tab,'//!    %s'%(l))
    outs += format_tab_line(args.tab,'//!    ```')
    write_file(outs,args.output)
    sys.exit(0)
    return

def mdrustdoc_handler(args,parser):
    set_logging(args)
    outs = format_tab_line(args.tab,'```%s'%(args.mdnote))
    for f in args.subnargs:
        ins = read_file(f)
        sarr = re.split('\n',ins)
        for l in sarr:
            l = l.rstrip('\r')
            outs += format_tab_line(args.tab,'%s'%(l))
    outs += format_tab_line(args.tab,'```')
    write_file(outs,args.output)
    sys.exit(0)
    return


def main():
    commandline='''
    {
        "input|i" : null,
        "utf8mode|U" : false,
        "output|o" : null,
        "srcdir|s" : null,
        "dstdir|d" : null,
        "shellmode|S" : false,
        "mdnote" : "rust",
        "tab|T" : 0,
        "xcopy<xcopy_handler>## dstd [srcd] to copy file from input from srcd to dstd srcd default .##" : {
            "$" : "+"
        },
        "bintostr<bintostr_handler>## inputfile to dump bin to string##" : {
            "$" : "+"
        },
        "testlog<testlog_handler>## time ##" : {
            "$" : "?"
        },
        "testout<testout_handler>##timesleep to sleep for a single line from read stdin default 1.0##" : {
            "$" : "?"
        },
        "utf8touni<utf8touni_handler>## bytes... to change utf8 coding to unicode ##" : {
            "$" : "+"
        },
        "getval<getval_handler>##value ... to change value##" : {
            "$" : "+"
        },
        "peccheck<peccheck_handler>## byte ... to check##" : {
            "$" : "+"
        },
        "walt<walt_handler>## value ... to handle ##" : {
            "$" : "+"
        },
        "bintorustvec<bintorustvec_handler>##to change buffer out to rust vec##" : {
            "$" : 0
        },
        "bintofile<bintofile_handler>##to change buffer read bin from input speciefied by output##" : {
            "$" : 0
        },
        "binhextofile<binhextofile_handler>##to change buffer read bin from input to output##" : {
            "$" : 0
        },
        "bintohex<bintohex_handler>##to change input buffer to hex string to output##" : {
            "$" : 0
        },
        "filetohex<filetohex_handler>##to change file byte into hexstr##" : {
            "$" : 0
        },
        "jsonget<jsonget_handler>##jsonfile keywords ... to get keyword##" : {
            "$" : "+"
        },
        "hextostr<hextostr_handler>###to change bignum to hex#" : {
            "$" : 0
        },
        "modinv<modinv_handler>##anum bnum to get modinversion##" : {
            "$" : 2
        },
        "primelist<primelist_handler>##maxnum to list##" : {
            "$" : 1
        },
        "ecfind<ecfind_handler>##pnum prime number to get##" : {
            "$" : 1
        },
        "egcd<egcd_handler>##a b a < b to Extend Euclidean algorithm##" : {
            "$" : 2
        },
        "mont<mont_handler>##a p to make montgomery algorithm in Guide to Elliptic Curve Cryptography (2004) - Hankerson, Menezes, Vanstone Page 63##" : {
            "$" : 2
        },
        "nafk<nafk_handler>##knum ... to debug naf in Guide to Elliptic Curve Cryptography Page 119##" : {
            "$" : "+"
        },
        "nafw<nafw_handler>##knum w to debug nafw in Guide to Elliptic Curve Cryptography Page 121##" : {
            "$" : 2
        },
        "filterlog<filterlog_handler>##[rust|python] to filter file for rust or python log##" : {
            "$" : "?"
        },
        "randwr<randwr_handler>##number ... to write for output##" : {
            "$" : "*"
        },
        "rpmpatch<rpmpatch_handler>##specfile sourcedir to patch##" : {
            "$" : 2
        },
        "rpmfiles<rpmfiles_handler>##rpmfiles listfiles to match rpm files##" : {
            "$" : 2
        },
        "formatcp<formatcp_handler>##srcfilelist dstfilelist to copy##" : {
            "$" : 2
        },
        "runtime<runtime_handler>##cmds ... to run time##" : {
            "$" : "+"
        },
        "rustdoc<rustdoc_handler>##infile ... to make rust doc examples  ##" : {
            "$" : "+"
        },
        "mdrustdoc<mdrustdoc_handler>##infile ... to make rust doc in markdown##" : {
            "$" : "+"
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