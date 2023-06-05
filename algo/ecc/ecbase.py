#! /usr/bin/env python

import json
import logging

A_PARAM = 'a'
B_PARAM = 'b'
ORDER_PARAM = 'order'
X_PARAM = 'x'
Y_PARAM = 'y'
P_PARAM = 'p'
M_PARAM = 'm'
L_PARAM = 'l'

class ECBase(object):
	def __init__(self,jsons=''):
		self.unpack()
		return

	def unpack(self,jsons):
		rdict = json.loads(jsons)
		if A_PARAM not in rdict.keys() or B_PARAM not in rdict.keys() or \
			ORDER_PARAM not in rdict.keys():
			raise Exception('no [%s] or [%s] or [%s] in jsons'%(A_PARAM,B_PARAM,ORDER_PARAM))
		if X_PARAM not in rdict.keys() or Y_PARAM not in rdict.keys():
			raise Exception('no [%s] or [%s] in jsons'%(X_PARAM,Y_PARAM))
		self.a = rdict[A_PARAM]
		self.b = rdict[B_PARAM]
		self.order = rdict[ORDER_PARAM]
		self.x = rdict[X_PARAM]
		self.y = rdict[Y_PARAM]
		return

	def pack(self):
		rdict = dict()
		rdict[A_PARAM] = self.a
		rdict[B_PARAM] = self.b
		rdict[ORDER_PARAM] = self.order
		rdict[X_PARAM] = self.x
		rdict[Y_PARAM] = self.y
		return json.dumps(rdict,indent=4)


	def __str__(self):
		return self.pack()

	def __repr__(self):
		return self.pack()


class BinaryField(object):
	def __init__(self,jsons=''):
		self.unpack(jsons)
		return

	def __str__(self):
		return self.pack()

	def __repr__(self):
		return self.pack()

	def unpack(self,jsons):
		rdict = json.loads(jsons)
		if P_PARAM not in rdict.keys() or M_PARAM not in rdict.keys() \
			or L_PARAM not in rdict.keys():
			raise Exception('no [%s] or [%s] or [%s] in keys'%(P_PARAM,M_PARAM,L_PARAM))
		self.p = rdict[P_PARAM]
		self.m = rdict[M_PARAM]
		self.l = rdict[L_PARAM]
		return

	def pack(self):
		rdict = dict()
		rdict[P_PARAM] =self.p
		rdict[L_PARAM] = self.l
		rdict[M_PARAM] = self.m
		return json.dumps(rdict,indent=4)

	def __add__(self,other):
		if self.p != other.p or self.m != other.m:
			raise Exception('p [%d] != [%d] or m [%d] != [%d]'%(self.p,other.p,self.m,other.m))
		l = []
		idx = 0
		while idx < self.m:
			lidx = self.m - idx -1
			curval = 0
			if lidx < len(self.l) :
				curval += self.l[lidx]
			if lidx < len(other.l):
				curval += other.l[lidx]
			curval %= self.p
			l.append(curval)
			idx += 1
		idx = 0 
		ol = []
		while idx < self.m:
			lidx = self.m - idx - 1
			ol.append(l[lidx])
			idx += 1
		rdict = dict()
		rdict[P_PARAM] = self.p
		rdict[M_PARAM] = self.m
		rdict[L_PARAM] = ol
		s = json.dumps(rdict)
		return BinaryField(s)

	def __sub__(self,other):
		if self.p != other.p or self.m != other.m:
			raise Exception('p [%d] != [%d] or m [%d] != [%d]'%(self.p,other.p,self.m,other.m))
		l = []
		idx = 0
		while idx < self.m:
			lidx = self.m - idx -1
			curval = 0
			if lidx < len(self.l) :
				curval += self.l[lidx]
			if lidx < len(other.l):
				curval -= other.l[lidx]
			curval %= self.p
			if curval < 0:
				curval += self.p
			l.append(curval)
			idx += 1
		idx = 0 
		ol = []
		while idx < self.m:
			lidx = self.m - idx - 1
			ol.append(l[lidx])
			idx += 1
		rdict = dict()
		rdict[P_PARAM] = self.p
		rdict[M_PARAM] = self.m
		rdict[L_PARAM] = ol
		s = json.dumps(rdict)
		return BinaryField(s)


