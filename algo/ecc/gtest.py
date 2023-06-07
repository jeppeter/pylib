#! /usr/bin/env python

import os
import sys
import logging
GALOIS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..','galois','src'))
sys.stdout.write('GALOIS_PATH [%s]\n'%(GALOIS_PATH))
sys.path.append(GALOIS_PATH)
import galois

def set_logging():
    loglvl= logging.DEBUG
    curlog = logging.getLogger('root')
    #sys.stderr.write('curlog [%s][%s]\n'%(args.logname,curlog))
    curlog.setLevel(loglvl)
    if len(curlog.handlers) > 0 :
        curlog.handlers = []
    formatter = logging.Formatter('%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d<%(levelname)s>\t%(message)s')
    logstderr = logging.StreamHandler()
    logstderr.setLevel(loglvl)
    logstderr.setFormatter(formatter)
    curlog.addHandler(logstderr)
    return

set_logging()
GF = galois.GF(251 ** 5,irreducible_poly=[1,1,12,9,0,7])
print('%s'%(GF.properties))

a = galois.Poly([123,0,76,7,4],field=GF)
print('%s'%(a))

b = galois.Poly([196,12,225,0,76],field=GF)
print('%s'%(b))
p = galois.Poly([1,1,12,9,0,7],field=GF)
print('%s'%(b))

d,s,t = galois.egcd(a,p)
print('d %s s %s t %s'%(d,s,t))