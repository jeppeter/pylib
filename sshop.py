#! /usr/bin/env python

import paramiko
import extargsparse
import logging
import os
import sys
import threading
import traceback
import re
import time


sys.path.append(os.path.abspath(__file__))
import loglib

class SshScan(threading.Thread):
	def __init__(self,ip,user,password,timeout=3.0):
		threading.Thread.__init__(self)
		self.ip = ip
		self.user = user
		self.password = password
		self.exitcode = None
		self.timeout = timeout
		return

	def run(self):
		self.exitcode = None
		exitval = -1
		client = None
		try:
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.client.WarningPolicy())
			client.connect(hostname=self.ip,username=self.user,password=self.password,timeout=self.timeout)
			logging.info('run [%s:%s@%s] succ'%(self.user,self.password,self.ip))
			exitval = 0
		except:
			logging.info('run [%s:%s@%s] error\n%s'%(self.user,self.password,self.ip,traceback.format_exc()))
		if client is not None:
			client.close()
		self.exitcode = exitval
		return

def get_ip_u32(ip):
	sarr = re.split('\\.',ip)
	if len(sarr) < 4:
		raise Exception('not valid ipv4 [%s]'%(ip))
	retu32 = 0
	idx = 0
	while idx < 4:
		iv = int(sarr[idx]) & 0xff
		retu32 += (iv << ((4 - idx - 1)*8))
		idx += 1
	return retu32

def get_mask_u32(maskbits):
	retu32 = 0xffffffff
	mask32 = (1 << (32-maskbits)) - 1
	return (retu32 - mask32)

def u32_to_ip(u32val):
	retip = ''
	idx = 0
	while idx < 4:
		val = (u32val >> ((3-idx)*8)) & 0xff
		if len(retip)>0:
			retip += '.'
		retip += '%d'%(val)
		idx += 1
	return retip

def split_ips(ip):
	retips = []
	sarr = re.split('/',ip)
	if len(sarr) <= 1:
		retips.append(ip)
	else:
		maskbits = int(sarr[1])
		startip32 = get_ip_u32(sarr[0])
		mask32 = get_mask_u32(maskbits)
		# now to give the start
		startip = (startip32 & mask32)
		curip = startip
		curip += 1
		while True:
			if (curip & mask32) != startip:
				break
			retips.append(u32_to_ip(curip))
			curip += 1
	return retips


def scanssh_handler(args,parser):
	loglib.set_logging(args)
	ips = []
	for ip in args.subnargs:
		ips.extend(split_ips(ip))

	handleips = []
	succips = []
	hdlcnt = 0

	while True:
		try:
			if len(handleips) == 0 and len(ips) == 0:
				break
			while len(handleips) < args.maxthreads or args.maxthreads == 0:
				if len(ips) == 0:
					break
				curip = ips[0]
				ips = ips[1:]
				curssh = SshScan(curip,args.user,args.password,args.timeout)
				curssh.start()
				handleips.append(curssh)

			idx = 0
			popped = False
			while idx < len(handleips):
				if handleips[idx].exitcode is not None:
					if handleips[idx].exitcode == 0:
						succips.append(handleips[idx].ip)
					else:
						logging.info('%s failed'%(handleips[idx].ip))
					handleips.pop(idx)
					logging.info('handleips %d'%(len(handleips)))
					popped = True
					hdlcnt += 1
					if (hdlcnt % 100) == 0 and args.verbose == 0:
						sys.stdout.write('\n')
					if (hdlcnt % 10) == 0 and args.verbose == 0:
						sys.stdout.write('.')
						sys.stdout.flush()
					break
				idx += 1
			if not popped:
				logging.info('handleips %d'%(len(handleips)))
				time.sleep(1.0)
		except KeyboardInterrupt:
			break
	if args.verbose == 0:
		sys.stdout.write('\n')
	sys.stdout.write('succips [%d]'%(len(succips)))
	idx = 0
	while idx < len(succips):
		if (idx % 5) == 0:
			sys.stdout.write('\n    ')
		sys.stdout.write(' %s'%(succips[idx]))
		idx += 1
	sys.stdout.write('\n')
	sys.exit(0)
	return


def main():
    commandline='''
    {
        "input|i" : null,
        "output|o" : null,
        "user" : null,
        "password" : null,
        "maxthreads" : 10,
        "timeout": 5.0,
        "scanssh<scanssh_handler>##ip[/netbit] ... to scan ssh##" : {
        	"$" : "+"
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    loglib.load_log_commandline(parser)
    parser.parse_command_line(None,parser)
    raise Exception('can not reach here')
    return

if __name__ == '__main__':
    main()

