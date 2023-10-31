#! /usr/bin/env python

import os
import sys
import extargsparse
import logging
import serial
import select


def pipe_file_size(infh,outfh,size=1024):
    retv = 0
    try:
        infd = infh.fd
    except:
        infd = infh.fileno()
    try:
        outfd = outfh.fd
    except:
        outfd = outfh.fileno()
    while retv < size:
        curlen = (size - retv)
        if curlen > (1024* 64):
            curlen = 1024 * 64
        rdset = [infd]
        wrset = [outfd]
        retrds,_,_ = select.select(rdset,[],[],10.0)
        if len(retrds) == 0:
            logging.info('read empty')
            continue
        logging.info('will read %d'%(curlen))
        retb = infh.read(curlen)
        _, retwrs,_ = select.select([],wrset,[],10.0)
        if len(retwrs) == 0:
            logging.info('miss write')
            continue
        wlen = outfh.write(retb)
        retv += wlen
        logging.info('total write %d'%(retv))
        if wlen != curlen:
            break
    return retv

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


def open_serial(serialname,args):
    return serial.Serial(serialname,baudrate=args.baudrate,
            bytesize=args.bytesize,parity=args.parity,stopbits=args.stopbits,
            xonxoff=args.xonxoff,
            rtscts=args.rtscts,dsrdtr=args.dsrdtr)

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

def get_file_size(fname):
    with open(fname,'r+b') as fh:
        fh.seek(0,2)
        return fh.tell()
    return 0


def readser_handler(args,parser):
    set_logging(args)
    infh = open_serial(args.input,args)
    outfh = open(args.output,'w+b')
    readsize = 1024
    if len(args.subnargs) > 0:
        readsize = parse_int(args.subnargs[0])
    retv = pipe_file_size(infh,outfh,readsize)
    infh.close()
    outfh.close()
    sys.exit(0)
    return



def writeser_handler(args,parser):
    set_logging(args)
    readsize = get_file_size(args.input)
    infh = open(args.input,'r+b')
    outfh = open_serial(args.output,args)
    if len(args.subnargs) > 0:
        readsize = parse_int(args.subnargs[0])
    retv = pipe_file_size(infh,outfh,readsize)
    infh.close()
    outfh.close()
    sys.exit(0)
    return

def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "baudrate" : 115200,
        "bytesize" : 8,
        "parity" : "N",
        "stopbits" : 1,
        "xonxoff" : false,
        "rtscts" : false,
        "dsrdtr" : false,
        "readser<readser_handler>##[size] to read size##" : {
            "$" : "?"
        },
        "writeser<writeser_handler>##[size] to write size##" : {
            "$" : "?"
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