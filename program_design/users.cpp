#pragma once
#include<bits/stdc++.h>
#include<conio.h>
#include"users.h"
#include"products.h"
#include<stdlib.h>
using namespace std;
void users::signin()//原始注册信息批量输入(可新增)
{
	int r = 0;
	char c;
	std::cout << "********************现在开始注册新用户********************" << endl;
	cout << "<<<用户名输入e结束注册>>>" << endl;
	head = new personinfo[(sizeof(personinfo))];
	personinfo* p1, * p2;
	p1 = p2 = head;
	std::cout << "请输入用户名(6位)：" << endl;
	cin >> head->login;
	head->login[6] = '\0';
	std::cout << "请输入密码(6位)：" << endl;
	while ((c = _getch()) != '\r')
	{
		head->key[r] = c;
		r++;
	    putchar('*');
		if (r > 0 && c == 8)
		{
			r--;
			putchar('\b');
			putchar(32);
		    putchar('\b');
			continue;
		}

	}
	head->key[6] = '\0';
	std::cout << endl;
	fstream sign;
	char* newuser = new char[9];
	char fileuser[9] = { "userfile" };
	strcpy(newuser, fileuser);
	sign.open(newuser, ios::app | ios::binary);
	if (!sign.is_open())
	{
		std::cout << "注册信息登入失败！" << endl;
	}
	sign.write((char*)head, sizeof(personinfo));
	p1 = new personinfo[sizeof(personinfo)];
	p2->next = p1;
	p2 = p1;
	//delete[]head;
	while (true)
	{
		r = 0;
		std::cout << "请输入用户名：" << endl;
		cin >> p1->login;
		p1->login[6] = '\0';
		if (p1->login[0] == 'e')
			break;
		user_num++;
		std::cout << "请输入密码：" << endl;
		while ((c = _getch()) != 13)
		{
			if (r < 6 && isprint(c))
			{
				p1->key[r] = c;
				r++;
				putchar('*');
			}
			else if (r > 0 && c == '\b')
			{
				r--;
				putchar('\b');
				putchar(32);
				putchar('\b');
			}

		}
		p1->key[6] = '\0';
		sign.write((char*)p1, sizeof(personinfo));
		std::cout << endl;
		p1 = new personinfo[sizeof(personinfo)];
		p2->next = p1;
		p2 = p1;
	}
	p1 = p2 = NULL;
	delete[]p1;
	std::cout << "注册完成！" << endl;
	sign.close();
}
bool users::loadup()
{
	char* account_user = new char[11];
	char* key_user = new char[7];
	key_user[0] = { 1 };
	int just = 0;
	char* newuser = new char[9];
	char fileuser[9] = { "userfile" };
	personinfo aperson;
	int i = 0;
	char p;
	fstream login_user;
	login_user.open(fileuser, ios::in | ios::binary);
	if (!login_user.is_open())
	{
		std::cout << "文件读取失败！" << endl;
		exit(0);
	}
	std::cout << "********************用户登录********************" << endl;
	std::cout << "账号：";
	cin >> account_user;
	std::cout << "密码：";
	while ((p = _getch()) != '\r')
	{
		if (i < 6 && isprint(p))
		{
			key_user[i] = p;
			i++;
			putchar('*');
		}
		else if (i > 0 && p == 8)
		{
			i--;
			putchar('\b');
			putchar(32);
			putchar('\b');
		}
	}
	key_user[6] = '\0';
	char temp[7] = { '\0' };
	login_user.read((char*)&aperson, sizeof(personinfo));
	strcpy(temp, aperson.key);
	//temp[6] = '\0';
	cout << endl;
	while (!login_user.eof())
	{
		if (strcmp(aperson.login, account_user) == 0)
		{
			if (strcmp(temp, key_user) == 0)
			{
				cout << "登录成功！" << endl << "您的身份是:用户" << endl;
				just++;
				break;
			}
			else
			{
				cout << "密码输入错误！" << endl;
				break;
			}
		}
		login_user.read((char*)&aperson, sizeof(personinfo));
		strcpy(temp, aperson.key);
		//temp[6] = '\0';
	}
	if (just == 0)
	{
		cout << "登录失败！" << endl;
		login_user.close();
		return false;
	}
	else if (just != 0)
	{
		login_user.close();
		return true;
	}
}

void users::show_info()
{
	//cout << "当前注册用户数：" << user_num << endl;
	//执行文件显示
	personinfo temp_show;
	fstream show_userinfo;
	char useinfo[9] = { "userfile" };
	show_userinfo.open(useinfo, ios::in | ios::binary);
	if (show_userinfo.fail())
	{
		cout << "用户信息显示出错！" << endl;
	}
	show_userinfo.read((char*)&temp_show, sizeof(personinfo));
	while (!show_userinfo.eof())
	{
		
		cout << temp_show.login << endl;
		user_num++;
		show_userinfo.read((char*)&temp_show, sizeof(personinfo));
	}
	cout << "用户信息显示完毕！" << endl
		<<"共:"<<user_num<<"人"<<endl;
}
void users::user_proshow()
{
	aproduct.show_product();
}
void users::user_prosearch()
{
	aproduct.search();
}
void users::get_product()
{
	aproduct.getpro();
}
void users::settle()
{
	aproduct.getpro();
	//cout << "共计消费:" << aproduct.pro_settle() << "元" << endl
	cout<< "欢迎下次光临！" << endl;
}
int users::user_num = 0;