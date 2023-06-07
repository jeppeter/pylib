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

def bit_length(val):
	retcnt = 0
	while val != 0:
		val >>= 1
		retcnt += 1
	return retcnt

class _FieldArray(object):
	def _degree(self):
		self._shrink()
		return len(self.val)

	def _shrink(self):
		setv = self.val
		idx = 0
		while idx < len(setv):
			if (setv[idx]  % self.p) != 0:
				break
			idx += 1

		if idx == 0:
			return
		self.val = setv[idx:]
		return

	def _update(self):
		self.degree = self._degree()
		return

	def __init__(self,arr=[],p=251):
		self.val = arr
		self.p = p
		self._update()
		return

	def _check_other(self,other):
		if not issubclass(other,_FieldArray):
			raise Exception('not accept _FieldArray type')

		if self.p != other.p:
			raise Exception('p %d != other.p %d'%(self.p,other.p))
		return

	def __floordiv__(self,other) -> _FieldArray:
		self._check_other(other)
		
		if self.degree < other.degree:
			return _FieldArray([0])
		q_degree = self.degree - other.degree
		q = []
		idx = 0
		while idx < (q_degree + 1):
			q.append(0)
			idx += 1
		aa = self.val[0:q_degree + 1].copy()
		for i in range(q_degree + 1):
			if aa[i] > 0:
				q[i] = (aa[i] * (pow(other.val[0],self.p - 2, self.p))) % self.p
				N = min(other.degree,q_degree + 1 - i)
				for j in range(1,N):
					aa[i+j] = (aa[i + j] - (q[i] * b[j]) % self.p ) % self.p
		return _FieldArray(q,self.p)

	def __mul__(self,other):
		self._check_other(other)
		return

	def __eq__(self,other):
		if isinstance(other,int):
			if other == 0:
				return self.degree == 0
			else:
				return self.degree == 1 and self.val[0] == other
		other._shrink()
		self._shrink()
		return self.degree == other.degree and self.val == other.val



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

		# now to calculate the number 
		mull = []
		idx = 0
		while idx < (2 * self.m - 1):
			# to make the calculate number
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
				#logging.info('[%d]=[%d](+%d)'%(cidx,mull[cidx],curval))
				jdx += 1
			idx += 1

		idx = 0
		while idx < len(mull):
			#logging.info('[%d]=[%d]'%(idx,mull[idx]))
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

	def inv(self):
		expcnt =  self.p - 2
		explist = []
		curv = BinaryField(self.pack())
		explist.append(curv)
		idx = 2
		logging.info('expcnt %d'%(expcnt))
		while idx < expcnt:
			curv = curv * curv
			logging.info('[%d]\n%s'%(idx,curv))
			explist.append(curv)
			idx <<= 1

		retv = None
		idx = 0
		while idx < len(explist):
			if ((expcnt >> idx) & 0x1) != 0:
				logging.info('idx [%d] [%d]\n%s'%(idx,(1 << idx),repr(explist[idx])))
				if retv is None:
					retv = explist[idx]
				else:
					retv = retv * explist[idx]
				logging.info('retv\n%s'%(repr(retv)))
			idx += 1
		return retv




