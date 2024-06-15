#pragma once
#include<iostream>
#include<cstring>
#include"agency.h"
#include"products.h"
#include<conio.h>
#include<fstream>
using namespace std;

void agency::signin()
{
	personinfoa agency_in;
	int g = 0;
	char ag = 0;
	std::cout << "********************现在开始添加新代理商********************" << endl;
	std::cout << "<<<输入e结束注册>>>" << endl;
	char lgoin_agency[7] = { '\0' };
	char key_agency[7] = { '\0' };
	char belong_temp = 0;
	fstream agencyinfo;
	agencyinfo.open("agency", ios::app | ios::binary);
	if (agencyinfo.fail())
	{
		std::cout << "代理商添加失败" << endl;
		exit(0);
	}
	std::cout << "请输入用户名:" << endl;
	std::cin >> agency_in.login;
	std::cout << "请输入密码:" << endl;
	while ((g = _getch()) != 13)
	{
		if (ag < 6 && isprint(g))
		{
			agency_in.key[g] = ag;
			g++;
			putchar('*');
		}
		else if (g > 0 && ag == '\b')
		{
			g--;
			putchar('\b');
			putchar(32);
			putchar('\b');
		}

	}
	std::cout << endl;
	std::cout << "请输入加盟商(A or B or C)" << endl;
	std::cin>>agency_in.belong;
	while (true)
	{
		agencyinfo.write((char*)&agency_in, sizeof(personinfoa));
		std::cout << "请输入用户名:" << endl;
		std::cin >> agency_in.login;
		if (agency_in.login[0] == 'e')
			break;
		std::cout << "请输入密码:" << endl;
		ag = 0;
		while ((g = _getch()) != 13)
		{
			if (ag < 6 && isprint(g))
			{
				agency_in.key[g] = ag;
				g++;
				putchar('*');
			}
			else if (g > 0 && ag == '\b')
			{
				g--;
				putchar('\b');
				putchar(32);
				putchar('\b');
			}

		}
		std::cout << endl;
		std::cout << "请输入加盟商(A or B or C):" << endl;
		std::cin>>agency_in.belong;
	}
	agencyinfo.close();
}
bool agency::loadup()
{
	int bg = 0, ko = 0;
	personinfoa agency_up;
	char login_up[7] = { '\0' };
	char key_up[7] = { '\0' };
	cout << "********************代理商登录********************" << endl;
	cout << "账号:";
	cin >> login_up;
	cout << "密码:";
	bg = 0;
	while ((ko = _getch()) != 13)
	{
		if (bg < 6 && isprint(ko))
		{
			agency_up.key[bg] = ko;
			bg++;
			putchar('*');
		}
		else if (bg > 0 && ko == '\b')
		{
			bg--;
			putchar('\b');
			putchar(32);
			putchar('\b');
		}

	}
	cout << endl;
	fstream agency_load;
	agency_load.open("agency", ios::in | ios::binary);
	if (agency_load.fail())
	{
		std::cout << "登录时出现问题" << endl;
		exit(0);
	}
	agency_load.read((char*)&agency_up, sizeof(personinfoa));
	while (!agency_load.eof())
	{
		if (!strcmp(login_up, agency_up.login))
		{
			if (!strcmp(key_up, agency_up.key))
			{
				std::cout << "登录成功！"
					<<"您的身份是:代理商" << endl;
				change = agency_up.belong;
				return true;
				break;
			}
			else
			{
				std::cout << "密码错误！" << endl;
				return false;
				break;
			}
		}
		agency_load.read((char*)&agency_up, sizeof(personinfoa));
	}
	agency_load.close();
}
void agency::agency_showpro()
{
	agency_pro.show_product();
}
void agency::show_info()
{
	fstream agency_show;
	personinfoa showagency;
	agency_show.open("agency", ios::in | ios::binary);
	if (agency_show.fail())
	{
		std::cout << "代理商信息显示失败！" << endl;
		exit(0);
	}
	agency_show.read((char*)&showagency, sizeof(personinfoa));
	while (!agency_show.eof())
	{
		std::cout << showagency.login <<"  "<<showagency.belong << endl;
		agency_show.read((char*)&showagency, sizeof(personinfoa));
	}
	std::cout << "显示完毕！" << endl;
	agency_show.close();
}
void agency::agency_choose(double discount)
{
	std::cout << "请选择您要代理的商品:" << endl;
	//代理商可以一定折扣批发商品
	//agency_pro.show_product();
	int rect = 0, iobs = 0;
	double sumprocea = 0.0;
	products nowe;
	char fir_titl[50][50] = {'\0'};
	nowe.show_product();
	cout << "请输入要选择的商品名称及其数量(输入e结束):" << endl;
	for (rect = 0; ; rect++)
	{
		std::cin >> fir_titl[rect];
		if (fir_titl[rect][0] == 'e')
		{
			break;
		}
		std::cin >> number_how[rect];
	}
	fstream get_proinfoa;
	char getinfoa[8] = { "product" };
	get_proinfoa.open(getinfoa, ios::in | ios::binary);
	product getpro;
	get_proinfoa.read((char*)&getpro, sizeof(product));
	while (!get_proinfoa.eof())
	{
		for (iobs = 0; iobs < 5; iobs++)
		{
			if (fir_titl[iobs][0] == getpro.titles[0])
			{
				sumprocea += getpro.price * number_how[iobs];
			}
		}
		get_proinfoa.read((char*)&getpro, sizeof(product));
	}
	std::cout << "本次共批发:" << sumprocea * discount << "元" << endl;
}
void agenunion::union_showinfo()
{
	std::cout << "当前加盟商为:" << nameunion << "  " << "享有折扣为:" <<count<< endl;
}