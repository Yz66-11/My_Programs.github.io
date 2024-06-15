#pragma once
#include"person.h"
#include"products.h"
#include"users.h"
extern char change;
typedef struct personinfoa
{
	char login[7] = { '\0' };
	char key[7] = { '\0' };
	char belong;
}personinfoa;

class products;
class agency: public person
{
private:
	products agency_pro;
	double number_how[50] = { 0.0 };
public:
	void agency_showpro();
	void show_info();
	void agency_choose(double discunt);
	bool loadup();
	void signin();
};
class agenunion
{
private:
	char nameunion;
	double count;
public:
	agenunion(char nameu = 'A', double ucount = 0.8)
	{
		nameunion = nameu;
		count = ucount;
	}
	void union_showinfo();
	agenunion operator*(agenunion& obj)
	{
		agenunion temp;
		temp.count = this->count * obj.count;
		temp.nameunion = this->nameunion + 3;
		return temp;
	}
	 agenunion& operator=(const agenunion& obj)
	{
		 //agenunion kop;
		 this->nameunion = obj.nameunion;
		 this->count = obj.count;
		 return *this;
	}
	double get_discount()
	{
		return count;
	}
};