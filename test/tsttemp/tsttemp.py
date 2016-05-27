#!/usr/bin/python

import sys
import os
import tempfile
import json

def main():
	fd,fname = tempfile.mkstemp(suffix='.json',prefix='parse',dir=None,text=True)
	os.close(fd)
	print('fname %s'%(fname))
	with open(fname,'w+') as f:
		f.write('{"hello":"good"}\n')
	with open(fname,'r+') as f:
		d = json.load(f)
		print('%s json %s'%(fname,d))
	os.remove(fname)
	return

if __name__ == '__main__':
	main()