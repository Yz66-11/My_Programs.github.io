#pragma once
#include<bits/stdc++.h>
#include<conio.h>
#include"administrator.h"
using namespace std;
void administrator::signin()
{
	int t = 0;
	char x;
	std::cout << "********************现在开始注册新管理员********************" << endl;
	std::cout << "<<<输入e结束注册>>>" << endl;
	head0 = new personinfo[sizeof(personinfo)];
	personinfo* p3, * p4;
	p3 = p4 = head0;
	cout << "请输入用户名(6位)：" << endl;
	cin >> head0->login;
	head0->login[6] = '\0';
	//cin.ignore();
	cout << "请输入密码(6位)：" << endl;
	while ((x = _getch()) != 13)
	{
		if (t < 6 && isprint(x))
		{
			head0->key[t] = x;
			t++;
			putchar('*');
		}
		else if (t > 0 && x == '\b')
		{
			t--;
			putchar('\b');
			putchar(32);
			putchar('\b');
		}

	}
	head0->key[6] = '\0';
	std::cout << endl;
	fstream sign;
	
	char fileadmi[9] = { "admifile" };
	
	sign.open(fileadmi, ios::app | ios::binary);
	if (!sign.is_open())
	{
		std::cout << "注册信息登入失败！" << endl;
	}
	sign.write((char*)head0, sizeof(personinfo));
	p3 = new personinfo[sizeof(personinfo)];
	p4->next = p3;
	p4 = p3;
	delete[]head0;
	while (true)
	{
		t = 0;
		std::cout << "请输入用户名：" << endl;
		cin >> p3->login;
		p3->login[6] = '\0';
		cin.ignore();
		if (p3->login[0] == 'e')
			break;
		
		std::cout << "请输入密码：" << endl;
		while ((x = _getch()) != 13)
		{
			if (t < 6 && isprint(x))
			{
				p3->key[t] = x;
				t++;
				putchar('*');
			}
			else if (t > 0 && x == '\b')
			{
				t--;
				putchar('\b');
				putchar(32);
				putchar('\b');
			}

		}
		p3->key[6] = '\0';
		sign.write((char*)p3, sizeof(personinfo));
		std::cout << endl;
		p3 = new personinfo[sizeof(personinfo)];
		p4->next = p3;
		p4 = p3;
	}
	delete[]p3;
	p3 = p4 = NULL;
	
	cout << "注册完成！" << endl;
}
bool administrator::loadup()
{
	char account_admi[11] = {'\0'};
	char key_admi[7] = { '\0'};
	int ajust = 0;
	char fileadmi[9] = { "admifile" };
	int i = 0;
	char p;
	personinfo admi_temp;
	fstream login_admi;
	login_admi.open(fileadmi, ios::in | ios::binary);
	if (login_admi.fail())
	{
		std::cout << "文件读取失败！" << endl;
		exit(0);
	}
	std::cout << "********************管理员登录********************" << endl;
	std::cout << "账号：";
	cin >> account_admi;
	std::cout << "密码：";
	while ((p = _getch()) != '\r')
	{
		if (i < 6 && isprint(p))
		{
			key_admi[i] = p;
			i++;
			putchar('*');
		}
		else if (i > 0 && p == 127)
		{
			i--;
			putchar('\b');
			putchar(32);
			putchar('\b');
		}
	}
	key_admi[6] = '\0';
	login_admi.read((char*)&admi_temp, sizeof(personinfo));
	cout << endl;
	while (!login_admi.eof())
	{
		if (strcmp(admi_temp.login, account_admi) == 0)
		{
			if (strcmp(admi_temp.key, key_admi) == 0)
			{
				cout << "登录成功！" << endl << "您的身份是:管理员" << endl;
				ajust++;
				break;
			}
			else
			{
				cout << "密码输入错误！" << endl;
				break;
			}
		}
		login_admi.read((char*)&admi_temp, sizeof(personinfo));
		//tempu[6] = '\0';
	}
	if (ajust == 0)
	{
		cout << "登录失败！" << endl;
		login_admi.close();
		return false;
	}
	else if (ajust != 0)
	{
		login_admi.close();
		return true;
	}
}
void administrator::show_info()
{
	fstream show_admiinfo;
	personinfo admi_show;
	char admishow[9] = { "admifile" };
	show_admiinfo.open(admishow, ios::in | ios::binary);
	show_admiinfo.read((char*)&admi_show, sizeof(personinfo));
	while (!show_admiinfo.eof())
	{
		cout << admi_show.login << endl;
		show_admiinfo.read((char*)&admi_show, sizeof(personinfo));
	}
	cout << "管理员信息显示完毕！" << endl;
}
void administrator::admi_proshow()
{	
	product_e.show_product();
}
void administrator::admi_usershow()
{
	to_show.show_info();
}
void administrator::admi_prostore()
{
	product_e.store();
}
void administrator::admi_prosearch()
{
	product_e.search();
}
void administrator::admi_agentshow()
{
	agency_show.show_info();
}