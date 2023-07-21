# 
# Montgomery reduction algorithm (Python)
# 
# Copyright (c) 2022 Project Nayuki
# All rights reserved. Contact Nayuki for licensing.
# https://www.nayuki.io/page/montgomery-reduction-algorithm
# 

import math
import logging





import math

MONT_BITSIZE = 0x40

class MontReducer(object):
	def __init__(self,mod):
		if mod < 3 or mod % 2 == 0:
			raise ValueError("Modulus must be an odd number at least 3")
		self.mod = mod
		bl = mod.bit_length()
		bl = ((bl + MONT_BITSIZE -1) // MONT_BITSIZE) * MONT_BITSIZE
		self.BL = bl
		self.MAXB = mod.bit_length()
		self.R = ( 1 << self.BL)
		self.RR = (1 << (self.BL * 2))
		self.INVR = pow(self.R,mod-2,mod)
		self.FACTOR = (self.R * self.INVR - 1) // self.mod
		self.MASK = (self.R - 1)
		return

	def mont_from(self,a):
		return (a * self.INVR) % self.mod

	def mont_to(self,a):
		#return (a * self.RR * self.INVR) % self.mod
		return (a * self.R) % self.mod

	def __str__(self):
		return self.format()

	def __repr__(self):
		return self.format()

	def format(self):
		s = 'N 0x%X'%(self.mod)
		s += ' R 0x%X'%(self.R)
		s += ' RR 0x%X'%(self.RR)
		s += ' INVR 0x%X'%(self.INVR)
		s += ' BL 0x%X'%(self.BL)
		s += ' MAXB 0x%X'%(self.MAXB)
		s += ' FACTOR 0x%X'%(self.FACTOR)
		return s

	def multiply(self,x,y):
		x = x % self.mod
		y = y % self.mod
		product = x * y
		temp = ((product & self.MASK) * self.FACTOR) & self.MASK
		reduced = (product + temp * self.mod) >> self.BL
		if reduced < self.mod:
			result = reduced
		else:
			result = reduced - self.mod
		return result








class MontgomeryReducer:
	
	def __init__(self, mod):
		# Modulus
		if mod < 3 or mod % 2 == 0:
			raise ValueError("Modulus must be an odd number at least 3")
		self.modulus = mod
		
		# Reducer
		self.reducerbits = (mod.bit_length() // 8 + 1) * 8  # This is a multiple of 8
		self.reducer = 1 << self.reducerbits  # This is a power of 256
		self.mask = self.reducer - 1
		assert self.reducer > mod and math.gcd(self.reducer, mod) == 1
		
		# Other computed numbers
		self.reciprocal = MontgomeryReducer.reciprocal_mod(self.reducer % mod, mod)
		self.factor = (self.reducer * self.reciprocal - 1) // mod
		self.convertedone = self.reducer % mod

	def __str__(self):
		return self.format()

	def __repr__(self):
		return self.format()

	def format(self):
		s = 'modulus 0x%x reducerbits 0x%x'%(self.modulus,self.reducerbits)
		s += ' reducer 0x%x'%(self.reducer)
		s += ' reciprocal 0x%x'%(self.reciprocal)
		s += ' factor 0x%x'%(self.factor)
		s += ' convertedone 0x%x'%(self.convertedone)
		return s
	
	
	# The range of x is unlimited
	def convert_in(self, x):
		return (x << self.reducerbits) % self.modulus
	
	
	# The range of x is unlimited
	def convert_out(self, x):
		return (x * self.reciprocal) % self.modulus
	
	
	# Inputs and output are in Montgomery form and in the range [0, modulus)
	def multiply(self, x, y):
		mod = self.modulus
		assert 0 <= x < mod and 0 <= y < mod
		product = x * y
		temp = ((product & self.mask) * self.factor) & self.mask
		reduced = (product + temp * mod) >> self.reducerbits
		result = reduced if (reduced < mod) else (reduced - mod)
		assert 0 <= result < mod
		return result
	
	
	# Input x (base) and output (power) are in Montgomery form and in the range [0, modulus); input y (exponent) is in standard form
	def pow(self, x, y):
		assert 0 <= x < self.modulus
		if y < 0:
			raise ValueError("Negative exponent")
		z = self.convertedone
		while y != 0:
			if y & 1 != 0:
				z = self.multiply(z, x)
			x = self.multiply(x, x)
			y >>= 1
		return z
	
	
	@staticmethod
	def reciprocal_mod(x, mod):
		# Based on a simplification of the extended Euclidean algorithm
		assert mod > 0 and 0 <= x < mod
		y = x
		x = mod
		a = 0
		b = 1
		while y != 0:
			a, b = b, a - x // y * b
			x, y = y, x % y
		if x == 1:
			return a % mod
		else:
			raise ValueError("Reciprocal does not exist")
