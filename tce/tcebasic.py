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
	def TCE_WGET():
		return 'wget'

	@constant
	def TCE_CAT():
		return 'cat'

	@constant
	def TCE_RM():
		return 'rm'



CONST = _Const()

class TceBase(object):
	def __init__(self):
		return

	def set_tce_attrs(self,args):
		# first to set the default value
		for 
		for p in dir(args):
			if p.startswith('tce_'):
				setattr(self,p,getattr(args,p))
		return

