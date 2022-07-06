#! /usr/bin/env python

import logging
import extargsparse
import re
import sys

from elftools.elf.elffile import ELFFile

from elftools.elf.sections import (
    NoteSection, SymbolTableSection, SymbolTableIndexSection
)

from elftools.elf.descriptions import (
	describe_symbol_shndx
)

from elftools.elf.constants import SHN_INDICES

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


def sort_symbol(k):
	sym = k[0]
	return sym['st_value']

class ElfSearchObj(object):
	def __init__(self,fname):
		self.__fname = fname
		self.__elffile = ELFFile(open(fname,'rb'))
		self.__symtabs = []
		self.__sections = []
		sectidx = 0
		for s in self.__elffile.iter_sections():
			if isinstance(s,SymbolTableSection):
				self.__sections.append(s)
				symidx = 0
				for symbol in s.iter_symbols():
					if symbol['st_size'] != 0:
						nc = (symbol,symidx,sectidx)
						self.__symtabs.append(nc)
					symidx += 1
			sectidx += 1
		self.__symtabs.sort(key=sort_symbol)
		self.__shn_sections = []
		for s in self.__elffile.iter_sections():
			if isinstance(s,SymbolTableIndexSection):
				logging.info('SymbolTableIndexSection %s'%(repr(s)))
				self.__shn_sections.append(s.symboltable)
		return

	def __search_name(self,sym,symidx,sectidx):
		return sym.name

	def search_symbol_vaddr(self,offset):
		sidx = 0
		eidx = len(self.__symtabs) - 1
		cidx = int((sidx + eidx)/2)
		#logging.info('search [%s] [0x%x]'%(self.__fname, offset))
		while sidx < eidx:
			k = self.__symtabs[cidx]
			sym = k[0]
			if sym['st_value'] <= offset and offset < (sym['st_value'] + sym['st_size']):
				return '%s+0x%x'%(self.__search_name(sym,k[1],k[2]), offset - sym['st_value'])
			elif offset < sym['st_value']:
				eidx = cidx
			else:
				sidx = cidx

			if eidx <= sidx:
				return 'must 0x%x value [0x%x]'%(offset,sym['st_value'])

			if eidx == (sidx + 1):
				k = self.__symtabs[sidx]
				sym = k[0]
				if sym['st_value'] <= offset and offset < (sym['st_value'] + sym['st_size']):
					return '%s+0x%x'%(self.__search_name(sym,k[1],k[2]), offset - sym['st_value'])

				k = self.__symtabs[eidx]
				sym = k[0]
				if sym['st_value'] <= offset and offset < (sym['st_value'] + sym['st_size']):
					return '%s+0x%x'%(self.__search_name(sym,k[1],k[2]), offset - sym['st_value'])
				t = self.__symtabs[sidx]
				tsym = t[0]
				logging.error('%s [0x%x] + [0x%x] >> 0x%x << %s [0x%x] '%(self.__search_name(tsym,t[1],t[2]), tsym['st_value'] , tsym['st_size'] ,offset,self.__search_name(sym,k[1],k[2]), sym['st_value']))
				return '%s+0x%x'%(self.__search_name(tsym,t[1],t[2]), offset - tsym['st_value'])
			#logging.info('sidx [%d] eidx [%d]'%(sidx, eidx))
			cidx = int((eidx + sidx)/2)

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
							fname = m[0][1]
							if fname not in elfdicts.keys():
								elfdicts[fname] = ElfSearchObj(fname)
							funcsym = elfdicts[fname].search_symbol_vaddr(offset)
							logging.info('[%d]%s search [0x%x] [%s]'%(lidx,fname,offset, funcsym))
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
		"backtracedump<backtraceparse_handler>##to parse backtrace functions##" : {
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

