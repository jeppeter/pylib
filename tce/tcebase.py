#!/usr/bin/python

################################################
##  this file is for tce handle in python module
##
################################################
import re
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import const
import extargsparse

tce_const_keywords = {
	'mirror' : 'http://repo.tinycorelinux.net',
	'root' : '/',
	'tceversion': '7.x',
	'wget' : 'wget',
	'cat' : 'cat',
	'rm' : 'rm',
	'sudoprefix' : 'sudo',
	'optional_dir' : '/cde',
	'trymode' : False,
	'platform' : 'x86_64',
	'mount' : 'mount',
	'umount' : 'umount',
	'chroot' : 'chroot',
	'chown' : 'chown',
	'chmod' : 'chmod',
	'jsonfile' : None,
	'perspace' : 3 ,
	'depmapfile' : None,
	'timeout' : 10
}




class TceBase(object):
	def __init__(self):
		return

	def strip_line(self,l):
		l = l.rstrip(' \t')
		l = l.rstrip('\r\n')
		l = l.strip(' \t')
		return l


	def set_tce_attrs(self,args):
		# first to set the default value
		extargsparse.set_attr_args(self,args,'tce')
		return

tce_base_command_line = {
	'verbose|v' : '+',
	'+tce' : tce_const_keywords
}

def add_tce_args(parser):
	if not isinstance(parser,extargsparse.ExtArgsParse):
		raise Exception('%s not subclass of extargsparse.ExtArgsParse'%(parser))
	parser.load_command_line(tce_base_command_line)
	return parser


