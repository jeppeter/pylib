#!/usr/bin/python
import re

import json


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


            

def singleton(class_):
  instances = {}
  def getinstance(*args, **kwargs):
    if class_ not in instances:
        instances[class_] = class_(*args, **kwargs)
    return instances[class_]
  return getinstance

@singleton
class ConstantClass(ConstantClassBase):
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
				setattr(self,p,getattr(args,p.upper()))
		return


def add_dpkg_args(parser):
	parser.add_argument('-v','--verbose',default=0,action='count')
	parser.add_argument('-r','--root',dest='%sroot'%(CONST.KEYWORD()),default=None,action='store',help='root of dpkg specified default (%s)'%(getattr(CONST,('%sroot'%(CONST.KEYWORD())).upper())))
	parser.add_argument('-c','--cat',dest='%scat'%(CONST.KEYWORD()),default=None,action='store',help='cat specified default(%s)'%(getattr(CONST,('%scat'%(CONST.KEYWORD())).upper())))
	parser.add_argument('-C','--chroot',dest='%schroot'%(CONST.KEYWORD()),default=None,action='store',help='chroot specified default (%s)'%(getattr(CONST,('%schroot'%(CONST.KEYWORD())).upper())))
	parser.add_argument('-t','--try',dest='%strymode'%(CONST.KEYWORD()),default=None,action='store_true',help='try mode default (%s)'%(getattr(CONST,('%strymode'%(CONST.KEYWORD())).upper())))
	parser.add_argument('-m','--mount',dest='%smount'%(CONST.KEYWORD()),default=None,action='store',help='mount specified default (%s)'%(getattr(CONST,('%smount'%(CONST.KEYWORD())).upper())))
	parser.add_argument('-u','--umount',dest='%sumount'%(CONST.KEYWORD()),default=None,action='store',help='umount specified default (%s)'%(getattr(CONST,('%sumount'%(CONST.KEYWORD())).upper())))
	parser.add_argument('--chown',dest='%schown'%(CONST.KEYWORD()),default=None,action='store',help='chown specified default (%s)'%(getattr(CONST,('%schown'%(CONST.KEYWORD())).upper())))
	parser.add_argument('--chmod',dest='%schmod'%(CONST.KEYWORD()),default=None,action='store',help='chmod specified default (%s)'%(getattr(CONST,('%schmod'%(CONST.KEYWORD())).upper())))
	parser.add_argument('--rm',dest='%srm'%(CONST.KEYWORD()),default=None,action='store',help='rm specified default(%s)'%(getattr(CONST,('%srm'%(CONST.KEYWORD())).upper())))
	parser.add_argument('--sudo',dest='%ssudoprefix'%(CONST.KEYWORD()),default=None,action='store',help='sudo specified default(%s)'%(getattr(CONST,('%ssudoprefix'%(CONST.KEYWORD())).upper())))
	parser.add_argument('-j','--json',dest='%sjsonfile'%(CONST.KEYWORD()),default=None,action='store',help='to make json file as input args default(%s)'%(getattr(CONST,('%sjsonfile'%(CONST.KEYWORD())).upper())))
	return parser


def load_dpkg_jsonfile(args):
	if args.dpkg_jsonfile is None:
		# now we should get all the default
		for p in dir(CONST):
			if p.startswith(CONST.KEYWORD().upper()):
				if getattr(args,p.lower()) is None:
					setattr(args,p.lower(),getattr(CONST,p))
		return args

	# it will parse the files
	keywords = []
	for p in dir(CONST):
		if p.lower().startswith(CONST.KEYWORD()):
			curkey = p.lower().replace(CONST.KEYWORD(),'')
			if curkey not in keywords:
				keywords.append(curkey)
	with open(args.tce_jsonfile,'r') as f:
		tcejson = json.load(f)
		for p in tcejson.keys():
			if p in keywords:
				tcekeyword = '%s%s'%(CONST.KEYWORD(),p)
				if getattr(args,tcekeyword) is None:
					setattr(args,tcekeyword,tcejson[p])
		for p in dir(CONST):
			if p.startswith(CONST.KEYWORD().upper()):
				if getattr(args,p.lower()) is None:
					setattr(args,p.lower(),getattr(CONST,p))
	return args

