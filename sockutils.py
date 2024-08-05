#! /usr/bin/env python

import extargsparse
import sys
import socket
import logging
import re
import os
import random
import traceback
import struct
import time

sys.path.insert(0,os.path.join(os.path.dirname(__file__)))
import fileop
import strop

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


def chatcli_handler(args,parser):
	set_logging(args)
	hoststr = args.subnargs[0]
	sarr = re.split(':',hoststr)
	if len(sarr) > 1:
		host = sarr[0]
		port = parse_int(sarr[1])
	else:
		host = sarr[0]
		port = 3391

	cli = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	cli.connect((host,port))
	try:
		while True:
			s = input('>')
			sb = s.encode('utf-8')
			cli.send(sb)
			rb = cli.recv(2048)
			r = rb.decode('utf-8')
			sys.stdout.write(r)
			sys.stdout.write('\n')
			sys.stdout.flush()
	except KeyboardInterrupt:
		pass
	cli.close()
	cli = None
	sys.exit(0)
	return

def get_rand_bytes(cnt):
    s = b''
    i = 0
    while i < cnt:
        s += struct.pack('B',random.randint(0,256) & 0xff)
        i += 1
    return s

def get_rand_max(maxnum):
    return random.randint(1,maxnum)

def asyncchatcli_handler(args,parser):
    set_logging(args)
    hoststr = args.subnargs[0]
    verbose = args.verbose
    sarr = re.split(':',hoststr)
    if len(sarr) > 1:
        host = sarr[0]
        port = parse_int(sarr[1])
    else:
        host = sarr[0]
        port = 3391
    testcnt = 10
    if len(args.subnargs) > 1:
        testcnt = int(args.subnargs[1])
    random.seed(time.time())
    cli = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    cli.connect((host,port))
    allret = True
    i = 0
    logging.info('testcnt %d'%(testcnt))
    while i < testcnt:
        try:
            maxnum = get_rand_max(50029)
            logging.info('maxnum %d'%(maxnum))
            sndb = get_rand_bytes(maxnum)
            logging.info('%s'%(strop.dump_buffer(sndb,'sndb')))
            cli.send(sndb)
            recvb = b''
            while len(recvb) < maxnum:
                nrecv = cli.recv(100000)
                recvb += nrecv
                logging.info('recvb [%d]'%(len(recvb)))
            logging.info('%s\n%s'%(strop.dump_buffer(sndb,'sndb'),strop.dump_buffer(recvb,'recvb')))
            if len(recvb) != maxnum or recvb != sndb:
                raise Exception('not valid compare')
        except:
            logging.error('%s'%(traceback.format_exc()))
            allret = False
            break
        if verbose == 0 and (i % 10) == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        if verbose == 0 and (i % 100) == 0:
            sys.stdout.write('\n')
        i += 1

    cli.close()
    cli = None

    if not allret:
        sys.exit(5)
    sys.exit(0)
    return


def chatsvr_handler(args,parser):
    set_logging(args)
    port = int(args.subnargs[0])
    host = ''
    if len(args.subnargs) > 1:
        host = args.subnargs[1]

    svr = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    svr.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
    svr.bind((host,port))
    svr.listen(5)
    logging.info('listen on %s:%d'%(host,port))
    try:
        while True:
            conn,addr = svr.accept()
            logging.info('accept %s %s'%(repr(conn),repr(addr)))
            while True:
                rd = conn.recv(2045)
                if len(rd) == 0:
                    logging.info('%s closed'%(repr(addr)))
                    conn.close()
                    conn= None
                    break
                logging.info('rd %s'%(rd))
                conn.send(rd)
    except KeyboardInterrupt:
        pass
    svr.close()
    svr = None
    sys.exit(0)
    return

def udpconn_handler(args,parser):
    set_logging(args)
    allret = True
    cli = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    carr = re.split(':',args.subnargs[0])
    if len(carr) > 1:
        destaddr = (carr[0],int(carr[1]))
    else:
        destaddr = (carr[0],0)
    for f in args.subnargs[1:]:
        c = fileop.read_file_bytes(f)
        cli.sendto(c,destaddr)
        (retdata,recvaddr) = cli.recvfrom(1555)
        sys.stdout.write('%s'%(strop.dump_buffer(retdata,'recv %s'%(repr(recvaddr)))))

    sys.exit(0)
    return

def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "chatcli<chatcli_handler>##ip:port to connect##" : {
        	"$" : "+"
        },
        "chatsvr<chatsvr_handler>##port to listen##" : {
            "$" : "+"
        },
        "udpconn<udpconn_handler>##ip:port udpfile ##": {
            "$" : "+"
        },
        "asyncchatcli<asyncchatcli_handler>##ip:port num to test##" : {
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