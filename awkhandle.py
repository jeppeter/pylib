#! /usr/bin/python


import extargsparse
import re
import sys
import logging

def set_logging(args):
	loglvl= logging.ERROR
	if args.verbose >= 3:
		loglvl = logging.DEBUG
	elif args.verbose >= 2:
		loglvl = logging.INFO
	logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
	return

def pack_awk(fin):
	s = ''
	for l in fin:
		l = re.sub('\r','',l)
		l = re.sub('\n','',l)
		l = re.sub(' ','',l)
		l = re.sub('\t','',l)
		s += l
	return s


def unpack_awk(fin):
	s = ''
	tabs = 0
	packs = pack_awk(fin)
	idx = 0
	startline = 1
	while idx < len(packs):
		c = packs[idx]
		idx += 1
		if c == ' ' or c == '\t':
			continue
		if startline and c != '}':
			startline = 0
			s += ' ' * tabs
			logging.info('(%d)[%s:](%s)'%(tabs,idx,packs[idx:]))
		if c != '}':
			s += c
		if c == ';':
			tmpc = None
			elseclause=False
			rightbracket=False
			logging.info('(%d)[%s:](%s)(%s)'%(tabs,idx,packs[idx:],s))
			if idx < len(packs):
				tmpc = packs[idx]
				if tmpc == '}':
					rightbracket = True
				if packs[idx:].startswith('}else{'):
					elseclause = True
				if rightbracket :
					tabs -= 4
				s += '\n'
				startline = 1
				if rightbracket and not elseclause:
					if startline :
						startline = 0
						s += ' ' * tabs
					s += '}'
					s += '\n'
					startline = 1
					idx += 1
				elif elseclause:
					if startline :
						startline = 0
						s += ' ' * tabs
					s += '} else {'
					idx += 7
					s += '\n'
					startline = 1
					tabs += 4
			else:
				s += '\n'
				startline = 1

		elif c == '{':
			s += '\n'
			tabs += 4
			startline = 1
		elif c == '}':
			logging.info('(%d)[%d:](%s)(%s)'%(tabs,idx,packs[idx:],s))
			if packs[idx:].startswith('else{'):
				tabs -= 4
				if startline : 
					s += ' ' * tabs
					startline = 0					
				s += '} else {'
				s += '\n'
				tabs += 4
				startline = 1
				idx += 5				
				continue
			else:
				tabs -= 4
				if startline:
					s += ' ' * tabs
					startline = 0
				s += '}'
				s += '\n'
				startline = 1
				while idx < len(packs):
					logging.info('(%d)[%d:](%s)(%s)'%(tabs,idx,packs[idx:],s))
					if packs[idx:].startswith('}else{'):
						if startline:
							s += ' ' * tabs
							startline = 0
						idx += 5
						s += ' else {'
						s += '\n'
						startline = 1
					elif packs[idx:].startswith('}'):
						logging.info('[%d:](%s)'%(idx,packs[idx:]))
						tabs -= 4
						if startline:
							s += ' ' * tabs
							startline = 0
						idx += 1
						s += '}'
						s += '\n'
						startline = 1
					else:
						break
				startline = 1


	assert(tabs == 0)
	return s


def unpack_handler(args,parser):
	set_logging(args)
	fin = sys.stdin
	fout = sys.stdout
	outs = ''
	fin = sys.stdin
	fout = sys.stdout
	if args.input is not None:
		fin = open(args.input,'r+')
	if args.output is not None:
		fout = open(args.output,'w+')
	outs = unpack_awk(fin)
	fout.write('%s'%(outs))
	if fout != sys.stdout:
		fout.close()
	if fin != sys.stdin:
		fin.close()
	sys.exit(0)
	return

def pack_handler(args,parser):
	set_logging(args)
	outs = ''
	fin = sys.stdin
	fout = sys.stdout
	if args.input is not None:
		fin = open(args.input,'r+')
	if args.output is not None:
		fout = open(args.output,'w+')
	outs = pack_awk(fin)
	fout.write('%s'%(outs))
	if fout != sys.stdout:
		fout.close()
	if fin != sys.stdin:
		fin.close()
	sys.exit(0)
	return



command_line = {
	'input|i' : None,
	'verbose|v' : '+',
	'output|o' : None,
	'pack<pack_handler>' : {
		'$' : 0
	},
	'unpack<unpack_handler>' : {
		'$' : 0
	}
}

def main():
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line(command_line)
	parser.parse_command_line(None,parser)
	return

if __name__ == '__main__':
	main()	