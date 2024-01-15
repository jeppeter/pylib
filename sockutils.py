#! /usr/bin/env python

import extargsparse
import sys
import socket
import logging
import re


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