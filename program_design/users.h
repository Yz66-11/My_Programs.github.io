#pragma once
#include"person.h"
#include"products.h"
#ifndef TYPEDEF_PERSONINFO
#define TYPEDEF_PERSONINFO
typedef struct personinfo
{
	char login[7] = {'\0'};
	char key[7] = {'\0'};
	struct personinfo* next;
}personinfo;
#endif
class products;
class users :public person//用户类
{
private:
	static int user_num;
	//int* _purchasenum;
	personinfo* head;
	products aproduct;	
public:
	
	users()
	{
		//_purchasenum = new int(0);
		head = NULL;
		//user_num++;
	}
	bool loadup();
	void show_info();
	void get_product();
	~users()
	{
		//user_num--;
	}
	void signin();
	void user_proshow();
	void user_prosearch();
	void settle();
};