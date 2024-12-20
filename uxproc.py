
import sys
import os


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