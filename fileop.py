#! /usr/bin/env


import extargsparse
import sys
import os
import logging


def set_logging(args):
    loglvl= logging.ERROR
    if args.verbose >= 3:
        loglvl = logging.DEBUG
    elif args.verbose >= 2:
        loglvl = logging.INFO
    elif args.verbose >= 1 :
        loglvl = logging.WARN
    # we delete old handlers ,and set new handler
    if logging.root is not None and logging.root.handlers is not None and len(logging.root.handlers) > 0:
        logging.root.handlers = []
    logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
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

def read_file_bytes(infile=None):
    fin = sys.stdin
    if infile is not None:
        fin = open(infile,'r+b')
    retb = b''
    while True:
        if fin != sys.stdin:
            curb = fin.read(1024 * 1024)
        else:
            curb = fin.buffer.read()
        if curb is None or len(curb) == 0:
            break
        retb += curb
    if fin != sys.stdin:
        fin.close()
    fin = None
    return retb


def write_file(s,outfile=None):
    fout = sys.stdout
    if outfile is not None:
        fout = open(outfile, 'w+b')
    outs = s
    if 'b' in fout.mode:
        outs = s.encode('utf-8')
    fout.write(outs)
    if fout != sys.stdout:
        fout.close()
    fout = None
    return 

def display_file(f,c):
    sys.stdout.write('[%s] ----------\n'%(f))
    sys.stdout.write('%s'%(c))
    sys.stdout.write('\n[%s]++++++++++++++++\n'%(f))
    return

def read_handler(args,parser):
    set_logging(args)
    if len(args.subnargs) > 0:
        for f in args.subnargs:
            s = read_file(f)
            display_file(f,s)
    else:
        s = read_file()
        display_file('sys.stdin',s)
    sys.exit(0)
    return

def display_byte_file(f,bb):
    sys.stdout.write('[%s] -------------\n'%(f))
    idx = 0
    lastidx = 0
    while idx < len(bb):
        if (idx % 16) == 0:
            if idx > 0:
                sys.stdout.write('    ')
                while lastidx < idx:
                    cb = bb[lastidx]
                    if cb >= ord(' ') and cb <= ord('~'):
                        sys.stdout.write('%c'%(cb))
                    else:
                        sys.stdout.write('.')
                    lastidx += 1
                sys.stdout.write('\n')
            sys.stdout.write('0x%08x:'%(idx))
        sys.stdout.write(' 0x%02x'%(bb[idx]))
        idx += 1

    if (idx % 16) != 0:
        while (idx % 16) != 0:
            sys.stdout.write('     ')
            idx += 1
        sys.stdout.write('    ')
        while lastidx < len(bb):
            cb = bb[lastidx]
            if cb >= ord(' ') and cb <= ord('~'):
                sys.stdout.write('%c'%(cb))
            else:
                sys.stdout.write('.')
            lastidx += 1
        sys.stdout.write('\n')
    sys.stdout.write('[%s]+++++++++++++++++\n'%(f))
    return

def readbyte_handler(args,parser):
    set_logging(args)
    if len(args.subnargs) > 0:
        for f in args.subnargs:
            bb = read_file_bytes(f)
            display_byte_file(f,bb)
    else:
        bb = read_file_bytes()
        display_byte_file('sys.stdin',bb)
    sys.exit(0)
    return

def write_handler(args,parser):
    set_logging(args)
    s = read_file(args.input)
    if len(args.subnargs):
        for f in args.subnargs:
            write_file(s,f)
    else:
        write_file(s)
    sys.exit(0)
    return

def main():
    commandline='''
    {
        "verbose|v" : "+",
        "input|i" : null,
        "read<read_handler>" : {
            "$" : "*"
        },
        "readbytes<readbyte_handler>" : {
            "$" : "*"
        },
        "write<write_handler>" : {
            "$" : "*"
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    parser.parse_command_line(None,parser)
    raise Exception('can not here for no command handle')
    return


if __name__ == '__main__':
    main()