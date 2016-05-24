#!/usr/bin/python

################################################
##  this file is for tce handle in python module
##
################################################
import re
import os
import sys
import argparse
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import dbgexp
import cmdpack


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

	def KEYWORD():
		return 'tce_'


CONST = _Const()

class TceBase(object):
	def __init__(self):
		return

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

