#include <base.h>
#include <derive.h>
#include <iostream>

using namespace std;

int main(int argc,char* argv[]) {
	Base* pb = new Base();
	Derive* pd = new Derive();
	Base* pnb;
	Derive* pnd;
	char* name = (char*)"cc";
	if (argc > 1) {
		name = argv[1];
	}

	pb->hello(name);
	pd->hello(name);
	pnb = (Base*)pd;
	pnd = (Derive*)pb;
	pnb->hello(name);
	pnd->hello(name);
	delete pb;
	pb = NULL;
	delete pd;
	pd = NULL;
	return 0;
}