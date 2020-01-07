#! /usr/bin/env python

import extargsparse
import sys
import os
import logging
import re
import time
import ctypes
import io


def set_logging(args):
    loglvl= logging.ERROR
    if args.verbose >= 3:
        loglvl = logging.DEBUG
    elif args.verbose >= 2:
        loglvl = logging.INFO
    if logging.root is not None and len(logging.root.handlers) > 0:
        logging.root.handlers = []
    logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
    return


def redirect_file_c(outfp,outname,tofile,mode):
    # Flush the C-level buffer stdout
    to_fp = open(tofile,mode)
    to_fd = to_fp.fileno()
    libc = ctypes.CDLL(None)
    c_outfp = ctypes.c_void_p.in_dll(libc, outname)
    original_fd = outfp.fileno()
    libc.fflush(c_outfp)
    outfp.close()
    os.close(original_fd)
    os.dup2(to_fd, original_fd)
    retfp = os.fdopen(original_fd, 'wb')
    return retfp


def redirect_stdout(tofile,mode):
    """Redirect stdout to the given file descriptor."""
    # Flush the C-level buffer stdout
    stdoutname = '%s.stdout'%(tofile)
    sys.stdout = redirect_file_c(sys.stdout, 'stdout', stdoutname,mode)
    stderrname = '%s.stderr'%(tofile)
    sys.stderr = redirect_file_c(sys.stderr, 'stderr', stderrname,mode)
    return



def runout_handler(args,parser):
    set_logging(args)
    if args.output is not None:
        redirect_stdout(args.output, 'wb')
    cnt = 0
    while True:
        time.sleep(1.0)
        sys.stdout.write('cnt[%d]\n'%(cnt))
        cnt += 1
    sys.exit(0)
    return



def main():
    commandline='''
    {
        "verbose|v" : "+",
        "output|o" : null,
        "runout<runout_handler>##   to test for call back##" : {
            "$" : 0
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    parser.parse_command_line(None,parser)
    raise Exception('can not reach here')
    return

if __name__ == '__main__':
    main()