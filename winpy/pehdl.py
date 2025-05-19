#! /usr/bin/env python

import extargsparse
import re
import sys
import os
import logging
import struct


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
	spanexpr = re.compile('^\\[0x([0-9a-fA-F]+)\\]\\s+\\-\\s+\\[0x([0-9a-fA-F]+)\\]\\s+\\[([^\\]]*)\\]\\s+\\[([^\\]]*)\\]')
	memmap = MemoryMap()

	for l in sarr:
		l = l.rstrip('\r')
		m = funcexpr.findall(l)
		if m is not None and len(m) > 0 and len(m[0]) > 1:
			funcstack.append(int(m[0][1],16))
			continue
		m = spanexpr.findall(l)
		if m is not None and len(m) > 0 and len(m[0]) > 3:
			memmap.add_map(int(m[0][0],16),int(m[0][1],16),m[0][3])
			continue
	for f in funcstack:
		saddr ,offset, fname = memmap.search(f)
		sys.stdout.write('[0x%x] 0x%x 0x%x %s\n'%(f,saddr,offset,fname))
	sys.exit(0)
	return

class OffsetFile(object):
	def __init__(self,fname,memoff,memsize):
		self.fname = fname
		self.memoff = memoff
		self.memsize = memsize
		self.data = []
		return

	def add_bytes(self,data):
		self.data.extend(data)
		return
	def cmp_bytes(self,other):
		idx = 0
		offset = 0
		msize = 0
		sidx = 0
		didx = 0
		moffset = -1

		if len(self.data) < 16:
			raise Exception('self.data [%d]'%(len(self.data)))
		if len(other.data) < 16:
			raise Exception('other.data [%d]'%(len(other.data)))
		while didx < len(other.data):
			tmpdidx = didx
			sidx = 0
			# first to search 16 bytes
			while sidx < 16 and tmpdidx < len(other.data):
				if self.data[sidx] != other.data[tmpdidx]:
					break
				sidx += 1
				tmpdidx += 1
			if sidx < 16:
				didx += 1
				continue
			# now it is match
			while sidx < len(self.data) and tmpdidx < len(other.data):
				if self.data[sidx] != other.data[tmpdidx]:
					break
				sidx += 1
				tmpdidx += 1
			logging.info('curoffset 0x%x  size 0x%x'%(tmpdidx - sidx, sidx))
			if sidx > msize:
				moffset= tmpdidx - sidx
				msize = sidx
			didx += sidx			
		return moffset,msize

def pemapsearch_handler(args,parser):
	loglib.set_logging(args)
	s =fileop.read_file(args.input)
	sarr = re.split('\n',s)
	funcstack = []
	startfileexpr = re.compile('^\\[([0-9]+)\\]\\[([^\\]]+)\\]\\s+0x([0-9a-fA-F]+)\\s+size\\s+0x([0-9a-fA-F]+)')
	linematchexpr = re.compile('^0x([0-9a-fA-F]+):\\s+(.*)')
	mfile = False
	curfile = None
	offsetmaps = []
	for l in sarr:
		l = l.rstrip('\r')
		if curfile is None:
			m = startfileexpr.findall(l)
			if m is not None and len(m) > 0:
				curfile = OffsetFile(m[0][1],int(m[0][2],16),int(m[0][3],16))
				continue
		else:
			m = linematchexpr.findall(l)
			if m is not None and len(m) > 0 and len(m[0]) > 1:
				#logging.info('l[%s]'%(l))
				carr = re.split('\\s+',m[0][1])
				idx = 0
				jdx = 0
				data = []
				while idx < 16:
					if len(carr[jdx]) > 0:
						data.append(int(carr[jdx][2:],16))
						idx += 1
					jdx += 1
				curfile.add_bytes(data)
			else:
				offsetmaps.append(curfile)
				curfile = None
			continue

	for f in args.subnargs:
		basef = os.path.basename(f)
		fdata = fileop.read_file_bytes(f)
		rawdata = OffsetFile(f,0,0)
		rawdata.add_bytes(fdata)
		for m in offsetmaps:
			cmpf = os.path.basename(m.fname)
			if cmpf == basef:
				offset,size = m.cmp_bytes(rawdata)
				sys.stdout.write('[%s][0x%x][0x%x] match 0x%x size 0x%x\n'%(m.fname,m.memoff,m.memsize,offset,size))
	sys.exit(0)
	return

def main():
	cmdline='''
	{
		"input|i" : null,
		"output|o" : null,
		"callsearch<callsearch_handler>##from input to search file##" : {
			"$" : 0
		},
		"pemapsearch<pemapsearch_handler>##dllfile ... to map files##" : {
			"$" : "+"
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




