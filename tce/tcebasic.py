#!/usr/bin/python

################################################
##  this file is for tce handle in python module
##
################################################
import json


def constant(f):
    def fset(self, value):
        raise TypeError
    def fget(self):
        return f()
    return property(fget, fset)


class _Const(object):
	@constant
	def TCE_MIRROR():
		return 'http://repo.tinycorelinux.net/'
	@constant
	def TCE_ROOT():
		return '/'
	@constant
	def TCE_VERSION():
		return '7.x'
	@constant
	def TCE_WGET():
		return 'wget'
	@constant
	def TCE_CAT():
		return 'cat'
	@constant
	def TCE_RM():
		return 'rm'
	@constant
	def TCE_CURL():
		return 'curl'
	@constant
	def TCE_OPTION_DIR():
		return '/cde/optional/'
	@constant
	def TCE_SUDOPREFIX():
		return 'sudo'
	@constant
	def TCE_PLATFORM():
		return 'x86_64'
	@constant
	def TCE_TRYMODE():
		return False
	@constant
	def TCE_MOUNT():
		return 'mount'
	@constant
	def TCE_UMOUNT():
		return 'umount'
	@constant
	def TCE_CHROOT():
		return 'chroot'
	@constant
	def TCE_CHOWN():
		return 'chown'
	@constant
	def TCE_CHMOD():
		return 'chmod'
	@constant
	def TCE_JSONFILE():
		return None
	@constant
	def KEYWORD():
		return 'tce_'

CONST = _Const()

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
			if p.lower().startswith(CONST.KEYWORD):
				setattr(self,p.lower(),getattr(CONST,p.upper()))
		return

	def set_tce_attrs(self,args):
		# first to set the default value
		self.set_tce_default()
		for p in dir(args):
			if p.lower().startswith(CONST.KEYWORD):
				setattr(self,p,getattr(args,p.upper()))
		return


def add_tce_args(parser):
	parser.add_argument('-v','--verbose',default=0,action='count')
	parser.add_argument('-r','--root',dest='%sroot'%(CONST.KEYWORD),default=None,action='store',help='root of dpkg specified default (%s)'%(getattr(CONST,('%sroot'%(CONST.KEYWORD)).upper())))
	parser.add_argument('-M','--mirror',dest='%smirror'%(CONST.KEYWORD),default=None,action='store',help='mirror site default (%s)'%(getattr(CONST,('%smirror'%(CONST.KEYWORD)).upper())))
	parser.add_argument('-c','--cat',dest='%scat'%(CONST.KEYWORD),default=None,action='store',help='cat specified default(%s)'%(getattr(CONST,('%scat'%(CONST.KEYWORD)).upper())))
	parser.add_argument('-C','--chroot',dest='%schroot'%(CONST.KEYWORD),default=None,action='store',help='chroot specified default (%s)'%(getattr(CONST,('%schroot'%(CONST.KEYWORD)).upper())))
	parser.add_argument('-t','--try',dest='%strymode'%(CONST.KEYWORD),default=None,action='store_true',help='try mode default (%s)'%(getattr(CONST,('%strymode'%(CONST.KEYWORD)).upper())))
	parser.add_argument('-m','--mount',dest='%smount'%(CONST.KEYWORD),default=None,action='store',help='mount specified default (%s)'%(getattr(CONST,('%smount'%(CONST.KEYWORD)).upper())))
	parser.add_argument('-u','--umount',dest='%sumount'%(CONST.KEYWORD),default=None,action='store',help='umount specified default (%s)'%(getattr(CONST,('%sumount'%(CONST.KEYWORD)).upper())))
	parser.add_argument('--chown',dest='%schown'%(CONST.KEYWORD),default=None,action='store',help='chown specified default (%s)'%(getattr(CONST,('%schown'%(CONST.KEYWORD)).upper())))
	parser.add_argument('--chmod',dest='%schmod'%(CONST.KEYWORD),default=None,action='store',help='chmod specified default (%s)'%(getattr(CONST,('%schmod'%(CONST.KEYWORD)).upper())))
	parser.add_argument('--curl',dest='%scurl'%(CONST.KEYWORD),default=None,action='store',help='curl specified default(%s)'%(getattr(CONST,('%scurl'%(CONST.KEYWORD)).upper())))
	parser.add_argument('--optiondir',dest='%soption_dir'%(CONST.KEYWORD),default=None,action='store',help='option dir specified default(%s)'%(getattr(CONST,('%soption_dir'%(CONST.KEYWORD)).upper())))
	parser.add_argument('--platform',dest='%splatform'%(CONST.KEYWORD),default=None,action='store',help='platform specified default(%s)'%(getattr(CONST,('%splatform'%(CONST.KEYWORD)).upper())))
	parser.add_argument('--rm',dest='%srm'%(CONST.KEYWORD),default=None,action='store',help='rm specified default(%s)'%(getattr(CONST,('%srm'%(CONST.KEYWORD)).upper())))
	parser.add_argument('--sudo',dest='%ssudoprefix'%(CONST.KEYWORD),default=None,action='store',help='sudo specified default(%s)'%(getattr(CONST,('%ssudoprefix'%(CONST.KEYWORD)).upper())))
	parser.add_argument('--tceversion',dest='%sversion'%(CONST.KEYWORD),default=None,action='store',help='tce version specified default(%s)'%(getattr(CONST,('%sversion'%(CONST.KEYWORD)).upper())))
	parser.add_argument('--wget',dest='%swget'%(CONST.KEYWORD),default=None,action='store',help='wget specified default(%s)'%(getattr(CONST,('%swget'%(CONST.KEYWORD)).upper())))
	parser.add_argument('-j','--json',dest='%sjsonfile'%(CONST.KEYWORD),default=None,action='store',help='to make json file as input args default(%s)'%(getattr(CONST,('%sjsonfile'%(CONST.KEYWORD)).upper())))
	return parser


def load_tce_jsonfile(args):
	if args.tce_jsonfile is None:
		# now we should get all the default
		for p in dir(CONST):
			if p.startswith(CONST.KEYWORD.upper()):
				if getattr(args,p.lower()) is None:
					setattr(args,p.lower(),getattr(CONST,p))
		return args

	# it will parse the files
	keywords = []
	for p in dir(CONST):
		if p.lower().startswith(CONST.KEYWORD):
			curkey = p.lower().replace(CONST.KEYWORD,'')
			if curkey not in keywords:
				keywords.append(curkey)
	with open(args.tce_jsonfile,'r') as f:
		tcejson = json.load(f)
		for p in tcejson.keys():
			if p in keywords:
				tcekeyword = '%s%s'%(CONST.KEYWORD,p)
				if getattr(args,tcekeyword) is None:
					setattr(args,tcekeyword,tcejson[p])
		for p in dir(CONST):
			if p.startswith(CONST.KEYWORD.upper()):
				if getattr(args,p.lower()) is None:
					setattr(args,p.lower(),getattr(CONST,p))
	return args
