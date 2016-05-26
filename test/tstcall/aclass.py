#!/usr/bin/python

import traceback

def CallA():
	funcname = traceback.extract_stack(None, 1)[0][2]
	print ('%s.%s'%(__name__,funcname))

def CallB():
	funcname = traceback.extract_stack(None, 1)[0][2]
	print ('%s.%s'%(__name__,funcname))


	