
import sys
import os
import logging
import hashlib
import platform
import struct
import random
import time
import math
import re
import traceback
import socket

sys.path.insert(0,os.path.join(os.path.dirname(__file__),'pythonlib'))
sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
import extargsparse
from loglib import set_logging,load_log_commandline
from strop import parse_int

def _open_tcp_client(svraddr,port,wr=True):
	try:
		cli = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		cli.connect((svraddr,port))
		if wr:
			return cli.makefile('w')
		else:
			return cli.makefile('r')
	except:
		logging.error('%s'%(traceback.format_exc()))
		return None


def _default_file(wr=True):
	if wr:
		return open(os.devnull,'w+')
	else:
		return open(os.devnull,'r')

def _open_file(fname,wr=True,note=''):
	if fname is None:
		logging.info('open %s default'%(note))
		return _default_file(wr)
	if fname.startswith('tcp:'):
		sarr = re.split(':',fname)
		if len(sarr) >= 3:
			host = sarr[1]
			port = parse_int(sarr[2])
		else:
			host = '127.0.0.1'
			port = parse_int(sarr[1])
		outf = _open_tcp_client(host,port,wr)
		if outf is None:
			outf = _default_file(wr)
		logging.info('open %s for %s'%(fname,note))
	else:
		try:
			if wr:
				outf = open(fname,'w+')
			else:
				outf = open(fname,'r')
			logging.info('open %s for %s'%(fname,note))
		except:
			logging.error('can not open [%s]'%(fname))
			return _default_file(wr)
	return outf

def daemon_proc(stdoutfile=None,stderrfile=None,stdinfile=None,note='',redirect=True):
    logging.debug('daemon_proc will on [%s]'%(note))
    pid = os.fork()
    logging.info('pid %d'%(pid))
    if pid > 0:
        sys.exit(0)
    elif pid < 0:
        sys.exit(3)

    if redirect:
        sys.stdout.close()
        sys.stdout = _open_file(stdoutfile,True,'stdout')
        logging.info(' ')
        sys.stdin.close()
        sys.stdin = _open_file(stdinfile,False,'stdin')
        sys.stderr.close()
        logging.info(' ')
        sys.stderr = _open_file(stderrfile,True,'stderr')
        logging.info(' ')

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

def server_handler(args,parser):
	set_logging(args)
	listenport = 4395
	if len(args.subnargs) > 0:
		listenport = parse_int(args.subnargs[0])
	sever = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	server.bind(('0.0.0.0',listenport))
	server.listen(5)
	clisocks = []
    running = True
    while running:
        # now first to set blocks
        rds = [self.sock,self.exitevt]
        for s in self.clisocks:
            rds.append(s.sock)
        rds.append(self.i2ccmdnotievt)
        rds.append(self.outevt)
        # now we should test if need 
        wrs = []
        for s in self.clisocks:
            if s.need_write():
                wrs.append(s.sock)
        try:
            canrds ,canwrs,_ = select.select(rds,wrs,[],15.0)
        except:
            logwarn('%s'%(traceback.format_exc()))
            continue
        if len(canrds) > 0:
            for evt in canrds:
                if evt == self.sock:
                    try:
                        clisock, cliaddr = self.sock.accept()
                        logging.info('come %s'%(repr(cliaddr)))
                        s = I2CClientEx(clisock,self.inq,self.inevt,self.timeout)
                        self.clisocks.append(s)
                    except:
                        logging.fatal('%s'%(traceback.format_exc()))
                        runnig = False
                        break
                elif evt == self.i2ccmdnotievt:
                    self.i2ccmdnotievt.clear()
                    running = False
                    break
                elif evt == self.outevt:
                    self.outevt.clear()
                    # it means we have some thing to send
                    try:
                        while True:
                            pkg = self.outq.get_nowait()
                            finded = 0
                            for s in self.clisocks:
                                if id(s.sock) == pkg[0]:
                                    s.put(pkg)
                                    finded = 1
                                    break
                            if finded < 0:
                                logwarn('not found [%s]'%(pkg[0]))                         
                    except Queue.Empty:
                        logwarn('outq empty')
                    except:
                        logging.fatal('%s'%(traceback.format_exc()))
                        running = False
                elif evt == self.exitevt:
                    self.exitevt.clear()
                    running = False                     
                else:
                    searr = []
                    for s in self.clisocks:
                        if evt == s.sock:
                            try:
                                s.read()
                            except dbgexp.DebugException as err:
                                #logwarn('[%s]%s'%(repr(s.sock.getpeername()),traceback.format_exc()))
                                logwarn('[%s]%s'%(repr(s.sock),traceback.format_exc()))
                                searr.append(s)
                            except:
                                logging.fatal('%s'%(traceback.format_exc()))
                                running = False
                            break
                    if len(searr) > 0:
                        for se in searr:
                            # we need to remove close socket
                            logging.info('remove [%s]'%(se.sock))
                            se.close()
                            self.clisocks.remove(se)
                            se = None
                    searr = []
        if len(canwrs) > 0:
            for evt in canwrs:
                searr  = []
                for s in self.clisocks:
                        if s.sock == evt:
                            try:
                                s.write()
                            except dbgexp.DebugException as err:
                                logwarn('%s'%(err))
                                searr.append(s)
                            except:
                                logging.error('%s'%(traceback.format_exc()))
                                running = False
                            break
                    if len(searr) > 0:
                        for se in searr:
                            logging.info('remove [%s]'%(se))
                            se.close()
                            self.clisocks.remove(se)
                            se = None
                    searr = []
        return		

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
    	},
    	"logserver<logserver_handler>##[port]to log to listen on port default 4395 ##" : {
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