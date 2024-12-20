
import sys
import os
import logging
import hashlib
import platform
import struct
import random
import time
import math

sys.path.insert(0,os.path.join(os.path.dirname(__file__),'pythonlib'))
sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
import extargsparse
from loglib import set_logging,load_log_commandline
from strop import parse_int


def daemon_proc(stdoutfile=None,stderrfile=None,stdinfile=None,note='',redirect=True):
    logging.debug('daemon_proc will on [%s]'%(note))
    if redirect:
        sys.stdout.close()
        curfile = os.devnull
        if stdoutfile is not None:
            curfile = stdoutfile
        sys.stdout = open(curfile,'w+')
        sys.stderr.close()
        curfile = os.devnull
        if stderrfile is not None:
            curfile = stderrfile
        sys.stderr = open(curfile,'w+')
        sys.stdin.close()
        curfile = os.devnull
        if stdinfile is not None:
            curfile = stdin
        sys.stdin = open(curfile,'r')
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    elif pid < 0:
        sys.exit(3)
    os.setsid()
    logging.debug('daemon child setsid')

    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    elif pid < 0:
        sys.exit(3)
    logging.debug('daemon fork over')    
    os.umask(0) 
    return

def daemonout_handler(args,parser):
	set_logging(args)
	maxtimes = 0
	if len(args.subnargs) > 0:
		maxtimes = parse_int(args.subnargs[0])
	daemon_proc(args.stdout,args.stderr,args.stdin,'daemonout',args.redirect)
	curtime = 0
	while True:
		if maxtimes != 0 and curtime >= maxtimes:
			break
		sys.stdout.write('daemon [%d]\n'%(curtime))
		sys.stdout.flush()
		time.sleep(args.timeout)
		curtime += 1

	sys.exit(0)
	return

def main():
    commandline='''
    {
    	"stdout" : null,
    	"stderr" : null,
    	"stdin" : null,
    	"redirect" : true,
    	"timeout" : 1.0,
    	"daemonout<daemonout_handler>##to  daemon out values##" : {
    		"$" : "*"
    	}
    }
    '''
    parser = extargsparse.ExtArgsParse()
    load_log_commandline(parser)
    parser.load_command_line_string(commandline)
    parser.parse_command_line(None,parser)
    raise Exception('can not here for no command handle')
    return


if __name__ == '__main__':
    main()