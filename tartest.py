#! /usr/bin/env python

import extargsparse
import tarfile
import logging
import sys
import os
import tempfile
import shutil
import subprocess

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

def detach_run(cmdargs,shellmode=False):
	logging.info('run %s'%(cmdargs))
	p = subprocess.Popen(cmdargs,shell=shellmode)
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

def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "compresstype" : "bz2",
        "listtar<listtar_handler>##tarfile to list tarfile##" : {
        	"$" : "+"
        },
        "addtar<addtar_handler>##tarfile infile [altname] to add to tarfile##" : {
        	"$" : "+"
        },
        "deltar<deltar_handler>##tarfile delfile to delete file##" : {
        	"$" : "+"
        },
        "detachrun<detachrun_handler>##cmds ... to run##" : {
        	"$" : "+"
        }

    }
    '''
    parser = extargsparse.ExtArgsParse()
    set_logging_args(parser)
    parser.load_command_line_string(commandline)
    parser.parse_command_line(None,parser)
    raise Exception('can not here for no command handle')
    return


if __name__ == '__main__':
    main()
