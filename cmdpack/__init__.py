#!/usr/bin/python

import os
import sys
import subprocess
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import dbgexp

def run_cmd_wait(cmd,mustsucc=1):
	logging.debug('run (%s)'%(cmd))
	ret = subprocess.call(cmd,shell=True)
	if mustsucc and ret != 0:
		raise dbgexp.DebugException(dbgexp.ERROR_RUN_CMD,'run cmd (%s) error'%(cmd))
	return ret

def run_read_cmd(cmd):
	#logging.debug('run (%s)'%(cmd))
	p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
	return p

def __trans_to_string(s):
	if sys.version[0] == '3':
		return s.decode(encoding='UTF-8')
	return s

def read_line(pin,ch='\r'):
	s = ''
	retbyte = '\n'
	chbyte = ch
	if sys.version[0] == '3':
		retbyte = '\n'.encode(encoding='UTF-8')
		chbyte = ch.encode(encoding='UTF-8')
		s = bytes()
	while True:
		b = pin.read(1)
		if b is None or len(b) == 0:
			if len(s) == 0:
				return None
			return __trans_to_string(s)
		if b != chbyte and b != retbyte:
			if sys.version[0] == '3':
				# it is python3
				s += b
			else:
				s += b
			continue

		return __trans_to_string(s)
	return __trans_to_string(s)


def run_command_callback(cmd,callback,ctx):
	p = run_read_cmd(cmd)
	exited = 0
	exitcode = -1
	while exited == 0:
		pret = p.poll()
		#logging.debug('pret %s'%(repr(pret)))
		if pret is not None:
			exitcode = pret
			exited = 1
			#logging.debug('exitcode (%d)'%(exitcode))
			while True:
				rl = read_line(p.stdout)
				#logging.debug('read (%s)'%(rl))
				if rl is None:
					break
				if callback is not None:
					callback(rl,ctx)
			break
		else:
			rl = read_line(p.stdout)
			#logging.debug('read (%s)'%(rl))
			if rl :
				if callback is not None:
					callback(rl,ctx)
	return exitcode
