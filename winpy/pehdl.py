#! /usr/bin/env python

import extargsparse
import re
import sys
import os
import logging


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import loglib
import fileop

class MemorySection(object):
	def __init__(self, saddr, eaddr,fname):
		self.saddr = saddr
		self.eaddr = eaddr
		self.fname = fname
		return

class MemoryMap(object):
	def __init__(self):
		self.maps = []
		return

	def add_map(self,saddr,eaddr,fname):
		self.maps.append(MemorySection(saddr,eaddr,fname))
		return

	def search(self,addr):
		sidx = 0
		eidx = len(self.maps) - 1


		while sidx < eidx:
			cidx = int((sidx + eidx)/2)
			if cidx == sidx:
				if self.maps[cidx].eaddr > addr:
					sectstart=  self.maps[cidx].saddr
					offset = addr - self.maps[cidx].saddr
					fname = self.maps[cidx].fname
					return sectstart,offset,fname
				sidx += 1
			elif cidx == eidx:
				if self.maps[cidx].saddr < addr:
					sectstart=  self.maps[cidx].saddr
					offset = addr - self.maps[cidx].saddr
					fname = self.maps[cidx].fname
					return sectstart,offset,fname
				eidx -= 1
			else:
				if self.maps[cidx].saddr <= addr and self.maps[cidx].eaddr >= addr:
					sectstart=  self.maps[cidx].saddr
					offset = addr - self.maps[cidx].saddr
					fname = self.maps[cidx].fname
					return sectstart,offset,fname
				if self.maps[cidx].eaddr < addr:
					sidx = cidx
				else:
					eidx = cidx
		assert(sidx == eidx)
		sectstart = self.maps[sidx].saddr
		offset = addr - sectstart
		fname = self.maps[sidx].fname
		return sectstart,offset,fname


def callsearch_handler(args,parser):
	loglib.set_logging(args)
	s =fileop.read_file(args.input)
	sarr = re.split('\n',s)
	funcstack = []
	funcexpr = re.compile('^\\[([0-9]+)\\]\\s+0x([0-9a-fA-F]+)$')
	spanexpr = re.compile('^\\[0x([0-9a-fA-F]+)\\]\\s+\\-\\s+\\[0x([0-9a-fA-F]+)\\]\\s+\\[([^\\]]*)\\]')
	memmap = MemoryMap()

	for l in sarr:
		l = l.rstrip('\r')
		m = funcexpr.findall(l)
		if m is not None and len(m) > 0 and len(m[0]) > 1:
			funcstack.append(int(m[0][1],16))
			continue
		m = spanexpr.findall(l)
		if m is not None and len(m) > 0 and len(m[0]) > 2:
			memmap.add_map(int(m[0][0],16),int(m[0][1],16),m[0][2])
			continue
	for f in funcstack:
		saddr ,offset, fname = memmap.search(f)
		sys.stdout.write('[0x%x] 0x%x 0x%x %s\n'%(f,saddr,offset,fname))
	sys.exit(0)
	return

def main():
	cmdline='''
	{
		"input|i" : null,
		"output|o" : null,
		"callsearch<callsearch_handler>##from input to search file##" : {
			"$" : 0
		}
	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(cmdline)
	parser = loglib.load_log_commandline(parser)
	args = parser.parse_command_line(None,parser)
	raise Exception('can not handle [%s]'%(args))
	return

if __name__ == '__main__':
	main()




