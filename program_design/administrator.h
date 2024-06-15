#pragma once
#include"person.h"
#include"products.h"
#include"users.h"
#include"agency.h"
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
class users;
class agency;
class administrator :public person//管理员类
{
private:
	personinfo* head0;
	products product_e;
	users to_show;
	agency agency_show;
public:
	bool loadup();
	void signin();
	void show_info();
	administrator()
	{
		head0 = NULL;
	}
	~administrator()
	{
		//admi_num--;
	}
	void admi_proshow();
	void admi_usershow();
	void admi_prostore();
	void admi_prosearch();
	void admi_agentshow();
};