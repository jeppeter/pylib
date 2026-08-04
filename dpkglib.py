#! /usr/bin/env python


import re
import logging
import sys
import os
import traceback


PRE_DEPS_KEYWORD = 'Pre-Depends'
DEPS_KEYWORD = 'Depends'
PACKAGE_KEYWORD = 'Package'
STATUS_KEYWORD = 'Status'

class DpkgPackage(object):
	def __init__(self):
		self.info = dict()
		self.name = ''
		self.__start = False

		return

	def parse(self,sarr,index):
		passed = index
		lastkey = None
		mkeyexpr = re.compile('^([A-Za-z0-9\\-]+):\\s+(.*)$')
		while passed < len(sarr):
			l = sarr[passed]
			l = l.rstrip('\r\n')
			if self.__start:
				if len(l) == 0:
					break
			else:
				if len(l) != 0:
					self.__start = True
				else:
					passed += 1
					continue
			m = mkeyexpr.findall(l)
			if m is None or len(m) == 0 or len(m[0]) == 0:
				if lastkey is not None:
					self.info[lastkey] += '%s\n'%(l)
				else:
					logging.error('no key set for line:%d %s'%(passed,l))
			else:				
				lastkey = m[0][0]
				l = m[0][1]
				l = l.rstrip('\r\n')
				l = l.rstrip('\t ')
				l = l.strip('\t ')
				self.info[lastkey] = l
				if lastkey == PACKAGE_KEYWORD:
					self.name = l
			passed += 1
		return passed


class DpkgDatabase(object):
	def __init__(self,infile):
		self.infile = infile
		self.maps = dict()
		return


	def _read_file(self):
	    fin = open(self.infile,'rb')
	    rets = ''
	    if 'b' in fin.mode:
	        rdata = b''
	        while True:
	            try:
	                l = fin.read(64 * 1024)
	                if l is None or len(l) == 0:
	                    break
	                rdata += l
	            except:
	                break
	        if sys.version[0] == '3':
	            rets = rdata.decode('utf-8')
	        else:
	            rets = rdata
	    else:        
	        for l in fin:
	            s = l
	            rets += s

	    fin.close()
	    fin = None
	    return rets

	def parse(self):
		ins = self._read_file()
		sarr = re.split('\n',ins)
		indx = 0
		while indx < len(sarr):
			obj = DpkgPackage()
			indx = obj.parse(sarr,indx)
			if obj.name != '':
				if obj.name in self.maps.keys():
					logging.error('%s duplicated'%(obj.name))
					self.maps[obj.name] = obj
				else:
					logging.info('add [%s]'%(obj.name))
					self.maps[obj.name] = obj
			else:
				logging.info('passed %d lines'%(indx))
		return


class DpkgDeps(object):
	def __init__(self,val):
		if isinstance(val,DpkgDatabase):
			self.db = val
		else:
			self.db = DpkgDatabase(val)
			self.db.parse()
		return

	def _get_dep(self,name):
		deps = []
		if name in self.db.maps.keys():
			obj = self.db.maps[name]
			logging.info('has info [%s] keys %s'%(name,obj.info.keys()))
			if DEPS_KEYWORD in obj.info.keys():
				logging.info('[%s] has %s [%s]'%(name,DEPS_KEYWORD,obj.info[DEPS_KEYWORD]))
				sarr = re.split(',',obj.info[DEPS_KEYWORD])
				for l in sarr:
					p = re.sub('\\(([^\\)]+)\\)','',l)
					carr = re.split('\\|',p)
					for cp in carr:
						cp = cp.rstrip('\t ')
						cp = cp.strip('\t ')
						if cp in self.db.maps.keys():
							logging.info('add [%s] for [%s]'%(cp,name))
							deps.append(cp)
							break
			if PRE_DEPS_KEYWORD in obj.info.keys():
				logging.info('[%s] has %s'%(name,PRE_DEPS_KEYWORD))
				sarr = re.split(',',obj.info[PRE_DEPS_KEYWORD])
				for l in sarr:
					p = re.sub('\\(([^\\)]+)\\)','',l)
					carr = re.split('\\|',p)
					for cp in carr:
						cp = cp.rstrip('\t ')
						cp = cp.strip('\t ')
						if cp in self.db.maps.keys():
							logging.info('add [%s] for [%s]'%(cp,name))
							deps.append(cp)
							break
		else:
			logging.error('no [%s] find in maps'%(name))
		return deps

	def get_dep(self,name,recursive=False):
		totaldeps = dict()
		deps = self._get_dep(name)
		totaldeps[name] = True
		retdeps = []
		retdeps.extend(deps)
		for k in retdeps:
			if k not in totaldeps.keys():
				totaldeps[k] = False
		cont = True
		while cont and recursive:
			cont = False
			curkeys = totaldeps.keys()
			nkeys = []
			setkeys = []
			for k in curkeys:
				v = totaldeps[k]
				logging.info('%s %s'%(k,v))
				if not v:
					deps = self._get_dep(k)
					logging.info('%s deps %s'%(k,deps))
					setkeys.append(k)
					retdeps.extend(deps)
			retdeps = list(set(retdeps))
			retdeps = sorted(retdeps)
			for k in setkeys:
				totaldeps[k] = True
			for k in retdeps:
				if k not in totaldeps.keys():
					cont = True
					totaldeps[k] = False
				elif not totaldeps[k]:
					cont = True

		retdeps = list(set(retdeps))
		retdeps = sorted(retdeps)
		return retdeps


class DpkgInstalled(object):
	def __init__(self,val):
		if isinstance(val,DpkgDatabase):
			self.db = val
		else:
			self.db = DpkgDatabase(val)
			self.db.parse()
		return


	def get_installed(self,name):
		retval = False
		try:
			if name in self.db.maps.keys():
				curmap = self.db.maps[name]
				logging.info('curmap %s'%(curmap))
				if STATUS_KEYWORD in curmap.info.keys():
					l = curmap.info[STATUS_KEYWORD]
					instexpr = re.compile('^install\\s+ok\\s+installed$',re.I)
					if instexpr.match(l):
						retval = True
		except:
			logging.error('%s'%(traceback.format_exc()))
		return retval

class DpkgFiles(object):
	def __init__(self,datadir):
		self.datadir = datadir
		return

	def _read_file(self,infile):
	    fin = open(infile,'rb')
	    rets = ''
	    if 'b' in fin.mode:
	        rdata = b''
	        while True:
	            try:
	                l = fin.read(64 * 1024)
	                if l is None or len(l) == 0:
	                    break
	                rdata += l
	            except:
	                break
	        if sys.version[0] == '3':
	            rets = rdata.decode('utf-8')
	        else:
	            rets = rdata
	    else:        
	        for l in fin:
	            s = l
	            rets += s

	    fin.close()
	    fin = None
	    return rets

	def _get_match_list(self,name):
		matchfiles = []
		mname = name
		mname = re.sub('\\+','\\\\+',name)
		restr = '^%s(:[A-Za-z0-9]+)?.list'%(mname)
		mexpr = re.compile(restr)
		logging.info('search [%s] restr [%s]'%(name,restr))
		with os.scandir(self.datadir) as entries:
			for fobj in entries:
				if fobj.is_file() and mexpr.match(fobj.name):
					logging.info('match [%s]'%(fobj.name))
					matchfiles.append(fobj.name)
		return matchfiles

	def get_files(self,name):
		retfiles = []
		matchfiles = self._get_match_list(name)
		for f in matchfiles:
			listname = os.path.join(self.datadir,f)
			ins = self._read_file(listname)
			sarr = re.split('\n',ins)
			for l in sarr:
				l = l.rstrip('\r\n')
				l = l.rstrip('\t ')
				if len(l) >0 :
					retfiles.append(l)
		return retfiles

