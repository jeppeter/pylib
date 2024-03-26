

all:_hello.so

_hello.so:hello.o hello_wrap.o
	ld -shared hello.o hello_wrap.o -o _hello.so

%.o:%.c
	gcc -fpic -I/usr/include/python3.4m -c $< -o $@
	#gcc -fpic -I/usr/include/python2.7 -c $< -o $@

hello_wrap.c:hello.i
	swig -python hello.i

clean:
	rm -f _hello.so *.o
	rm -f hello_wrap.c
	rm -f hello.py
	rm -rf __pycache__
	rm -f *.pyc