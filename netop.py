#! /usr/bin/env python

import sys
import os
import logging
import time
import math
import traceback
import requests

sys.path.insert(0,os.path.join(os.path.dirname(__file__),'pythonlib'))
import extargsparse

class DownloadProgress(object):
	def __init__(self,f):
		self.fname = f
		self.outs = ''
		return

	def step(self,inlen):
		if len(self.outs) > 0:
			idx = 0
			while idx < len(self.outs):
				sys.stdout.write('\b')
				idx += 1
		self.outs = '%s %d'%(self.fname,inlen)
		sys.stdout.write('%s'%(self.outs))
		sys.stdout.flush()
		return

	def end(self,inlen):
		if len(self.outs) > 0:
			idx = 0
			while idx < len(self.outs):
				sys.stdout.write('\b')
				idx += 1
		self.outs = '%s %d'%(self.fname,inlen)
		sys.stdout.write('%s\n'%(self.outs))
		return



def download_file(url,f,tmout=10.0,progobj=None,throwexp=True):
	retval = False
	err = ''
	outs = ''
	if progobj is None:
		progobj = DownloadProgress(f)
	else:
		if not issubclass(progobj, DownloadProgress):
			if throwexp:
				return retval
			raise Exception('%s not DownloadProgress object'%(progobj))
	try:
		inlen = 0		
		if math.fabs(tmout - 0.0) < 0.00001:
			with requests.get(url,stream=True) as sf:
				sf.raise_for_status()
				with open(f,mode='wb') as fout:
					for chunk in sf.iter_content(chunk_size=64 * 1024):
						inlen += len(chunk)
						progobj.step(inlen)
						fout.write(chunk)
						fout.flush()			
		else:
			with requests.get(url,stream=True,timeout=tmout) as sf:
				sf.raise_for_status()
				with open(f,mode='wb') as fout:
					for chunk in sf.iter_content(chunk_size=64 * 1024):
						inlen += len(chunk)
						progobj.step(inlen)
						fout.write(chunk)
						fout.flush()
		retval = True
		progobj.end(inlen)
	except:
		err = '%s'%(traceback.format_exc())
		logging.info('%s'%(err))
	if not retval and throwexp:
		raise Exception('%s'%(err))
	return retval
