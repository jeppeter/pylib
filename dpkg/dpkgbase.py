#!/usr/bin/python
import re
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import const
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
	'+dpkg' : dpkg_const_keywords
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

CONST = ConstantClass('dpkg_',dpkg_const_keywords)

class DpkgBase(object):
	def __init__(self):
		return

	def strip_line(self,l):
		l = l.rstrip(' \t')
		l = l.rstrip('\r\n')
		l = l.strip(' \t')
		return l

	def set_dpkg_default(self):
		for p in dir(CONST):
			if p.lower().startswith(CONST.KEYWORD()):
				setattr(self,p.lower(),getattr(CONST,p.upper()))
		return

	def resub(self,l):
		newl = re.sub('\([^\(\)]*\)','',l)
		newl = re.sub('[\s]+','',newl)
		newl = re.sub(':([^\s:,]+)','',newl)
		return newl


	def set_dpkg_attrs(self,args):
		# first to set the default value
		self.set_dpkg_default()
		for p in dir(args):
			if p.lower().startswith(CONST.KEYWORD()):
				setattr(self,p,getattr(args,p.lower()))
		return



def add_dpkg_args(parser):
	if not isinstance(parser,extargsparse.ExtArgsParse):
		raise Exception('%s not subclass of extargsparse.ExtArgsParse'%(parser))
	parser.add_argument('-v','--verbose',default=0,action='count')
	parser.add_args_dict('dpkg_',dpkg_const_keywords)
	return parser


def load_dpkg_jsonfile(args):
	return extargsparse.load_json_args(args,CONST)

