#! /usr/bin/env python

import os
import sys
import gzip
import re
import logging

VERSION_KEYWORD = 'version'
TARFILE_KEYWORD = 'tarfile'

class ReadTar(object):
    def __init__(self,fname):
        self.fname = fname
        self.tarobj = None
        return

    def open(self,types='r:gz'):
        if self.tarobj is not None:
            self.tarobj.close()
            self.tarobj = None
        self.tarobj = tarfile.open(self.fname,types)
        return

    def get_list(self):
        if self.tarobj is None:
            raise Exception('not opened %s'%(self.fname))
        retobj = []
        for info in self.tarobj:
            retobj.append(info)
        return retobj

    def extract_file_content(self,fname):
        if self.tarobj is None:
            raise Exception('not opened %s'%(self.fname))
        f = self.tarobj.extractfile(fname)
        inb = f.read()
        return inb


class CpanPackages(object):
	def __init__(self,file,cpandir='%s/.cpan'%(os.environ['HOME'])):
		self.file = file
		self.cpandir=  cpandir
		self.maps = dict()
		return

	def _read_file(self):
		outs = ''
		if self.file.endswith('.gz'):
			inb = b''
			with gzip.open(self.file,'r') as fin:
				while True:
					ccb = fin.read(1024 * 128)
					if ccb is None or len(ccb) == 0:
						break
					inb += ccb
					logging.info('len %d'%(len(inb)))
			if sys.version[0] == '3':
				outs = inb.decode('utf-8')
			else:
				outs = string(inb)
		else:
			inf = open(self.file,'rb')
			inb = b''
			while True:
				cb = inf.read(1024*256)
				if cb is None or len(cb) == 0:
					break
				inb += cb
			if sys.version[0] == '3':
				outs = inb.decode('utf-8')
			else:
				outs = inb
		return outs


	def parse(self):
		retl = self._read_file()
		sarr = re.split('\n',retl)
		started = False
		index = 0
		for l in sarr:
			index += 1
			l = l.rstrip('\r')
			if not started:
				if len(l) == 0:
					started = True
				continue
			if len(l) == 0:
				continue
			carr = re.split('\\s+',l)
			if len(carr) < 3:
				logging.error('[%d] [%s]not matched'%(index,l))
				continue
			curdict = dict()
			curdict[VERSION_KEYWORD] = carr[1]
			curdict[TARFILE_KEYWORD] = carr[2]
			self.maps[carr[0]] = curdict
		return



