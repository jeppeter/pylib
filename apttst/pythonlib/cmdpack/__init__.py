#!/usr/bin/python

import os
import sys
import subprocess
import logging
import time
import threading
import re
try:
    import Queue
except ImportError:
    import queue as Queue

__version__ = "0.4.6"
__version_info__ = ( 0, 4, 6)

class _LoggerObject(object):
    def __init__(self,logname='cmdpack'):
        self.__logger = logging.getLogger(logname)
        if len(self.__logger.handlers) == 0:
            loglvl = logging.WARN
            lvlname = '%s_LOGLEVEL'%(logname.upper())
            if lvlname in os.environ.keys():
                v = os.environ[lvlname]
                vint = 0
                try:
                    vint = int(v)
                except:
                    vint = 0
                if vint >= 4:
                    loglvl = logging.DEBUG
                elif vint >= 3:
                    loglvl = logging.INFO
            handler = logging.StreamHandler()
            fmt = "%(levelname)-8s %(message)s"
            logfmtname = '%s_LOGFMT'%(logname.upper())
            if logfmtname in os.environ.keys():
                v = os.environ[logfmtname]
                if v is not None and len(v) > 0:
                    fmt = v
            formatter = logging.Formatter(fmt)
            handler.setFormatter(formatter)
            self.__logger.addHandler(handler)
            self.__logger.setLevel(loglvl)

    def format_string(self,arr):
        s = ''
        if isinstance(arr,list):
            i = 0
            for c in arr:
                s += '[%d]%s\n'%(i,c)
                i += 1
        elif isinstance(arr,dict):
            for c in arr.keys():
                s += '%s=%s\n'%(c,arr[c])
        else:
            s += '%s'%(arr)
        return s

    def format_call_msg(self,msg,callstack):
        inmsg = ''  
        if callstack is not None:
            try:
                frame = sys._getframe(callstack)
                inmsg += '[%-10s:%-20s:%-5s] '%(frame.f_code.co_filename,frame.f_code.co_name,frame.f_lineno)
            except:
                inmsg = ''
        inmsg += msg
        return inmsg

    def info(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.info('%s'%(inmsg))

    def error(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.error('%s'%(inmsg))

    def warn(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.warn('%s'%(inmsg))

    def debug(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.debug('%s'%(inmsg))

    def fatal(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.fatal('%s'%(inmsg))



def shell_quote_string(s):
    rets = ''
    plat = sys.platform.lower()
    infoobj = _LoggerObject('cmdpack')
    idx = 0
    while idx < len(s):
        c = s[idx]
        if c == '"':
            adds = '\\"'
            infoobj.info('add (%s)'%(adds))
        elif c == '`':
            if plat == 'win32':
                adds = '`'
            else:
                adds = '\\`'
        elif c == '\\':
            if plat == 'win32':
                if (idx + 1) == len(s):
                    adds = '\\\\'
                else:
                    adds = '\\'
            else:
                adds = '\\\\'
        else:
            adds = c
        rets += adds
        idx += 1
    return rets

def format_list_to_shell_cmd(cmd):
    rets = ''
    for c in cmd:
        if len(rets) > 0:
            rets += ' '
        rets += '"%s"'%(shell_quote_string(c))
    return rets

def run_cmd_wait(cmd,mustsucc=1,noout=1,shellmode=True):
    p = _LoggerObject('cmdpack')
    p.debug('run (%s)'%(cmd))
    cmdin = cmd
    if isinstance(cmdin,list) and shellmode:
        cmdin = format_list_to_shell_cmd(cmd)
    if noout > 0:
        devnullfd = open(os.devnull,'wb')
        ret = subprocess.call(cmdin,stdout=devnullfd,stderr=devnullfd,shell=shellmode)
        devnullfd.close()
        devnullfd = None
    else:
        ret = subprocess.call(cmdin,shell=shellmode)
    if mustsucc and ret != 0:
        raise Exception('run cmd (%s) error'%(cmd))
    return ret

def run_read_cmd(cmd,stdoutfile=subprocess.PIPE,stderrfile=subprocess.PIPE,shellmode=True,copyenv=None):
    infoobj = _LoggerObject('cmdpack')
    infoobj.info('run %s stdoutfile %s stderrfile %s shellmode %s copyenv %s'%(cmd,stdoutfile,stderrfile,shellmode,copyenv))
    if copyenv is None:
        copyenv = os.environ.copy()
    cmds = cmd
    if isinstance(cmd,list) and shellmode:
        cmds = format_list_to_shell_cmd(cmd)
    infoobj.info('call (%s)'%(cmds))
    p = subprocess.Popen(cmds,stdout=stdoutfile,stderr=stderrfile,shell=shellmode,env=copyenv)
    return p

def __get_child_pids_win32(pid,recursive=True):
    infoobj = _LoggerObject('cmdpack')
    pids = []
    cmd = 'wmic process where(ParentProcessId=%d) get ProcessId'%(pid)
    infoobj.info('run (%s)'%(cmd))
    intexpr = re.compile('^([\d]+)\s*$')
    for l in run_cmd_output(cmd):
        infoobj.info('[%s]'%(l.rstrip('\r\n')))
        l = l.rstrip('\r\n')
        if intexpr.match(l):
            l = l.strip('\t ')
            l = l.rstrip('\t ')
            cpid = int(l)
            infoobj.info('[%s] cpid %d'%(l,cpid))
            if cpid not in pids:
                pids.append(cpid)
            if recursive:
                cpids = __get_child_pids_win32(cpid,recursive)
                for p in cpids:
                    if p not in pids:
                        pids.append(p)
    return pids


def __get_child_pids_cygwin(pid,recursive=True):
    pids = []
    intexpr = re.compile('([\d]+)')
    for l in run_cmd_output(['ps','-W']):
        l = l.rstrip('\r\n')
        l = l.strip('\t ')
        l = l.rstrip('\t ')
        sarr = re.split('\s+',l)
        if len(sarr) < 2:
            continue
        if not intexpr.match(sarr[0]) or not intexpr.match(sarr[1]):
            continue
        ppid = int(sarr[1])
        if ppid != pid:
            continue
        cpid = int(sarr[0])
        if cpid not in pids:
            pids.append(cpid)
        if recursive:
            cpids = __get_child_pids_cygwin(cpid,recursive)
            for p in cpids:
                if p not in pids:
                    pids.append(p)
    return pids

def __get_child_pids_darwin(pid,recursive=True):
    pids = []
    intexpr = re.compile('([\d]+)')
    for l in run_cmd_output(['ps','-A','-O','ppid']):
        l = l.rstrip('\r\n\t ')
        l = l.strip('\t ')
        sarr = re.split('\s+',l)
        if len(sarr) < 2:
            continue
        if not intexpr.match(sarr[0]) or not intexpr.match(sarr[1]):
            continue
        ppid = int(sarr[1])
        if ppid != pid:
            continue
        cpid = int(sarr[0])
        if cpid not in pids:
            pids.append(cpid)
        if recursive:
            cpids = __get_child_pids_darwin(cpid,recursive)
            for p in cpids:
                if p not in pids:
                    pids.append(p)
    return pids

def __get_child_pids_linux(pid,recursive=True):
    pids = []
    intexpr = re.compile('([\d]+)')
    for l in run_cmd_output(['ps','-e','-O','ppid']):
        l = l.rstrip('\r\n \t')
        l = l.strip('\t ')
        sarr = re.split('\s+',l)
        if len(sarr) < 2:
            continue
        if not intexpr.match(sarr[0]) or not intexpr.match(sarr[1]):
            continue
        ppid = int(sarr[1])
        if ppid != pid:
            continue
        cpid = int(sarr[0])
        if cpid not in pids:
            pids.append(cpid)
        if recursive:
            cpids = __get_child_pids_linux(cpid,recursive)
            for p in cpids:
                if p not in pids:
                    pids.append(p)
    return pids


def get_child_pids(pid,recursive=True):
    osname = sys.platform.lower()
    if osname == 'darwin':
        return __get_child_pids_darwin(pid,recursive)
    elif osname == 'cygwin':
        return __get_child_pids_cygwin(pid,recursive)
    elif osname == 'win32':
        return __get_child_pids_win32(pid,recursive)
    elif osname == 'linux2' or osname == 'linux':
        return __get_child_pids_linux(pid,recursive)
    else:
        raise Exception('not supported platform [%s]'%(osname))

class CmdObjectAttr(object):
    def __init__(self):
        pass

    def __getattr__(self,k,defval=None):
        if k not in self.__dict__.keys():
            return defval
        return self.__dict__[k]

    def __setattr__(self,k,v):
        self.__dict__[k] = v
        return



class _CmdRunObject(_LoggerObject):
    def __trans_to_string(self,s):
        if sys.version[0] == '3':
            encodetype = ['UTF-8','latin-1']
            idx=0
            while idx < len(encodetype):
                try:
                    return s.decode(encoding=encodetype[idx])
                except:
                    idx += 1
            raise Exception('not valid bytes (%s)'%(repr(s)))
        return s

    def __enqueue_output(self,out, queue,description,endq):
        for line in iter(out.readline, b''):
            transline = self.__trans_to_string(line)
            queue.put(transline)
        endq.put('done')
        endq.task_done()
        return
    def __prepare_out(self):
        if self.__p.stdout is not None:
            if self.recvq is None:
                self.recvq = Queue.Queue()
            assert(self.endout is None)
            self.endout = Queue.Queue()
            assert(self.tout is None)
            self.tout = threading.Thread(target=self.__enqueue_output,args=(self.__p.stdout,self.recvq,'stdout',self.endout))
        return

    def __prepare_err(self):
        if self.__p.stderr is not None:
            if self.recvq is None:
                self.recvq = Queue.Queue()
            assert(self.enderr is None)
            self.enderr = Queue.Queue()
            assert(self.terr is None)
            self.terr = threading.Thread(target=self.__enqueue_output,args=(self.__p.stderr,self.recvq,'stderr',self.enderr))
        return

    def __start_out(self):
        if self.tout is not None:
            self.tout.start()
            self.outended = False
            self.info('outended False')
        return

    def __start_err(self):
        if self.terr is not None:
            self.terr.start()
            self.errended = False
            self.info('errended False')
        return

    def __auto_close(self,f):
        if f is not None and hasattr(f,'close'):
            f.close()
            f = None
        return

    def __init__(self,cmd,stdoutfile,stderrfile,shellmode,copyenv,autoclosefds=[]):
        super(_CmdRunObject,self).__init__('cmdpack')
        self.__p = run_read_cmd(cmd,stdoutfile,stderrfile,shellmode,copyenv)
        self.__closefiles=autoclosefds
        self.terr = None
        self.tout = None
        self.endout = None
        self.outended = True
        self.errended = True
        self.recvq = None
        self.enderr = None
        self.endout = None
        self.__prepare_out()
        self.__prepare_err()
        self.__start_out()
        self.__start_err()
        self.__retcode = 0
        return

    def __wait_err(self):
        if self.terr is not None:
            self.terr.join()
            self.terr = None
        return

    def __wait_out(self):
        if self.tout is not None:
            self.tout.join()
            self.tout = None

    def __wait_recvq(self):
        if self.recvq is not None:
            assert(self.recvq.empty())
            # nothing to be done
            self.recvq = None
        return

    def __get_exitcode(self):
        exitcode = self.__retcode
        if self.__p is not None:
            while True:
                # wait 
                pret = self.__p.poll()
                if pret is not None:
                    exitcode = pret
                    self.info('exitcode %d'%(exitcode))
                    break
                # wait for a time
                self.info('will wait')
                time.sleep(0.1)
            if self.__p.stdout is not None:
                self.__p.stdout.close()
                self.__p.stdout = None
            if self.__p.stderr is not None:
                self.__p.stderr.close()
                self.__p.stderr = None
            self.__p = None
        for f in self.__closefiles:
            self.__auto_close(f)
        self.__closefiles = []
        self.info('exitcode (%s)'%(exitcode))
        self.__retcode = exitcode
        return exitcode

    def call_readback(self,callback,ctx):
        if self.__p is None:
            return
        while True:
            if self.errended and self.outended:
                self.info('outended errended')
                break
            try:
                rl = self.recvq.get_nowait()
                if callback is not None:
                    callback(rl,ctx)
            except Queue.Empty:
                if not self.errended:
                    try:
                        rl = self.enderr.get_nowait()
                        if rl == 'done':
                            self.info('errended')
                            self.errended = True
                            self.enderr.join()
                            self.enderr = None
                    except Queue.Empty:
                        pass
                if not self.outended :
                    try:
                        rl = self.endout.get_nowait()
                        if rl == 'done':
                            self.info('outended')
                            self.outended = True
                            self.endout.join()
                            self.endout = None
                    except Queue.Empty:
                        pass
                if not self.errended or not self.outended:
                    # sleep for a while to get 
                    time.sleep(0.1)
        return

    def __iter__(self):
        if self.__p is not None:
            while True:
                if self.errended and self.outended:
                    break
                try:
                    rl = self.recvq.get_nowait()
                    yield rl
                except Queue.Empty:
                    if not self.errended:
                        try:
                            rl = self.enderr.get_nowait()
                            if rl == 'done':
                                self.errended = True
                                self.enderr.join()
                                self.enderr = None
                        except Queue.Empty:
                            pass
                    if not self.outended :
                        try:
                            rl = self.endout.get_nowait()
                            if rl == 'done':
                                self.outended = True
                                self.endout.join()
                                self.endout = None
                        except Queue.Empty:
                            pass
                    if not self.errended or not self.outended:
                        # sleep for a while to get 
                        time.sleep(0.1)
            # all is ok ,so remove the resource
            self.__clean_resource()


    def __clean_resource(self):
        self.__wait_out()
        self.__wait_err()
        self.__wait_recvq()
        return self.__get_exitcode()

    def __send_kill(self,pid):
        osname = sys.platform.lower()
        self.info('send kill [%s]'%(pid))
        if osname == 'win32':
            cmd = 'taskkill /F /PID %d'%(pid)
            self.info('call [%s]'%(cmd))
            devnullfd=open(os.devnull,'wb')
            subprocess.call(cmd,stdout=devnullfd,stderr=devnullfd,shell=True) 
            devnullfd.close()
            devnullfd = None
        elif osname == 'cygwin' or osname == 'linux' or osname == 'linux2' or osname == 'darwin':
            cmd='kill -9 %d'%(pid)
            devnullfd=open(os.devnull,'wb')
            subprocess.call(cmd,stdout=devnullfd,stderr=devnullfd,shell=True)
            devnullfd.close()
            devnullfd = None
        else:
            raise Exception('unsupported osname [%s]'%(osname))
        return

    def __kill_proc_childs(self,pid):
        cpids = get_child_pids(pid)
        self.__send_kill(pid)
        for p in cpids:            
            self.__send_kill(p)
        return

    def __kill_proc(self,attr=None):
        maxwtime = None
        if attr is not None:
            maxwtime = attr.maxwtime
        exitcode = self.__retcode
        stime = time.time()
        if self.__p is not None:
            while True:
                if self.errended and self.outended:
                    break
                try:
                    rl = self.recvq.get_nowait()
                    self.info('rl (%s)'%(rl.rstrip('\r\n')))
                except Queue.Empty:
                    if not self.errended:
                        try:
                            rl = self.enderr.get_nowait()
                            if rl == 'done':
                                self.errended = True
                                self.enderr.join()
                                self.enderr = None
                        except Queue.Empty:
                            pass
                    if not self.outended :
                        try:
                            rl = self.endout.get_nowait()
                            if rl == 'done':
                                self.outended = True
                                self.endout.join()
                                self.endout = None
                        except Queue.Empty:
                            pass
                    if not self.errended or not self.outended:
                        # sleep for a while to get 
                        if maxwtime is not None:
                            ctime = time.time()
                            if (ctime - stime) > maxwtime:
                                self.info('[%s] kill[%s]'%(ctime,self.__p.pid))
                                self.__kill_proc_childs(self.__p.pid)
                        time.sleep(0.1)
        self.__retcode = exitcode
        return exitcode

    def __del__(self):
        # we do not clean_resource because on here we do not any more
        return

    def get_exitcode(self,attr=None):
        self.__kill_proc(attr)
        return self.__clean_resource()


def run_command_callback(cmd,callback,ctx,stdoutfile=subprocess.PIPE,stderrfile=None,shellmode=True,copyenv=None):
    cmdobj = _CmdRunObject(cmd,stdoutfile,stderrfile,shellmode,copyenv,[])
    cmdobj.call_readback(callback,ctx)
    return cmdobj.get_exitcode()


def run_cmd_output(cmd,stdout=True,stderr=False,shellmode=True,copyenv=None):
    stdouttype = type(stdout)
    autoclosefds = []
    if isinstance(stdout,bool):
        if stdout:
            stdoutfile=subprocess.PIPE
        else:
            stdoutfile=open(os.devnull,'wb')
            autoclosefds.append(stdoutfile)
    elif isinstance(stdout,str) or (sys.version[0] == '2' and isinstance(stdout,unicode)) :
        stdoutfile=open(stdout,'wb')
        autoclosefds.append(stdoutfile)
    else:
        stdoutfile=stdout

    if isinstance(stderr,bool):
        if stderr:
            stderrfile=subprocess.PIPE
        else:
            stderrfile=open(os.devnull,'wb')
            autoclosefds.append(stderrfile)
    elif isinstance(stderr,str) or (sys.version[0] == '2' and isinstance(stderr,unicode)):
        stderrfile=open(stderr,'wb')
        autoclosefds.append(stderrfile)
    else:
        stderrfile=stderr
    return _CmdRunObject(cmd,stdoutfile,stderrfile,shellmode,copyenv,autoclosefds)



