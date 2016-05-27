#!/usr/bin/python

import sys
def main():
	for a in sys.argv[1:]:
		val = eval(a)
		print('%s (%s)'%(a,val))

main()