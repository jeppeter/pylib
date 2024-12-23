
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
import select
import signal

sys.path.insert(0,os.path.join(os.path.dirname(__file__),'pythonlib'))
sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
import extargsparse
from loglib import set_logging,load_log_commandline
from strop import parse_int,dump_buffer
from jsonutil import JSONPack
GL_EVENT_FD_HAS=False
if not hasattr(os,'eventfd'):
    GL_EVENT_FD_HAS=True
if GL_EVENT_FD_HAS:
    from  eventfd import EventFD

def _write_sock(sock,jpack):
    retval = False
    try:
        sock.send(jpack.pack())
        retval = True
    except:
        logging.error('%s'%(traceback.format_exc()))
    return retval

def _write_hdl(hdl,jpack):
    retval = False
    try:
        hdl.buffer.write(jpack.pack())
        hdl.flush()
        retval = True
    except:
        logging.error('%s'%(traceback.format_exc()))
    return retval

def _write_sock_begin(sock,note):
    jpack = JSONPack()
    jpack.command = 'startsock'
    jpack.uid = 1
    jpack.pid = os.getpid()
    jpack.note = note
    jpack.sysargv = sys.argv
    return _write_sock(sock,jpack)

def _write_sock_end(hdl,note):
    jpack = JSONPack()
    jpack.command = 'endsock'
    jpack.uid = 333
    jpack.pid = os.getpid()
    jpack.note = note
    jpack.sysargv = sys.argv
    return _write_hdl(hdl,jpack)

def _open_tcp_client(svraddr,port,wr=True,note=''):
    try:
        cli = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        cli.connect((svraddr,port))
        if wr:
            retval = _write_sock_begin(cli,note)
            if not retval:
                cli.close()
                return None
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
        outf = _open_tcp_client(host,port,wr,note)
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
        #sys.stdin.close()
        #sys.stdin = _open_file(stdinfile,False,'stdin')
        #sys.stderr.close()
        logging.info(' ')
        sys.stdout.write('1nnncc\n')
        sys.stdout.flush()
        logging.info(' ')
        sys.stderr = _open_file(stderrfile,True,'stderr')
        logging.info(' ')
        sys.stdout.write('2nnncc\n')
        sys.stdout.flush()

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

def deamon_end_send(filehdl,note):
    return _write_sock_end(filehdl,note)

def daemonout_handler(args,parser):
    set_logging(args)
    maxtimes = 0
    if len(args.subnargs) > 0:
        maxtimes = parse_int(args.subnargs[0])
    if not args.foreground:
        daemon_proc(args.stdout,args.stderr,args.stdin,'daemonout',args.redirect)
    curtime = 0
    while True:
        if maxtimes != 0 and curtime >= maxtimes:
            break
        sys.stdout.write('daemon [%d]\n'%(curtime))
        sys.stdout.flush()
        sys.stderr.write('err daemon [%d]\n'%(curtime))
        sys.stderr.flush()
        time.sleep(args.timeout)
        curtime += 1
    logging.info('out log file')
    if not args.foreground:
        deamon_end_send(sys.stdout,'stdout')
        deamon_end_send(sys.stderr,'stderr')
    sys.exit(0)
    return

gl_exit = False
gl_exitevt = None

def exit_signal_handle(signum,frame):
    global gl_exit
    global gl_exitevt
    global GL_EVENT_FD_HAS
    gl_exit = True
    logging.info('notify gl_exit')
    if gl_exitevt is not None:
        if GL_EVENT_FD_HAS:
            gl_exitevt.set()
        else:
            os.eventfd_write(gl_exitevt,10)
    return

def sigint_handler(signum,frame):
    exit_signal_handle(signum,frame)
    return

def sigterm_handler(signum,frame):
    exit_signal_handle(signum,frame)
    return


def prepare_sighandler(args):
    global gl_exitevt
    global GL_EVENT_FD_HAS
    signal.signal(signal.SIGTERM,sigterm_handler)
    signal.signal(signal.SIGINT,sigint_handler)
    signal.signal(signal.SIGPIPE,signal.SIG_IGN)    
    if GL_EVENT_FD_HAS:
        gl_exitevt = EventFD()
    else:
        gl_exitevt = os.eventfd(0,os.EFD_SEMAPHORE )
    return


def logserver_handler(args,parser):
    global gl_exit
    global gl_exitevt
    set_logging(args)
    prepare_sighandler(args)
    listenport = 4395
    if len(args.subnargs) > 0:
        listenport = parse_int(args.subnargs[0])
    servsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    servsock.bind(('0.0.0.0',listenport))
    servsock.listen(5)
    logging.info('listen on %s'%(listenport))
    clisocks = []
    running = True
    while running and  not gl_exit :
        # now first to set blocks
        rds = [servsock,gl_exitevt]
        for s in clisocks:
            rds.append(s)

        # now we should test if need 
        try:
            #logging.info('rds %s'%(rds))
            canrds ,_,_ = select.select(rds,[],[],15.0)
        except:
            logging.error('%s'%(traceback.format_exc()))
            continue
        if len(canrds) > 0:
            for evt in canrds:
                if evt == servsock:
                    try:
                        cli, cliaddr = servsock.accept()
                        logging.info('accept %s'%(repr(cliaddr)))
                        clisocks.append(cli)
                    except:
                        logging.fatal('%s'%(traceback.format_exc()))
                        runnig = False
                        break
                elif evt == gl_exitevt:
                    running = False
                    break
                else:
                    searr = []
                    for s in clisocks:
                        if evt == s:
                            try:
                                b = s.recv(1024)
                                if b is not None and len(b) != 0:
                                    sys.stdout.write('%s\n'%(dump_buffer(b,'%s'%(repr(s)))))
                                else:
                                    logging.info('%s disconnect'%(repr(s)))
                                    searr.append(s)
                            except :
                                #logwarn('[%s]%s'%(repr(s.sock.getpeername()),traceback.format_exc()))
                                logging.error('[%s]%s'%(repr(s),traceback.format_exc()))
                                searr.append(s)
                            break
                    if len(searr) > 0:
                        for se in searr:
                            # we need to remove close socket
                            se.close()
                            clisocks.remove(se)
                            se = None
                    searr = []

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
        "foreground|F" : false,
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