

all:_example.so

_example.so:example_wrap.o example.o
	g++ -shared  example.o example_wrap.o -o _example.so

%.o:%.cxx
	g++  -fpic -I/usr/include/python2.7 -Wall -o $@ -c $<

example_wrap.cxx:example.i example.h
	swig -python -c++ -o example_wrap.cxx example.i

clean:
	rm -f *.o *.so
	rm -f example_wrap.cxx
	rm -f example.py