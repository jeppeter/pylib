#!/usr/bin/python

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import packtest

def main():
	classb = packtest.call_b_new()
	classb2 = packtest.PackB()
	classa = packtest.call_a_new()
	classa2 = packtest.PackBase()

	if not issubclass(classb.__class__,classa.__class__):
		raise Exception('classb not subclass of classa')
	if not issubclass(classb2.__class__,classa2.__class__):
		raise Exception('classb2 not subclass of classa2')
	return

if __name__ == '__main__':
	main()