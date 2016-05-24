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
	'optional_dir' : '/cde/optional',
	'trymode' : False,
	'platform' : 'x86_64',
	'mount' : 'mount',
	'umount' : 'umount',
	'chroot' : 'chroot',
	'chown' : 'chown',
	'chmod' : 'chmod',
	'jsonfile' : None,
	'perspace' : 3 ,
	'depmapfile' : None
}


def singleton(class_):
  instances = {}
  def getinstance(*args, **kwargs):
    if class_ not in instances:
        instances[class_] = class_(*args, **kwargs)
    return instances[class_]
  return getinstance

@singleton
class ConstantClass(const.ConstantClassBase):
  pass

CONST = ConstantClass('tce_',tce_const_keywords)


class TceBase(object):
	def __init__(self):
		return

	def strip_line(self,l):
		l = l.rstrip(' \t')
		l = l.rstrip('\r\n')
		l = l.strip(' \t')
		return l

	def set_tce_default(self):
		for p in dir(CONST):
			if p.lower().startswith(CONST.KEYWORD()):
				setattr(self,p.lower(),getattr(CONST,p.upper()))
		return

	def set_tce_attrs(self,args):
		# first to set the default value
		self.set_tce_default()
		for p in dir(args):
			if p.lower().startswith(CONST.KEYWORD()):
				setattr(self,p,getattr(args,p.lower()))
		return


def add_tce_args(parser):
	if not isinstance(parser,extargsparse.ExtArgsParse):
		raise Exception('%s not subclass of extargsparse.ExtArgsParse'%(parser))
	parser.add_argument('-v','--verbose',default=0,action='count')
	parser.add_args_dict('tce_',tce_const_keywords)
	return parser


def load_tce_jsonfile(args):
	retargs = extargsparse.load_json_args(args,CONST)
	retargs.tce_mirror = retargs.tce_mirror.rstrip('/')
	retargs.tce_optional_dir = retargs.tce_optional_dir.rstrip('/')
	return retargs
