
TOPDIR=$(shell pwd)
#TTI_TYPE=-fno-rtti
#SWIG_RTTI=-nortti

all:_callobj.so

_callobj.so:callobj_wrap.o
	#g++ -shared ${TTI_TYPE} -L${TOPDIR}/sofiles -lcppobj  callobj_wrap.o  -o _callobj.so
	#g++ -shared ${TTI_TYPE} -Wl,-soname=_callobj.so  -L${TOPDIR}/sofiles -lcppobj  callobj_wrap.o  -o _callobj.so
	g++ -shared ${TTI_TYPE} -Wl,-soname=_callobj.so  callobj_wrap.o -o _callobj.so -L${TOPDIR}/sofiles -lcppobj

%.o:%.cxx
	#g++ -fPIC -I${TOPDIR}/sofiles -I/usr/include/python3.4m -c $< -o $@
	g++ -fpic ${TTI_TYPE} -I${TOPDIR}/sofiles -I/usr/include/python2.7 -c $< -o $@
	#g++ -fpic ${TTI_TYPE} -I${TOPDIR}/sofiles -I/usr/local/include/python3.9 -c $< -o $@

callobj_wrap.cxx:callobj.i
	swig -python -c++ ${SWIG_RTTI} -I${TOPDIR}/sofiles -o $@ callobj.i

clean:
	rm -f *.so *.o
	rm -f callobj_wrap.cxx
	rm -f callobj.py
	rm -rf __pycache__
	rm -f *.pyc