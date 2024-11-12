#! /usr/bin/env python
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))

import d2ltorch

trained , test = d2ltorch.load_data_fashion_mnist(path='z:\\testfashion')
sys.stdout.write('trained\n%s\n'%(trained))
sys.stdout.write('test\n%s\n'%(test))