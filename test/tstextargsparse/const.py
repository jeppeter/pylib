#!/usr/bin/python

import os
import sys
import extargsparse


def set_attr(self,args,prefix=''):
	for p in vars(args).keys():
		if len(prefix) == 0 or p.startswith('%s_'%(prefix)):
			setattr(self,p,getattr(args,p))
	return

class EnvBase(object):
	def __init__(self,args):
		set_attr(self,args,'dpkg')
		return

	def print_key(self):
		for k in self.__dict__.keys():
			print('%s = %s'%(k,self.__dict__[k]))
		return

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
	'+dpkg' : dpkg_const_keywords
}


def main():
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line(dpkg_command_line)
	args = parser.parse_command_line()
	envbase = EnvBase(args)
	envbase.print_key()
	return

if __name__ == '__main__':
	main()