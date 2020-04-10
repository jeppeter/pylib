#! /usr/bin/env python
import custom

def xxc(gpio,X):
	print('gpio %d'%(gpio))
	print('X %s'%(X))
	return X
m = custom.Custom()
#m.setcall(30,xxc,30)
#v = m.call()
#print('call back %s'%(v))
m.first = 'xxx'
m.last = 'zzz'
print('%s'%(m.name()))