#! /usr/bin/env python

import string

def debug_str(instr,prefix=None,indexoff=True,printableout=True):
	i = 0
	if prefix is not None:
		rets = prefix
	else:
		rets = 'instr[%d]'%(len(instr))
	lasti = i
	while i < len(instr):
		c = ord(instr[i])
		if (i % 16) == 0:
			if i > 0:
				if printableout:
					rets += '    '
					while lasti < i:
						if instr[lasti] in string.printable:
							rets += instr[lasti]
						else:
							rets += '.'
						lasti = lasti + 1
				else:
					lasti = i
			if len(rets) > 0:
				rets += '\n'
			if indexoff:
				rets += '0x%08x'%(i)
		rets += ' 0x%02x'%(c)
		i = i + 1
	if i != lasti:
		k = i
		while (k % 16) != 0:
			rets += '     '
			k = k + 1
		if printableout:
			rets += '    '
			while lasti < i:
				if instr[lasti] in string.printable:
					rets += instr[lasti]
				else:
					rets += '.'
				lasti = lasti + 1
		else:
			lasti = i
		if len(rets) > 0:
			rets += '\n'
	return rets
