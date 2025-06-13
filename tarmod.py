#! /usr/bin/env python

import extargsparse
import tarfile
import logging
import sys
import os
import tempfile
import shutil
import subprocess
import time
import datetime
import re
import importlib
import fcntl
import math

sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..','pythonlib'))
sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('/usr/sbin/nanopi')
from common_util import set_logging,set_logging_args


def list_tar(infile):
	rmode = 'r:bz2'
	intar = tarfile.open(infile,mode=rmode)
	return intar.getmembers()
	
	

def add_tar(intar,infile,altname=None):
	outd = tempfile.mkdtemp()
	unzipcmd = 'bzip2'
	if os.path.exists(intar):
		abssrc = os.path.abspath(intar)
		cmd = 'cd %s && (cat %s | bzip2 -d | tar -xf -)'%(outd,abssrc)
		logging.info('cmd [%s]'%(cmd))
		subprocess.check_call(cmd,shell=True)
	tempf = tempfile.mktemp()
	outn = os.path.join(outd,altname)
	shutil.copyfile(infile,outn)
	cmd = 'cd %s && (tar -cf - * | bzip2 -9 | dd of=%s)'%(outd,tempf)
	logging.info('cmd [%s]'%(cmd))
	subprocess.check_call(cmd,shell=True)
	shutil.copyfile(tempf,intar)
	os.remove(tempf)
	shutil.rmtree(outd)
	return

def del_tar(intar,delfile):
	if not os.path.exists(intar):
		return
	outd = tempfile.mkdtemp()
	tempf = tempfile.mktemp()
	abssrc = os.path.abspath(intar)
	cmd = 'cd %s && (cat %s | bzip2 -d | tar -xf -)'%(outd,abssrc)
	logging.info('cmd [%s]'%(cmd))
	subprocess.check_call(cmd,shell=True)
	nfile = os.path.join(outd,delfile)
	if os.path.exists(nfile):
		os.remove(nfile)
	cmd = 'cd %s && (tar -cf - * | bzip2 -9 | dd of=%s)'%(outd,tempf)
	subprocess.check_call(cmd,shell=True)
	shutil.copyfile(tempf,intar)
	os.remove(tempf)
	shutil.rmtree(outd)
	return

def add_log(intar,logfile,maxlogs,reserved=False):
	tempd = tempfile.mkdtemp()
	if os.path.exists(intar):
		abssrc = os.path.abspath(intar)
		cmd = 'cd %s && (cat %s | bzip2 -d | tar -xf -)'%(tempd,abssrc)
		subprocess.check_call(cmd,shell=True)
	logname = os.path.basename(logfile)
	nsarr = re.split('\\.',logname)
	idx = 0
	nlogname = ''
	while idx < (len(nsarr) - 1):
		if idx > 0 :
			nlogname += '.'
		nlogname += '%s'%(nsarr[idx])
		idx += 1
	# to format time
	ntime = time.time()
	st = time.localtime(ntime)
	nlogname += '.%04d%02d%02d%02d%02d%02d'%(st.tm_year,st.tm_mon,st.tm_mday,st.tm_hour,st.tm_min,st.tm_sec)
	logging.info('new logname %s'%(nlogname))
	nabslog = os.path.join(tempd,nlogname)
	# now to copy for the name
	for rs,ds,fs in os.walk(tempd):
		if rs == tempd:
			if len(fs) > maxlogs:
				logging.info('fs %s'%(fs))
				fs.sort()
				logging.info('nfs %s'%(fs[0]))
				os.remove(os.path.join(tempd,fs[0]))
			break
	shutil.copyfile(logfile,nabslog)
	tempf = tempfile.mktemp()
	cmd = 'cd %s && (tar -cf - * | bzip2 -9 | dd of=%s)'%(tempd,tempf)
	subprocess.check_call(cmd,shell=True)
	shutil.copyfile(tempf,intar)
	if not reserved:
		os.remove(tempf)
		shutil.rmtree(tempd)
	else:
		logging.info('tempd %s tempf %s'%(tempd, tempf))
	return True





def detach_run(cmdargs,shellmode=False):
	#logging.info('run %s'%(cmdargs))
	p = subprocess.Popen(cmdargs,shell=shellmode)
	return

def run_add_log(fname):
	m = importlib.import_module('__main__')
	mainfile = os.path.abspath(m.__file__)
	cmds = [sys.executable,mainfile,'addlog',fname]
	detach_run(cmds)
	return


def listtar_handler(args,parser):
	set_logging(args)
	for f in args.subnargs:
		listv = list_tar(f)
		sys.stdout.write('%s list %s\n'%(f,listv))
	sys.exit(0)
	return

def addtar_handler(args,parser):
	set_logging(args)
	tarname = args.subnargs[0]
	f = args.subnargs[1]
	altname = None
	if len(args.subnargs) > 2:
		altname = args.subnargs[2]
	add_tar(tarname,f,altname)
	sys.exit(0)
	return

def deltar_handler(args,parser):
	set_logging(args)
	tarname = args.subnargs[0]
	f = args.subnargs[1]
	del_tar(tarname,f)
	sys.exit(0)
	return

def detachrun_handler(args,parser):
	set_logging(args)
	detach_run(args.subnargs,False)
	sys.exit(0)
	return

def lock_file_timeout(fname,maxtime=0.0):
    f = open(fname,'w')
    fd = f.fileno()
    stime = time.time()
    etime = stime + maxtime
    errcnt = 0
    while True:
        ctime = time.time()
        if math.fabs(maxtime) > 0.001 and ctime > etime:
            logging.info('lock %s timeout'%(fname))
            return None
        try:
            fcntl.lockf(fd,fcntl.LOCK_EX | fcntl.LOCK_NB)
            logging.info('retval %s succ'%(fname))
            break
        except:
            time.sleep(0.3)
            errcnt += 1
            if (errcnt % 10) == 0:
                logging.error('lock %s failed %d\n%s'%(fname,errcnt,traceback.format_exc()))
    return f


def addlog_handler(args,parser):
	set_logging(args)
	retval = lock_file_timeout('/tmp/addlog_handler')
	if not retval :
		sys.exit(5)
	logfile = args.subnargs[0]
	if len(args.subnargs) > 1 :
		logtar = args.subnargs[1]
	else:
		bdir = os.path.dirname(logfile)
		bbase = os.path.basename(logfile)
		nsarr = re.split('\\.',bbase)
		nfile = ''
		idx = 0
		while idx < (len(nsarr) - 1):
			if idx > 0:
				nfile += '.'
			nfile += '%s'%(nsarr[idx])
			idx += 1
		nfile += '.tar.bz2'
		logtar = os.path.join(bdir,nfile)
		logging.info('logtar %s'%(logtar))
	add_log(logtar,logfile,args.maxlogs,args.reserved)
	sys.exit(0)
	return

def callmain_handler(args,parser):
	set_logging(args)
	m = importlib.import_module('__main__')
	sys.stdout.write('file %s\n'%(os.path.abspath(m.__file__)))
	sys.exit(0)
	return


def lockfile_handler(args,parser):
	set_logging(args)
	fname = args.subnargs[0]
	timewait = 10.0
	if len(args.subnargs) > 1:
		timewait = float(args.subnargs[1])
	retval = lock_file_timeout(fname)
	if retval is None:
		logging.error('lock %s failed'%(fname))
		sys.exit(5)
	time.sleep(timewait)	
	sys.exit(0)
	return


def runaddlog_handler(args,parser):
	set_logging(args)
	run_add_log(args.subnargs[0])
	sys.exit(0)
	return


def load_tar_commands(parser):
	cmdfmt = '''
	{
		"maxlogs" : 7,
        "listtar<%s.listtar_handler>##tarfile to list tarfile##" : {
        	"$" : "+"
        },
        "addtar<%s.addtar_handler>##tarfile infile [altname] to add to tarfile##" : {
        	"$" : "+"
        },
        "deltar<%s.deltar_handler>##tarfile delfile to delete file##" : {
        	"$" : "+"
        },
        "detachrun<%s.detachrun_handler>##cmds ... to run##" : {
        	"$" : "+"
        },
        "addlog<%s.addlog_handler>##logfile [logtar] to add log##" : {
        	"$" : "+"
        },
        "callmain<%s.callmain_handler>##to call main file##" : {
        	"$" : 0
        },
        "lockfile<%s.lockfile_handler>##lockfile [time] to lock file default 10.0##" : {
        	"$" : "+"
        },
        "runaddlog<%s.runaddlog_handler>##file to run addlog##" : {
        	"$" : 1
        }
	}
	'''
	command = cmdfmt%(__name__,__name__,__name__,__name__,__name__,__name__,__name__,__name__)
	parser.load_command_line_string(command)
	return parser
