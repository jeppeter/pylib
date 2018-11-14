#! /usr/bin/env python

import extargsparse
import paramiko
import os
import logging
import sys
import time
import socket


def set_log_level(args):
    loglvl= logging.ERROR
    if args.verbose >= 3:
        loglvl = logging.DEBUG
    elif args.verbose >= 2:
        loglvl = logging.INFO
    elif args.verbose >= 1 :
        loglvl = logging.WARN
    # we delete old handlers ,and set new handler
    if logging.root is not None and logging.root.handlers is not None and len(logging.root.handlers) > 0:
    	logging.root.handlers = []
    logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
    return


def cmd_handler(args,parser):
	set_log_level(args)
	key = paramiko.RSAKey.from_private_key_file(args.privatekey)
	#client = paramiko.SSHClient(args.host,args.user,port=args.port,password=args.password,pkey=None)
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
	client.connect(args.host,port=args.port ,username=args.user,password=args.password,pkey=key)
	cmd = ''
	for c in args.subnargs:
		if len(cmd) > 0:
			cmd += ' '
		cmd += '%s'%(c)
	stdin, stdout,stderr = client.exec_command(cmd)
	#client.ssh(cmd,output=True)
	for l in stdout:
		sys.stdout.write('%s'%(l))
	sys.exit(0)
	return

def connect_sshcmd(args,cmd,timeout):
	starttime =time.time()
	endtime = starttime + timeout
	curtime = time.time()
	while curtime < endtime:
		try:
			key = paramiko.RSAKey.from_private_key_file(args.privatekey)
			#client = paramiko.SSHClient(args.host,args.user,port=args.port,password=args.password,pkey=None)
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
			logging.info('connect [%s:%s]'%(args.host,args.port))
			curtime = time.time()
			lefttime = endtime - curtime
			if lefttime > 3.0:
				lefttime = 3.0
			client.connect(args.host,port=args.port ,username=args.user,password=args.password,pkey=key,timeout=lefttime)
			logging.info('cmd [%s]'%(cmd))
			stdin,stdout,stderr = client.exec_command(cmd)
			for l in stdout:
				sys.stdout.write('%s'%(l))
			logging.info('close')
			client.close()
			return None
		except:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			if exc_type  == KeyboardInterrupt:
				sys.stderr.write('ctrl+c exit\n')
				return exc_type
			if exc_type != socket.timeout:
				sys.stderr.write('exc_type [%s] exc_obj [%s]\n'%(exc_type,exc_obj))
		curtime = time.time()
	raise Exception('connect [%s:%d] timeout [%s]'%(args.host,args.port,timeout))


def reboot_handler(args,parser):
	set_log_level(args)
	times = int(args.subnargs[0])
	timeout = int(args.subnargs[1])
	for i in range(times):
		try:
			retval = connect_sshcmd(args,'sudo reboot',timeout)
			if retval is not None:
				break
			# wait for handling in remote
			time.sleep(1.0)
		except:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			sys.stderr.write('exc_obj [%s] at [%d]\n'%(exc_obj, i))
			sys.exit(4)


	sys.exit(0)
	return

def main():
	commandline_fmt='''
	{
		"verbose|v" : "+",
		"host|H" : "127.0.0.1",
		"user|u" : "%s",
		"password|P" : "",
		"port|p" : 22,
		"input|i" : null,
		"output|o" : null,
		"stderr|e" : null,
		"privatekey|K" : null,
		"cmd<cmd_handler>" : {
			"$" : "+"
		},
		"reboot<reboot_handler>##times timeout... to reboot test for command##" : {
			"$" : 2
		}
	}
	'''
	if sys.platform == 'win32':
		commandline = commandline_fmt%(os.environ['USERNAME'])
	else:
		commandline = commandline_fmt%(os.environ['USER'])
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	args = parser.parse_command_line(None,parser)
	raise Exception('can not accept [%s]'%(args))
	return

if __name__ == '__main__':
	main()