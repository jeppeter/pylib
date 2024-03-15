#! /usr/bin/env python


import sys
import os
import re


def sort_and_uniq(sarr):
    retsarr = []
    idx = 0
    sarr.sort()
    if len(sarr) > 0:
        retsarr.append(sarr[0])

    idx = 1
    while idx < len(sarr):
        if retsarr[-1] != sarr[idx]:
            retsarr.append(sarr[idx])
        idx += 1
    return retsarr


def parse_input_sarr(ins):
	sarr = re.split('\n',ins)
	retval = []
	for l in sarr:
		l = l.rstrip('\r')
		if l.startswith('#') or len(l) == 0:
			continue
		carr = re.split('\\s+', l)
		for nk in carr:
			if len(nk) > 0:
				retval.append(nk)
	return retval


class Maxsize:
    def __init__(self):
        self.maxsize = 0
        return

    def set_max_length(self,s):
        if len(s) > self.maxsize:
            self.maxsize = len(s)
        return


def format_output_sarr(sarr,maxnum):
	msize = Maxsize()
	for l in nlist:
		msize.set_max_length(l)

	indx = 0
	outs = ''
	for l in nlist:
		indx += 1
		if (indx % maxnum) == 1:
			outs += '%-*s'%(msize.maxsize,l)
		else:
			outs += ' %-*s'%(msize.maxsize,l)
		if (indx % maxnum) == 0:
			outs += '\n'
	return outs

