#! /usr/bin/env python

import sys
import os
import subprocess
import logging

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
from envop import is_windows

class ProcInfo(object):
	def __init__(self):
		self.pid = None
		self.cmdline = []
		self.parentpid = None
		self.firstarg = ''
		return
	def set_pid(self,pid):
		self.pid = pid
		return

	def set_cmdline(self,cmdline):
		self.cmdline = cmdline
		return

	def set_parentpid(self,pid):
		self.parentpid = pid
		return

	def set_firstarg(self,firstarg):
		self.firstarg = firstarg
		return

class _winprocindex(object):
	def __init__(self):
		self._reset()
		return

	def _reset(self):
		self.pidstart = None
		self.pidend = None
		self.cmdstart = None
		self.cmdend = None
		self.execstart = None
		self.execend = None
		self.capstart = None
		self.capend = None
		return

	def parse_buf(self,buf):
		self._reset()
		idx = 0
		bstart = False
		curstart = None
		curend = None
		while idx < len(buf):
			if curstart is None:
				if buf[idx] != ord(' '):
					curstart = idx
			else:
				if curend is None:
					if buf[idx] == ord(' '):
						curend = idx
				else:
					if buf[idx] != ord(' '):
						# now to give the buffer
						logging.info('')


class ProcExpolore(object):
	def __init__(self):
		self.process = dict()
		return

	def _read_subprocess_output(self,cmds,shellmode=False):
		logging.info('cmds %s'%(cmds))
		p = subprocess.Popen(cmds,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=shellmode)
		stdoutbuf,stderrbuf = p.communicate()
		return stdoutbuf,stderrbuf

	def _split_buf_lines(self,buf):
		retbufs = []
		idx = 0
		sidx = 0
		while idx < len(buf):			
			if buf[idx] == ord('\r') or buf[idx] == ord('\n'):
				logging.info('[%d]=b[0x%x]'%(idx,buf[idx]))
				while (idx + 1) < len(buf) and (buf[idx] == ord('\r') or buf[idx+1] == ord('\n')):
					idx += 1
				logging.info('add [%d:%d] [%s]'%(sidx,idx+1,buf[sidx:(idx+1)]))
				retbufs.append(buf[sidx:(idx+1)])
				sidx = idx+1
			idx += 1
		if sidx < len(buf):
			retbufs.append(buf[sidx:])
		return retbufs



	def _scan_windows(self):
		outb,_ = self._read_subprocess_output(['wmic.exe','process','Get','ProcessId,Caption,CommandLine,ExecutablePath'])
		retlines = self._split_buf_lines(outb)
		# now we should give the process get caption
		wproc = _winprocindex()
		idx = 0
		while idx < len(retlines):
			curline = retlines[idx]
			if idx == 0:
				# that is to make sure the pid
				wproc.parse_buf(curline)


		return

	def _scan_unix(self):
		return


	def snapshot(self):
		self.process = dict()
		retval = True
		try:
			if is_windows():
				self._scan_windows()
			else:
				self._scan_unix()
		except:
			retval = False
			logging.error('%s'%(traceback.format_exc()))
		return retval

	def result(self):
		return self.process

