#! /usr/bin/env python

import extargsparse
import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

import ecbase

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

def binadd_handler(args,parser):
	set_logging(args)
	ajson = read_file(args.subnargs[0])
	bjson = read_file(args.subnargs[1])
	abin = ecbase.BinaryField(ajson)
	bbin = ecbase.BinaryField(bjson)
	cbin = abin + bbin
	sys.stdout.write('%s\n'%(repr(cbin)))
	sys.exit(0)
	return

def binsub_handler(args,parser):
	set_logging(args)
	ajson = read_file(args.subnargs[0])
	bjson = read_file(args.subnargs[1])
	abin = ecbase.BinaryField(ajson)
	bbin = ecbase.BinaryField(bjson)
	cbin = abin - bbin
	sys.stdout.write('%s\n'%(repr(cbin)))
	sys.exit(0)
	return

def binmul_handler(args,parser):
	set_logging(args)
	ajson = read_file(args.subnargs[0])
	bjson = read_file(args.subnargs[1])
	abin = ecbase.BinaryField(ajson)
	bbin = ecbase.BinaryField(bjson)
	cbin = abin * bbin
	sys.stdout.write('%s\n'%(repr(cbin)))
	sys.exit(0)
	return

def main():
    commandline='''
    {
    	"binadd<binadd_handler>##ajson bjson to add value##" : {
    		"$" : 2
    	},
    	"binsub<binsub_handler>##ajson bjson to sub value##" : {
    		"$" : 2
    	},
    	"binmul<binmul_handler>##ajson bjson to multiple value##" : {
    		"$" : 2
    	}


    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    load_log_commandline(parser)
    parser.parse_command_line(None,parser)
    raise Exception('can not here for no command handle')
    return


if __name__ == '__main__':
    main()