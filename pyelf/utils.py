#! /usr/bin/env python

import logging
import extargsparse
import elftools
import re
import sys


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
        fin = open(infile,'rb')
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

def write_file_bytes(sarr,outfile=None):
    fout = sys.stdout
    if outfile is not None:
        fout = open(outfile, 'wb')
    if 'b' not in fout.mode:
        fout.buffer.write(sarr)
    else:        
        fout.write(sarr)
    if fout != sys.stdout:
        fout.close()
    fout = None
    return 


class ElfSearchObj(object):
	def __init__(self,fname):
		self.__fname = fname
		return

	def search_vaddr(self,offset):
		return ''



def backtraceparse_handler(args,parser):
	set_logging(args)
	s = read_file(args.input)
	sarr = re.split('\n', s)
	bsearch = False
	rets = ''
	symre = re.compile('.*SYMBOLSFUNC.*')
	funcre = re.compile('^FUNC\\[(\\d+)\\]\\s+\\[([^(]+)\\(([^)]+)\\).*')
	purehexre = re.compile('[\\+]?0x([a-fA-F0-9]+)')
	elfdicts = dict()
	lidx = 0
	for l in sarr:
		lidx += 1
		l = l.rstrip('\r\n')
		if bsearch:
			m = funcre.findall(l)
			if m is not None and len(m) > 0:
				if len(m[0]) >= 3:
					if purehexre.match(m[0][2]):
						cm = purehexre.findall(m[0][2])
						if len(cm) > 0:
							offset = int(cm[0],16)
							if m[0][1] not in elfdicts.keys():
								elfdicts[m[0][1]] = ElfSearchObj(m[0][1])
							funcsym = elfdicts[m[0][1]].search_vaddr(offset)
							logging.info('[%d]%s search [0x%x]'%(lidx,m[0][1],offset))
							rets += '%s %s\n'%(l,funcsym)
						else:
							rets += '%s %s\n'%(l,m[0][2])
					else:
						rets += '%s %s\n'%(l,m[0][2])
			else:
				bsearch = False
				if symre.match(l):
					bsearch = True
				rets += '%s\n'%(l)
		else:
			if symre.match(l):
				bsearch = True
			rets += '%s\n'%(l)

	write_file(rets,args.output)

	sys.exit(0)
	return


def main():
	cmdline='''
	{
		"verbose|v" : "+",
		"input|i" : null,
		"output|o" : null,
		"backtraceparse<backtraceparse_handler>##to parse backtrace functions##" : {
			"$" : 0
		}
	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(cmdline)
	parser.parse_command_line(None,parser)
	raise Exception('not exit in handlers')
	return

if __name__ == '__main__':
	main()

