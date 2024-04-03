#! /usr/bin/env python
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import example

v = example.Vector(3.5,2.5,9.0)
print('%s'%(v.magnitude()))
print('%s'%(v.cprint()))
va = example.VectorArray(5)
va.set(0,v)
print('%s'%(va.get(0).cprint()))
v = example.Vector(3.5,21.0,9.0)
print('%s'%(v.magnitude()))