#! /usr/bin/env python

import json
import logging

A_PARAM = 'a'
B_PARAM = 'b'
ORDER_PARAM = 'order'

class ECBase(object):
	def __init__(self,jsons=''):
		self.unpack()
		return

	def unpack(self,jsons):
		rdict = json.loads(jsons)
		if A_PARAM not in rdict.keys() or B_PARAM not in rdict.keys() or \
			ORDER_PARAM not in rdict.keys():
			raise Exception('no [%s] or [%s] or [%s] in jsons'%(A_PARAM,B_PARAM,ORDER_PARAM))
		self.a = rdict[A_PARAM]
		self.b = rdict[B_PARAM]
		self.order = rdict[ORDER_PARAM]
		return

	def pack(self):
		rdict = dict()
		rdict[A_PARAM] = self.a
		rdict[B_PARAM] = self.b
		rdict[ORDER_PARAM] = self.order
		return json.dumps(rdict,indent=4)


	def __str__(self):
		return self.pack()

	def __repr__(self):
		return self.pack()
