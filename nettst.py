#! /usr/bin/env python
import extargsparse
import os
import sys
import socket
import threading
import re
import logging
import time
import traceback
import math
import select

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
from loglib import set_logging,load_log_commandline
import netop
import fileop
import strop


def downurl_handler(args,parser):
	set_logging(args)
	url = args.subnargs[0]
	ofile = None
	if len(args.subnargs) > 1:
		ofile = args.subnargs[1]

	down = netop.DownloadUrl(url,ofile)
	retval = down.download()
	if not retval:
		sys.exit(1)
	sys.exit(0)
	return

ECHO_SERVER_DEF_BINDSTR = '127.0.0.1:9939'



class EchoSession(threading.Thread):
    def __init__(self,sock):
        self.sock = sock
        threading.Thread.__init__(self)
        return

    def run(self):
        self.sock.setblocking(False)
        while True:
            try:
                logging.info('will recv')
                rds , _,_ = select.select([self.sock],[],[],3.0)
                if len(rds) > 0:
                    rdata = self.sock.recv(2048)
                    if rdata is None or len(rdata) == 0:
                        self.sock.close()
                        return
                    logging.info('%s'%(strop.dump_buffer(rdata,'server read data %d'%(len(rdata)))))
                    self.sock.sendall(rdata)
            except:
                logging.error('%s'%(traceback.format_exc()))
                self.sock.close()
                return


class EchoServer(object):
    def __init__(self,bindstr):
        self.bindstr = bindstr
        self.sock = None
        self.children = []
        return

    def start(self):
        sarr = re.split(':',self.bindstr)
        if len(sarr) < 2:
            raise Exception('bindstr [%s] not valid'%(self.bindstr))
        svraddr = sarr[0]        
        svrport =int(sarr[1])
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind((svraddr,svrport))
        self.sock.listen(5)
        logging.info('bind on %s'%(self.bindstr))
        self.sock.settimeout(1.0)
        while True:
            try:
                cont = True
                while cont:
                    cont = False
                    idx = 0
                    while idx < len(self.children):
                        if not self.children[idx].is_alive():
                            cont = True
                            self.children[idx].join()
                            nchld = []
                            jdx = 0
                            while jdx < len(self.children):
                                if jdx != idx:
                                    nchld.append(self.children[jdx])
                                jdx += 1
                            self.children = nchld
                            break
                        idx += 1
                sesssock ,addr = self.sock.accept()
                th1 = EchoSession(sesssock)
                th1.start()
                self.children.append(th1)
            except TimeoutError:
                # nothing to handle
                pass
            except KeyboardInterrupt:
                break
            except:
                logging.error('%s'%(traceback.format_exc()))
        return



def echosvr_handler(args,parser):
    set_logging(args)
    bindstr = ECHO_SERVER_DEF_BINDSTR
    if len(args.subnargs) > 0:
        bindstr = args.subnargs[0]
    echosvr = EchoServer(bindstr)
    echosvr.start()    
    sys.exit(0)


class SendFile(object):
    def __init__(self,remotestr,sendfile):
        self.remotestr = remotestr
        self.sendfile = sendfile
        return

    def start(self,timeout=0.0):
        s = fileop.read_file(self.sendfile)
        sarr = re.split('\n',s)
        rarr = re.split(':',self.remotestr)
        if len(rarr) < 2:
            raise Exception('%s not valid remote addr')
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        raddr = rarr[0]
        rport = int(rarr[1])
        self.sock.connect((raddr,rport))        
        for l in sarr:
            ws = '%s\n'%(l)
            wdata = ws.encode('utf-8')
            logging.info('%s'%(strop.dump_buffer(wdata,'send buffer')))
            self.sock.sendall(wdata)
            logging.info('cli read')
            rdata = self.sock.recv(2048)
            logging.info('%s'%(strop.dump_buffer(rdata,'read data %d'%(len(rdata)))))
            if math.fabs(timeout) > 0.001:
                time.sleep(timeout)


def sendfile_handler(args,parser):
    set_logging(args)
    remotestr = args.subnargs[0]
    sendfile = args.subnargs[1]
    sendcli = SendFile(remotestr,sendfile)
    sendcli.start(args.timeout)
    sys.exit(0)
    return

def main():
    commandline_fmt='''
    {
        "input|i" : null,
        "output|o" : null,
        "timeout" : 0.0,
        "downurl<downurl_handler>##url [outputfile] ... to download for output##" : {
        	"$" : "+"
        },
        "echosvr<echosvr_handler>##[binstr] to listen on bindstr default %s##" : {
            "$" : "?"
        },
        "sendfile<sendfile_handler>##connstr file to send file to remote##" :  {
            "$" : 2
        }
    }
    '''
    commandline = commandline_fmt%(ECHO_SERVER_DEF_BINDSTR)
    parser = extargsparse.ExtArgsParse()
    load_log_commandline(parser)
    parser.load_command_line_string(commandline)
    parser.parse_command_line(None,parser)
    raise Exception('can not here for no command handle')
    return


if __name__ == '__main__':
    main()
