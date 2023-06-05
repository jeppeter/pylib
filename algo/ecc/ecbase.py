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
R_PARAM = 'r'

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
			or L_PARAM not in rdict.keys() or R_PARAM not in rdict.keys():
			raise Exception('no [%s] or [%s] or [%s] or [%s] in keys'%(P_PARAM,M_PARAM,L_PARAM, R_PARAM))
		self.p = rdict[P_PARAM]
		self.m = rdict[M_PARAM]
		self.l = rdict[L_PARAM]
		self.r = rdict[R_PARAM]

		if len(self.r) != (self.m + 1):
			raise Exception('r len[%d] < m [%d]'%(len(self.r),self.m))
		if self.r[0] != 1:
			raise Exception('r not start with 1')
		return

	def pack(self):
		rdict = dict()
		rdict[P_PARAM] =self.p
		rdict[L_PARAM] = self.l
		rdict[M_PARAM] = self.m
		rdict[R_PARAM] = self.r
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
		rdict[R_PARAM] = self.r
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
		rdict[R_PARAM] = self.r
		s = json.dumps(rdict)
		return BinaryField(s)

	def __mul__(self,other):
		if self.p != other.p or self.m != other.m:
			raise Exception('p [%d] != [%d] or m [%d] != [%d]'%(self.p,other.p,self.m,other.m))
		if self.r != other.r:
			raise Exception('p %s != other %s'%(self.r,other.r))

		# now to calculate the 
		mull = []
		idx = 0
		while idx < (2 * self.m - 1):
			mull.append(0)
			idx += 1

		idx = 0
		while idx < len(self.l):
			jdx = 0
			while jdx < len(other.l):
				curval = self.l[idx] * other.l[jdx]
				cidx = idx + jdx
				mull[cidx] += curval
				mull[cidx] %= self.p
				logging.info('[%d]=[%d](+%d)'%(cidx,mull[cidx],curval))
				jdx += 1
			idx += 1

		idx = 0
		while idx < len(mull):
			logging.info('[%d]=[%d]'%(idx,mull[idx]))
			idx += 1

		# now to give the 
		idx = 0
		while idx <= (len(mull) - len(self.r)):
			jdx = 0
			curval = mull[idx]
			while jdx < len(self.r):
				mull[idx+jdx] -= (curval * self.r[jdx])
				jdx += 1
			idx += 1

		while idx < len(mull):
			mull[idx] %= self.p
			if mull[idx] < 0:
				mull[idx] += self.p
			idx += 1

		rdict = dict()
		rdict[L_PARAM] = mull[-(self.m):]
		rdict[R_PARAM] = self.r
		rdict[M_PARAM] = self.m
		rdict[P_PARAM] = self.p
		s = json.dumps(rdict)
		return BinaryField(s)



