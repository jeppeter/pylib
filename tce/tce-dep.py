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
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import dbgexp
import cmdpack
import tcebasic


class TceDepBase(tcebasic.TceBase):
	def __init__(self):
		self.__deps = []
		return

	def get_input(self,l):
		l = l.rstrip(' \t')
		l = l.rstrip('\r\n')
		l = l.strip(' \t')
		if len(l) > 0:
			if l not in self.__deps:
				self.__deps.append(l)
		return

	def get_depend(self):
		return self.__deps


def filter_context(instr,context):
	context.get_input(instr)
	return


class TceDep(TceDepBase):
	def __init__(self,args):
		super(TceDep,self).__init__()
		self.set_tce_attrs(args)
		return

