#!/usr/bin/python
import re
import json
import os
import sys
import extargsparse


dpkg_const_keywords = {
	'root' : '/',
	'dpkg' : 'dpkg',
	'aptcache': 'apt-cache',
	'aptget' : 'apt-get',
	'cat' : 'cat',
	'rm' : 'rm',
	'sudoprefix' : 'sudo',
	'trymode' : False,
	'mount' : 'mount',
	'umount' : 'umount',
	'chroot' : 'chroot',
	'chown' : 'chown',
	'chmod' : 'chmod',
	'jsonfile' : None ,
	'rollback' : True,
	'reserved' : False
}

dpkg_command_line = {
	'verbose:v' : '+',
	'+dpkg' : dpkg_const_keywords
}



class DpkgBase(object):
	def __init__(self):
		return

	def strip_line(self,l):
		l = l.rstrip(' \t')
		l = l.rstrip('\r\n')
		l = l.strip(' \t')
		return l

	def resub(self,l):
		newl = re.sub('\([^\(\)]*\)','',l)
		newl = re.sub('[\s]+','',newl)
		newl = re.sub(':([^\s:,]+)','',newl)
		return newl


	def set_dpkg_attrs(self,args):
		# first to set the default value
		extargsparse.set_attr_args(self,args,'dpkg')
		return



def add_dpkg_args(parser):
	if not isinstance(parser,extargsparse.ExtArgsParse):
		raise Exception('%s not subclass of extargsparse.ExtArgsParse'%(parser))
	parser.load_command_line(dpkg_command_line)
	return parser



