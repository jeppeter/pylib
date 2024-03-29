
TOPDIR=$(shell pwd)

all:_callobj.so

_callobj.so:callobj_wrap.o
	g++ -shared ${TTI_TYPE} -Wl,-soname=_callobj.so -L${TOPDIR}/sofiles -lcppobj -shared callobj_wrap.o -o _callobj.so

%.o:%.cxx
	#g++ -fPIC -I${TOPDIR}/sofiles -I/usr/include/python3.4m -c $< -o $@
	g++ -fPIC -I${TOPDIR}/sofiles -I/usr/include/python2.7 -c $< -o $@

callobj_wrap.cxx:callobj.i
	swig -python -c++ -I${TOPDIR}/sofiles -o $@ callobj.i

clean:
	rm -f *.so *.o
	rm -f callobj_wrap.cxx
	rm -f callobj.py
	rm -rf __pycache__
	rm -f *.pyc