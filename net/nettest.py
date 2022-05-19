#! /usr/bin/env


import extargsparse
import logging
import sys
import socket
import re
import cmdpack

def read_file(infile=None):
	fin = sys.stdin
	if infile is not None:
		fin = open(infile,'rb')
	rets = ''
	for l in fin:
		s = l
		if 'b' in fin.mode:
			if sys.version[0] == '3':
				s = l.decode('utf-8')
		rets += s

	if fin != sys.stdin:
		fin.close()
	fin = None
	return rets


def set_logging(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	if logging.root is not None and len(logging.root.handlers) > 0:
		logging.root.handlers = []
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return

def connect_handler(args,parser):
	set_logging(args)
	socktype = socket.SOCK_STREAM
	if args.udpmode:
		socktype = socket.SOCK_DGRAM
	host = '127.0.0.1'
	port = 6200
	if len(args.subnargs) > 0:
		hoststr = args.subnargs[0]
		sarr = re.split(':',hoststr)
		host = sarr[0]
		if len(sarr) > 1:
			port = int(sarr[1])
	with socket.socket(socket.AF_INET,socktype) as s:
		s.connect((host,port))
		sys.stdout.write('connect [%s] succ\n'%(args.subnargs[0]))
	sys.exit(0)

def get_mac_addr(name=None):
	matchexpr = re.compile('^([\w]+)\s.*HWaddr\s+([a-f0-9A-F:]+)')
	cmds = ['ifconfig']
	if name is not None:
		cmds.append(name)
	for l in cmdpack.run_cmd_output(cmds):
		l = l.rstrip('\r\n')
		m = matchexpr.findall(l)
		if m is not None and len(m) > 0 and len(m[0]) > 1:
			if name is None or name == m[0][0]:
				return m[0][1]		
	return None


def is_nic_dhcp_mode(nicname,fname='/etc/network/interfaces'):
	s = read_file(fname)
	sarr = re.split('\n',s)
	matchexpr = re.compile('iface\\s+%s\\s+'%(nicname))
	staticexpr = re.compile('.*\\s+static\\s*$')
	for l in sarr:
		l = l.rstrip('\r\n')
		if matchexpr.match(l):
			if staticexpr.match(l):
				return False
			else:
				return True
	return False



def isdhcp_handler(args,parser):
	set_logging(args)
	nicname = args.subnargs[0]
	fname = args.subnargs[1]
	if is_nic_dhcp_mode(nicname,fname):
		sys.stdout.write('%s dhcp\n'%(nicname))
	else:
		sys.stdout.write('%s not dhcp\n'%(nicname))
	sys.exit(0)
	return

def getmac_handler(args,parser):
	set_logging(args)
	for n in args.subnargs:
		mac = get_mac_addr(n)
		sys.stdout.write('%s %s\n'%(n,mac))
	sys.exit(0)
	return

def get_mac_for_ip(n):
	cmds = ['arp',n]
	matchexpr = re.compile('^%s\\s+.*'%(n))
	macexpr = re.compile('\\s+(([0-9a-fA-F]+:){5}[0-9a-fA-F]+)\\s+')
	rets = ''
	for l in cmdpack.run_cmd_output(cmds):
		l = l.rstrip('\r\n')
		if matchexpr.match(l):
			m = macexpr.findall(l)
			if m is not None and len(m) > 0 and len(m[0]) > 1:
				rets = m[0][0]
	return rets

def getipmac_handler(args,parser):
	set_logging(args)
	for n in args.subnargs:
		mac = get_mac_for_ip(n)
		sys.stdout.write('%s %s\n'%(n,mac))
	sys.exit(0)
	return

def main():
	commandline='''
	{
		"verbose|v" : "+",
		"udpmode|U" : false,
		"connect<connect_handler>" : {
			"$" : "+"
		},
		"isdhcp<isdhcp_handler>## nicname fname to get ##" : {
			"$" : 2
		},
		"getmac<getmac_handler>## nicname ...##" : {
			"$" : "+"
		},
		"getipmac<getipmac_handler>##ip ... ##" : {
			"$" : "+"
		}
	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	parser.parse_command_line(None,parser)
	raise Exception('can not reach here')
	return

if __name__ == '__main__':
	main()