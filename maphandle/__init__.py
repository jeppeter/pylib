#!/usr/bin/python
import sys

def form_map_list(depmap,pkg):
	retlist = []
	curpkg = pkg
	if curpkg in depmap.keys():
		retlist.extend(depmap[pkg])
	slen = len(retlist)
	while True:
		for p in retlist:
			if p in depmap.keys():
				for cp in depmap[p]:
					if cp not in retlist:
						retlist.append(cp)
		clen = len(retlist)
		if clen == slen:
			break
		slen = clen
	return retlist


def __format_output_max(pkgs,getpkgs,outstr,pmax,gmax,pout=sys.stdout):
	s = ''
	i = 0
	j = 0
	for p in pkgs:
		if (i % 5)==0:			
			if i != 0:
				j += 1
			i = 0
			s += '\n'
		if i != 0 :
			s += ','
		s += '%-*s'%(pmax,p)
		i += 1
	s += '\n'
	i = 0
	j = 0
	s += '%s (%d)'%(outstr,len(getpkgs))
	for p in getpkgs:
		if (i % 5)==0:			
			if i != 0:
				j += 1
			i = 0
			s += '\n'
		if i != 0 :
			s += ','
		s += '%-*s'%(gmax,p)
		i += 1
	s += '\n'
	pout.write(s)

def format_output(pkgs,getpkgs,outstr,pout=sys.stdout):
	s = ''
	i = 0
	j = 0
	pmax = 0
	gmax = 0
	for p in pkgs:
		if len(p) > pmax:
			pmax = len(p)

	for p in getpkgs:
		if len(p) > gmax:
			gmax = len(p)
	__format_output_max(pkgs,getpkgs,outstr,pmax,gmax,pout)
	return


def output_map(pkgs,maps,outstr,pout=sys.stdout):
	s = ''
	i = 0
	j = 0
	pmax = 0
	gmax = 0
	alldeps = []
	outputdeps = []
	curdeps = []
	for p in pkgs:
		if len(p) > pmax:
			pmax = len(p)
		curdeps = form_map_list(maps,p)
		for cp in curdeps:
			if cp not in alldeps:
				if len(cp) > gmax:
					gmax = len(cp)
				alldeps.append(cp)
	slen = len(alldeps)
	while True:
		for p in alldeps:
			curdeps = form_map_list(maps,p)
			for cp in curdeps:
				if cp not in alldeps:
					if len(cp) > gmax:
						gmax = len(cp)
					alldeps.append(cp)
		clen = len(alldeps)
		if clen == slen:
			break
	outdeps = []
	for p in pkgs:
		if p not in maps.keys():
			continue
		__format_output_max([p],maps[p],'%s %s'%(p,outstr),pmax,gmax,pout)
		if p not in outdeps:
			outdeps.append(p)

	for p in alldeps:
		if p in outdeps:
			continue
		if p not in maps.keys():
			continue
		__format_output_max([p],maps[p],'%s %s'%(p,outstr),pmax,gmax,pout)
		if p not in outdeps:
			outdeps.append(p)
	return
