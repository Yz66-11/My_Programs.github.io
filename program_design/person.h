#pragma once
class person
{
protected:
	static int numbers;
public:
	virtual bool loadup() = 0;
	person();
	virtual void show_info() = 0;
	virtual ~person();
	virtual void signin() = 0;
};