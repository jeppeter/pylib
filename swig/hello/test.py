#! /usr/bin/env python

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import hello

hello.print_hello('good name')
print('BASEVAL %s'%(hello.cvar.BASEVAL))