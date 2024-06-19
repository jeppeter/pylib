#! /usr/bin/env python


import sys
import os
import re
import struct
import logging

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import logop

import extargsparse


def sort_and_uniq(sarr):
    retsarr = []
    idx = 0
    sarr.sort()
    if len(sarr) > 0:
        retsarr.append(sarr[0])

    idx = 1
    while idx < len(sarr):
        if retsarr[-1] != sarr[idx]:
            retsarr.append(sarr[idx])
        idx += 1
    return retsarr


def parse_input_sarr(ins):
    sarr = re.split('\n',ins)
    retval = []
    for l in sarr:
        l = l.rstrip('\r')
        if l.startswith('#') or len(l) == 0:
            continue
        carr = re.split('\\s+', l)
        for nk in carr:
            if len(nk) > 0:
                retval.append(nk)
    return retval

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


class Maxsize:
    def __init__(self):
        self.maxsize = 0
        return

    def set_max_length(self,s):
        if len(s) > self.maxsize:
            self.maxsize = len(s)
        return


def format_output_sarr(sarr,maxnum):
    msize = Maxsize()
    for l in nlist:
        msize.set_max_length(l)

    indx = 0
    outs = ''
    for l in nlist:
        indx += 1
        if (indx % maxnum) == 1:
            outs += '%-*s'%(msize.maxsize,l)
        else:
            outs += ' %-*s'%(msize.maxsize,l)
        if (indx % maxnum) == 0:
            outs += '\n'
    return outs

def rand_bytes(numbyte):
    cb = os.urandom(numbyte)
    rets = ''
    indx = 0
    while indx < len(cb):
        cn = struct.unpack('B',cb[indx])[0]
        rets += '%02x'%(cn)
        indx += 2
    return rets

def rb_handler(args,parser):
    logop.set_logging(args)
    val = parse_int(args.subnargs[0])
    vs = rand_bytes(val)
    sys.stdout.write('%s [%s]\n'%(args.subnargs[0],vs))
    sys.exit(0)
    return


def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "rb<rb_handler>##to give rand bytes##" : {
            "$" : 1
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    logop.load_log_commandline(parser)
    parser.parse_command_line(None,parser)
    raise Exception('can not reach here')
    return

if __name__ == '__main__':
    main()
