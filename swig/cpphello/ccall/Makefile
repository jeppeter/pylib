
TOPDIR=$(shell pwd)

all:ccall

ccall:main.o ${TOPDIR}/../sofiles/libcppobj.so
	g++ -o $@ $^ -L${TOPDIR}/../sofiles -lcppobj

%.o:%.cpp
	g++ -Wall -I${TOPDIR}/../sofiles -o $@ -c $<

clean:
	rm -f ccall *.o