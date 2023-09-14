#! /usr/bin/env python

import os
import sys
import extargsparse
import logging
import re
import struct


sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import fileop


class HwdbHeader(object):
	def __init__(self):
		self.version = 0
		self.hdrsize = 0
		self.nodesize = 0
		self.chldentsize = 0
		self.valentsize = 0
		self.rootoffset = 0
		self.nodeslen = 0
		self.stringslen = 0
		return

	def dump_data(self,indb):
		if len(indb) < 72:
			raise Exception('indb [%d] need at least 72'%(len(indb)))
		passed = 0
		magic = indb[:8]
		passed += 8
		if magic != b'KSLPHHRH':
			raise Exception('need KSLPHHRH but get %s'%(fileop.format_bytes(magic,'HEADER')))
		self.version,self.hdrsize,self.nodesize,self.chldentsize,self.valentsize,self.rootoffset,self.nodeslen,self.stringslen = struct.unpack('<QQQQQQQQ',indb[passed:(passed+64)])
		logging.info('version 0x%x hdrsize 0x%x nodesize 0x%x child entry size 0x%x value entry size 0x%x'%(self.version,self.hdrsize,self.nodesize,self.chldentsize,self.valentsize))
		logging.info('rootoffset 0x%x nodeslen 0x%x stringslen 0x%x'%(self.rootoffset,self.nodeslen,self.stringslen))
		if len(indb) < self.hdrsize:
			raise Exception('hdrsize 0x%x > len(0x%x)'%(self.hdrsize,len(indb)))
		passed += 64
		return passed

class HwChild(object):
	def __init__(self):
		return

	def load_data(self,indb,offset):
		if len(indb[offset:]) < 16:
			raise Exception('len(%d) < 16'%(len(indb[offset:])))
		passed = offset
		self.c = struct.unpack('<b',indb[passed:(passed+1)])[0]
		passed += 8
		self.child_off = struct.unpack('<Q',indb[passed:(passed+8)])[0]
		passed += 8
		logging.info('c 0x%x child_off 0x%x'%(self.c & 0xff,self.child_off))
		return passed

class HwNode(object):
	def __init__(self):
		self.prefix_off = 0
		self.children_count = 0
		self.values_count = 0
		self.children = []
		self.childreninfo = []
		return

	def load_data(self,indb,offset,entsize):
		if len(indb[offset:]) < 24:
			raise Exception('len(%d) < 24'%(len(indb[offset:])))
		passed = offset
		self.prefix_off = struct.unpack('<Q',indb[passed:(passed+8)])[0]
		passed += 8
		self.children_count = struct.unpack('<b',indb[passed:(passed+1)])[0]
		passed += 8
		self.values_count = struct.unpack('<Q',indb[passed:(passed+8)])[0]
		passed += 8
		passed -= offset
		logging.info('prefix_off 0x%x children_count 0x%x values_count 0x%x'%(self.prefix_off,self.children_count,self.values_count))
		# now to pass 
		self.childreninfo = []

		idx = 0
		curoff = offset + entsize
		while idx < self.children_count:
			curchldinfo = HwChild()
			curchldinfo.load_data(indb,curoff)
			self.childreninfo.append(curchldinfo)
			curchld = HwNode()
			curchld.load_data(indb,curchldinfo.child_off,entsize)
			self.children.append(curchld)
			curoff += 16
			idx += 1
		return passed



class Hwdb(object):
	def __init__(self):
		self.header = None
		self.db = b''
		return

	def _load_inner(self):
		self.header = HwdbHeader()
		passed = 0
		passed += self.header.dump_data(self.db[passed:])
		self.root = HwNode()
		self.root.load_data(self.db,self.header.rootoffset,self.header.chldentsize)
		return



	def load_file(self,infile):
		self.db = fileop.read_file_bytes(infile)
		self._load_inner()
		return


def dump_handler(args,parser):
	fileop.set_logging(args)
	for f in args.subnargs:
		trif = Hwdb()
		trif.load_file(f)
	sys.exit(0)
	return

def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "dump<dump_handler>##hwdb.bin ... to dump file ##" : {
            "$" : "+"
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    fileop.load_log_commandline(parser)
    parser.parse_command_line(None,parser)
    raise Exception('can not reach here')
    return

if __name__ == '__main__':
    main()    