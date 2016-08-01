#!python

import sys
import re
import extargsparse

def binary_dump(infile,outfile):
	fin = sys.stdin
	if infile is not None:
		fin = open(infile,'r')

	fout = sys.stdout
	if outfile is not None:
		fout = open(outfile,'r+b')
	s = b''

	getexpr = re.compile('0x([0-9a-fA-F]+)\s((0x([0-9a-fA-F]+)\s?)+)')

	for l in fin:
		l = l.rstrip('\r\n')
		l = l.rstrip(' \t')
		l = l.strip(' \t')
		m = getexpr.findall(l)
		if m is not None and len(m) >= 0 and len(m[0]) >= 2:
			l = m[0][1]
			sarr = re.split('\s+',l)
			if len(sarr) >= 1:
				for b in sarr:
					s += chr(int(b,16))
	fout.write(s)
	if fout != sys.stdout:
		fout.close()
	fout = None

	if fin != sys.stdin:
		fin.close()
	fin = None
	return

def main():
	binary_dump(None,None)
	return

main()