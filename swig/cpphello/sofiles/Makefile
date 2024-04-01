
#TTI_TYPE=
TTI_TYPE=-fno-rtti

all:libcppobj.so

libcppobj.so:base.o derive.o
	g++ -shared ${TTI_TYPE} -Wl,-soname=libcppobj.so -o libcppobj.so base.o derive.o

%.o:%.cpp
	#g++ -fpic ${TTI_TYPE} -DBUILDING_DLL -Wall -c $< -o $@
	g++ -fpic ${TTI_TYPE} -Wall -c $< -o $@

clean:
	rm -f *.so *.o