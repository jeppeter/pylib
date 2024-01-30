#! /usr/bin/env python

import extargsparse
import sys
import logging
import re
import os
import json
import struct
import inspect
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__)))
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
                    raise Exception('unparsable str [%s]'%(jdict))
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
            raise Except(dump_buffer(retb,'len[%d] < 8'%(len(retb)),JSONUNPACK_STKIDX))
        if retb[:4] != b'JSON':
            raise Except(dump_buffer(retb,'not start with JSON',JSONUNPACK_STKIDX))
        size = struct.unpack('>I',retb[4:8])[0]
        if size != len(retb):
            raise Except(dump_buffer(retb,'size [%d] != len[%d]'%(size,len(retb)),JSONUNPACK_STKIDX))
        sb = retb[8:]
        try:
            if sys.version[0] == '3':
                js = sb.decode('utf-8')
            else:
                js = str(sb)
            self.__djson = json.loads(js)
            self.__djson = Utf8Encode(self.__djson).get_val()
        except:
            raise Exception(dump_buffer(sb,'not valid string\n%s'%(traceback.format_exc()),JSONUNPACK_STKIDX))
        self.__retb = retb
        return

    def __init__(self,retb):
        self.__parse_retb(retb)
        return

    def __getattr__(self,key):
        if not key.startswith('_'):
            if key not in self.__djson.keys():
                raise dbgexp.DebugException(dbgexp.I2CPROTO_EXCEPTION,dump_buffer(self.__retb,'not valid key [%s]'%(key),(JSONUNPACK_STKIDX-1)))
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

def jsonp_handler(args,parser):
	set_logging(args)
	for f in args.subnargs:
		s = fileop.read_file(f)
		sdict = json.loads(s)
		jpack = JSONPack(sdict)
		bd = jpack.pack()
		sys.stdout.write('%s\n'%(dump_buffer(bd)))

	sys.exit(0)
	return

def jsonunp_handler(args,parser):
	set_logging(args)
	for f in args.subnargs:
		b = fileop.read_file_bytes(f)
		junpack = JSONUnpack(b)
		sys.stdout.write('%s'%(repr(junpack)))
	sys.exit(0)
	return


def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "jsonp<jsonp_handler>##files ... ##" : {
        	"$" : "+"
        },
        "jsonunp<jsonunp_handler>##files ...##" : {
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