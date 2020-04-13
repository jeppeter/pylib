#! /usr/bin/env python

import noddy

def call_func(xx):
	print('xx %s'%(xx))
	return xx

n = noddy.Noddy(callback=call_func,args=392)
n.first = 'ccc'
n.last = 'xxx'
print('%s'%(n.name()))
n.callback = call_func
n.args = 392
v = n.call()
print("retval [%s]"%(v))