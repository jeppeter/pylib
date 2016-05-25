#!/usr/bin/python

import sys


class AttrClass:
	keywords = ['key','val']
	forbidwords = ['hidden']


	def __init__(self):
		self.__key = 'key1'
		self.__val = 'val1'
		self.__hidden = 'hidden1'
		return



	def __getattr__(self,keyname):
		if keyname in AttrClass.keywords:
			keyname = '_%s__%s'%(self.__class__.__name__,keyname)
		elif keyname in self.__class__.forbidwords:
			raise AttributeError
		return self.__dict__[keyname]

	def __setattr__(self,keyname,val):
		if keyname in self.__class__.keywords or keyname in self.__class__.forbidwords:
			raise AttributeError
		self.__dict__[keyname] = val


class BasicCar:
	def __init__(self,carname,parent):
		self.__name = carname
		self.__parent = parent
		return

	def drive(self):
		print ('%s to drive (%s)'%(self.__name,self.__parent))
		return

class LuxuryCar(BasicCar):
	def __init__(self,carname,parent):
		BasicCar.__init__(self,carname,parent)
		self.__name = carname
		self.__parent = parent
		return
	def drive(self):
		print ('(%s)driver luxury (%s)'%(self.__name,self.__parent))
		return

class RaceCar(BasicCar):
	def __init__(self,carname,parent):
		BasicCar.__init__(self,carname,parent)
		self.__name = carname
		self.__parent = parent
		return
	def drive(self):
		print ('(%s)driver race (%s)'%(self.__name,self.__parent))
		return



def main():
	attr = AttrClass()
	print ('key %s val %s'%(attr.key,attr.val))
	ok = 0
	try:
		print('hidden %s'%(attr.hidden))
	except:
		ok = 1
	assert(ok > 0)

	ok = 0
	try:
		attr.val = 'newval'
	except:
		ok = 1
	assert(ok > 0)

	ok = 0
	try:
		attr.key = 'newkey'
	except:
		ok = 1
	assert(ok > 0)
	ok = 0
	try:
		print('attr.__key %s'%(attr.__key))
	except:
		ok = 1
	assert(ok > 0)

	race = RaceCar('go','farali')
	lux = LuxuryCar('java','lv')
	race.drive()
	lux.drive()
	return

if __name__ == '__main__':
	main()