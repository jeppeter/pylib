#!/usr/bin/python

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from packa import PackBase , call_a_new
from packb import PackB , call_b_new

if sys.version[0] == '2':
	del packa
	del packb