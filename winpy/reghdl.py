#! /usr/bin/env python

import extargsparse
import difflib
import re
import logging
import sys


def set_log_level(args):
    loglvl= logging.ERROR
    if args.verbose >= 3:
        loglvl = logging.DEBUG
    elif args.verbose >= 2:
        loglvl = logging.INFO
    elif args.verbose >= 1 :
        loglvl = logging.WARN
    # we delete old handlers ,and set new handler
    if logging.root is not None and logging.root.handlers is not None and len(logging.root.handlers) > 0:
    	logging.root.handlers = []
    logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
    return

GL_MAP_FILES='mapfiles'
GL_MAP_CONTS='contents'
GL_MAP_LINES='lines'
GL_LEFT_LEAF='left'
GL_RIGHT_LEAF='right'

def get_file_lines(infile=None):
	fin = sys.stdin
	if infile is not None:
		fin = open(infile, 'r+b')
	rlines = []
	bcode = fin.read()
	bcode = bcode[2:]
	if sys.version[0] == '3':
		s = bcode.decode('utf-16')
	else:
		s = str(bcode)
	rlines = re.split('\n', s)

	if fin != sys.stdin:
		fin.close()
	fin = None
	return rlines


def get_reg_maps(infile=None):
	global GL_MAP_FILES
	global GL_MAP_CONTS
	global GL_MAP_LINES
	regk = None
	regv = []
	regl = 0
	kl = 0
	rdict = dict()
	rdict[GL_MAP_FILES] = infile
	matchexpr = re.compile('^\[([^\]]+)\]$')
	rlines = get_file_lines(infile)
	for l in rlines:
		regl += 1
		l = l.rstrip('\r\n')
		if len(l) == 0:
			continue
		m = matchexpr.findall(l)
		if m is not None and len(m) > 0:
			if regk is not None:
				rdict[regk] = dict()
				rdict[regk][GL_MAP_CONTS] = regv
				rdict[regk][GL_MAP_LINES] = kl
				logging.info('kl [%d]'%(kl))
			regk = m[0]
			regv = []
			kl = regl
		else:
			if regk is not None:
				regv.append(l)

	if regk is not None:
		rdict[regk] = dict()
		rdict[regk][GL_MAP_CONTS] = regv
		rdict[regk][GL_MAP_LINES] = kl
		logging.info('kl [%d]'%(kl))
		regk = None
		regv = []
		kl = 0
	return rdict
		
def get_key_sorted(rdict):
	ks = []
	for k in rdict.keys():
		ks.append(k)
	return sorted(ks)

def get_diff(adict,bdict):
	global GL_LEFT_LEAF
	global GL_RIGHT_LEAF
	global GL_MAP_CONTS
	global GL_MAP_CONTS
	akeys = get_key_sorted(adict)
	bkeys = get_key_sorted(bdict)
	ai = 0
	bi = 0
	diffdict = dict()
	diffdict[GL_LEFT_LEAF] = dict()
	diffdict[GL_RIGHT_LEAF] = dict()
	diffdict[GL_LEFT_LEAF][GL_MAP_FILES] = adict[GL_MAP_FILES]
	diffdict[GL_RIGHT_LEAF][GL_MAP_FILES] = bdict[GL_MAP_FILES]
	while True:
		if ai >= len(akeys) and bi >= len(bkeys):
			break
		while bi < len(bkeys) and akeys[ai] > bkeys[bi]:
			diffdict[GL_RIGHT_LEAF][bkeys[bi]] = bdict[bkeys[bi]]
			bi += 1

		while ai < len(akeys) and bkeys[bi] > akeys[ai]:
			diffdict[GL_LEFT_LEAF][akeys[ai]] = adict[akeys[ai]]
			ai += 1

		if ai < len(akeys) and bi < len(bkeys) and \
			akeys[ai] == bkeys[bi] :
			if akeys[ai] != GL_MAP_FILES:
				alines = adict[akeys[ai]][GL_MAP_CONTS]
				blines = bdict[bkeys[bi]][GL_MAP_CONTS]
				logging.info('alines[%d][%s] blines[%d][%s]'%(len(alines), type(alines), len(blines), type(blines)))
				if len(alines) != len(blines):
					diffdict[GL_LEFT_LEAF][akeys[ai]] = adict[akeys[ai]]
					diffdict[GL_RIGHT_LEAF][bkeys[bi]] = bdict[bkeys[bi]]
				else:
					diffone = False
					aj = 0
					while aj < len(alines):
						logging.info('aj [%d]'%(aj))
						if alines[aj] != blines[aj]:
							diffone = True
							break
						aj += 1
					if diffone:
						diffdict[GL_LEFT_LEAF][akeys[ai]] = adict[akeys[ai]]
						diffdict[GL_RIGHT_LEAF][bkeys[bi]] = bdict[bkeys[bi]]
			ai += 1
			bi += 1
	return diffdict

def format_tab_line(tabs,l,stch=''):
	s = stch
	i = 0
	while i < tabs:
		s += '    '
		i += 1
	s += l
	s += '\n'
	return s

def format_lines(stch,tabs,lines):
	s = ''
	for l in lines:
		s += format_tab_line(tabs,l,stch)
	return s

def contents_handler(args,parser):
	set_log_level(args)
	afile = args.subnargs[0]
	bfile = args.subnargs[1]
	adict = get_reg_maps(afile)
	bdict = get_reg_maps(bfile)
	diffdict = get_diff(adict,bdict)

	akeys = get_key_sorted(diffdict[GL_LEFT_LEAF])
	bkeys = get_key_sorted(diffdict[GL_RIGHT_LEAF])
	diffs = ''

	ai = 0
	bi = 0
	while True:
		if ai >= len(akeys) and bi >= len(bkeys):
			break

		while bi < len(bkeys) and akeys[ai] > bkeys[bi]:
			if bkeys[bi] != GL_MAP_FILES:
				diffs += format_tab_line(8,'[%s].[%s]'%(bkeys[bi],diffdict[GL_RIGHT_LEAF][bkeys[bi]][GL_MAP_LINES]),' ')
				diffs += format_lines('+',8,diffdict[GL_RIGHT_LEAF][bkeys[bi]][GL_MAP_CONTS])
			bi += 1

		while ai < len(akeys) and akeys[ai] < bkeys[bi]:
			if akeys[ai] != GL_MAP_FILES:
				diffs += format_tab_line(0,'[%s].[%s]'%(akeys[ai], diffdict[GL_LEFT_LEAF][akeys[ai]][GL_MAP_LINES]), ' ')
				diffs += format_lines('-',0,diffdict[GL_LEFT_LEAF][akeys[ai]][GL_MAP_CONTS])
			ai += 1

		if ai < len(akeys) and bi < len(bkeys) and \
			akeys[ai] == bkeys[bi]:
			if akeys[ai] != GL_MAP_FILES:
				for l in difflib.unified_diff(diffdict[GL_LEFT_LEAF][akeys[ai]][GL_MAP_CONTS], diffdict[GL_RIGHT_LEAF][bkeys[bi]][GL_MAP_CONTS], fromfile='%s.[%d]'%(akeys[ai],diffdict[GL_LEFT_LEAF][akeys[ai]][GL_MAP_LINES]),tofile='%s.[%d]'%(bkeys[bi],diffdict[GL_RIGHT_LEAF][bkeys[bi]][GL_MAP_LINES])):
					diffs += '%s\n'%(l)
			ai += 1
			bi += 1
	sys.stdout.write('%s'%(diffs))
	sys.exit(0)
	return


def keys_handler(args,parser):
	set_log_level(args)
	afile = args.subnargs[0]
	bfile = args.subnargs[1]
	adict = get_reg_maps(afile)
	bdict = get_reg_maps(bfile)
	diffdict = get_diff(adict,bdict)

	akeys = get_key_sorted(diffdict[GL_LEFT_LEAF])
	bkeys = get_key_sorted(diffdict[GL_RIGHT_LEAF])
	diffs = ''

	ai = 0
	bi = 0
	while True:
		if ai >= len(akeys) and bi >= len(bkeys):
			break

		while bi < len(bkeys) and akeys[ai] > bkeys[bi]:
			if bkeys[bi] != GL_MAP_FILES:
				diffs += format_tab_line(8,'[%s].[%s]'%(bkeys[bi],diffdict[GL_RIGHT_LEAF][bkeys[bi]][GL_MAP_LINES]),' ')
			bi += 1

		while ai < len(akeys) and akeys[ai] < bkeys[bi]:
			if akeys[ai] != GL_MAP_FILES:
				diffs += format_tab_line(0,'[%s].[%s]'%(akeys[ai], diffdict[GL_LEFT_LEAF][akeys[ai]][GL_MAP_LINES]), ' ')
			ai += 1

		if ai < len(akeys) and bi < len(bkeys) and \
			akeys[ai] == bkeys[bi]:
			if akeys[ai] != GL_MAP_FILES:
				diffs += format_tab_line(0,'[%s].[%d] => [%s].[%d]'%(akeys[ai], diffdict[GL_LEFT_LEAF][akeys[ai]][GL_MAP_LINES],\
						bkeys[bi],diffdict[GL_RIGHT_LEAF][bkeys[bi]][GL_MAP_LINES]))
			ai += 1
			bi += 1
	sys.stdout.write('%s'%(diffs))
	sys.exit(0)
	return

def main():
	cmdline='''
	{
		"verbose|v" : "+",
		"keys<keys_handler>" : {
			"$" : 2
		},
		"contents<contents_handler>" : {
			"$" : 2
		}
	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(cmdline)
	args = parser.parse_command_line(None,parser)
	raise Exception('can not handle [%s]'%(args))
	return

if __name__ == '__main__':
	main()

