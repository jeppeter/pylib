#!python

import sys

def split_in_out(infile,outfile):
	inf = sys.stdin
	if infile is not None:
		inf = open(infile,'r')

	outf = sys.stdout
	if outfile is not None:
		outf = open(outfile,'w')

	cnt = 0x10
	for l in inf:
		l = l.rstrip('\r\n')
		l = l.rstrip(' \t')
		l = l.strip(' \t')
		for i in range(0,len(l),2):
			if len(l) < (i+2):
				b = l[(i):]
			else:
				b = l[(i):(i+2)]
			if (cnt % 16) == 0:
				if cnt != 0:
					outf.write('\n')
				outf.write('0x%08x'%(cnt))
			outf.write(' 0x%2s'%(b))
			cnt += 1
	outf.write('\n')

	if inf != sys.stdin:
		inf.close()
	inf = None
	if outf != sys.stdout:
		outf.close()
	outf = None

def main():
	split_in_out(None,None)

main()