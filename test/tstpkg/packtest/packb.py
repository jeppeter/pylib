#!/usr/bin/python


import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import packa


class PackB(packa.PackBase):
	def __init__(self):
		packa.PackBase.__init__(self)
		print ('init packb')
		return

def call_b_new():
	return PackB()