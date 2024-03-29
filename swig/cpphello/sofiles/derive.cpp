#include "derive.h"
#include <iostream>

using namespace std;


Derive::Derive()
{

}

Derive::~Derive()
{

}

void Derive::hello(char* name)
{
	std::cout << "Derive hello " << name << std::endl;
	return;
}

