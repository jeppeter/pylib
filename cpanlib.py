#! /usr/bin/env python

import os
import sys
import gzip
import re
import logging
import tarfile
import json
import urllib.request
import traceback

VERSION_KEYWORD = 'version'
TARFILE_KEYWORD = 'tarfile'
PREREQS_KEYWORD = 'prereqs'
RUNTIME_KEYWORD = 'runtime'
REQUIRES_KEYWORD = 'requires'

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
	def __init__(self,cpandir='%s/.cpan'%(os.environ['HOME'])):
		self.cpandir=  cpandir
		self.file = '%s/sources/modules/02packages.details.txt.gz'%(cpandir)
		self.maps = dict()
		self._error = None
		self._missingfiles = []
		return

	def _read_file(self,fname=None):
		outs = ''
		if fname is None:
			fname = self.file
		if fname.endswith('.gz'):
			inb = b''
			with gzip.open(fname,'r') as fin:
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
			inf = open(fname,'rb')
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
			#logging.info('[%s] key file %s'%(carr[0],carr[2]))
			self.maps[carr[0]] = curdict
		return

	def _get_pkg_dep(self,pkg):
		self._error = None
		retdeps = []

		if pkg not in self.maps.keys():
			self._error = '[%s] not in maps'%(pkg)
			return None
		# now to get the 
		curdict = self.maps[pkg]

		curfile = '%s/sources/authors/id/%s'%(self.cpandir,curdict[TARFILE_KEYWORD])
		if not os.path.exists(curfile):
			self._missingfiles.append(curfile)
			return []
		# now we should get the tar zip file
		rtar = ReadTar(curfile)
		rtar.open()
		dinfos = rtar.get_list()
		metaexpr = re.compile('.*\\/meta.json$',re.I)
		content = None
		for d in dinfos:
			name = d.name
			if metaexpr.match(name):
				logging.info('extract [%s] from [%s]'%(name,curfile))
				content = rtar.extract_file_content(name)
				break
		if content is None:
			self._error = '[%s] file [%s] can not find META.json'%(pkg,curfile)
			return None

		rdict = json.loads(content)
		if PREREQS_KEYWORD not in rdict.keys():
			return retdeps

		cdict = rdict[PREREQS_KEYWORD]
		if RUNTIME_KEYWORD not in cdict.keys():
			return []
		rundict = cdict[RUNTIME_KEYWORD]
		if REQUIRES_KEYWORD not in rundict.keys():
			return []

		reqdict = rundict[REQUIRES_KEYWORD]
		for k in reqdict.keys():
			retdeps.append(k)
		return retdeps

	def get_error(self):
		return self._error




	def get_dep(self,pkg,recursive=False):
		self._missingfiles = []
		truemap = dict()
		retdeps = []
		deps = self._get_pkg_dep(pkg)
		if deps is None:
			return None, self._missingfiles
		retdeps.append(pkg)
		retdeps.extend(deps)
		if recursive:
			truemap[pkg] = True
			for k in deps:
				if k not in truemap.keys():
					truemap[k] = False
			cont = True
			while cont:
				cont = False
				keys = truemap.keys()
				for k in keys:
					if not truemap[k]:
						deps = self._get_pkg_dep(k)
						if deps is None:
							return None, self._missingfiles
						retdeps.extend(deps)
						truemap[k] = True
						for ck in deps:
							if ck not in truemap.keys():
								logging.info('add [%s]'%(ck))
								truemap[ck] = False
						break
				for k in truemap.keys():
					if not truemap[k]:
						logging.info('[%s] will handle'%(k))
						cont = True
						break
				retdeps = list(set(retdeps))
				retdeps = sorted(retdeps)

		retdeps = list(set(retdeps))
		retdeps = sorted(retdeps)
		return retdeps,self._missingfiles



class CpanDownload(object):
	def __init__(self,url='https://223.5.5.5/'):
		self.baseurl = url
		self._error = None
		return

	def get_error(self):
		return self._error

	def download_file(self,fname):
		self._error = None
		retval = False
		carr = re.split('authors', fname)
		if len(carr) < 2:
			self._error = '%s not in authors'%(fname)
			return retval
		try:
			url = '%s/authors/%s'%(self.baseurl,carr[1])
			url = os.path.realpath(url)
			logging.info('request [%s] => [%s]'%(url,fname))
			urllib.request.urlretrieve(url,fname)
			retval = True
		except:
			self._error = '%s'%(traceback.format_exc())
		return retval



