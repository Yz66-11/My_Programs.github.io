#pragma once
#include"person.h"
person::person()
{
	numbers++;
}
person::~person()
{
	numbers--;
}
int person::numbers = 0;