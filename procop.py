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


class ProcExpolore(object):
	def __init__(self):
		self.process = dict()
		return

	def _read_subprocess_output(self,cmds,shellmode=False):
		logging.info('cmds %s'%(cmds))
		p = subprocess.Popen(cmds,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=shellmode)
		stdoutbuf,stderrbuf = p.communicate()
		return stdoutbuf,stderrbuf


	def _scan_windows(self):
		outb,_ = self._read_subprocess_output(['wmic.exe','process','Get','ProcessId,Caption,CommandLine,ExecutablePath'])
		# now we should give the process get caption
		return

	def _scan_unix(self):
		return


	def snapshot(self):
		self.process = dict()
		if is_windows():
			self._scan_windows()
		else:
			self._scan_unix()
		return

	def result(self):
		return self.process

