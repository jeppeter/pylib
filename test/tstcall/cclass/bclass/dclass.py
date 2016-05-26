#!/usr/bin/python

import traceback

def CallA(name):
	funcname = traceback.extract_stack(None, 1)[0][2]
	print ('%s->%s %s'%(__name__,funcname,name))

def CallB(name):
	funcname = traceback.extract_stack(None, 1)[0][2]
	print ('%s->%s %s'%(__name__,funcname,name))
