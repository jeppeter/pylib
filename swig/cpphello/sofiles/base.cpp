#include "base.h"
#include <iostream>

using namespace std;


Base::Base()
{

}

Base::~Base()
{

}

void Base::hello(char* name)
{
	std::cout << "Base hello " << name << std::endl;
	return;
}
