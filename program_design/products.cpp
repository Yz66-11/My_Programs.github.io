#pragma once
#include"products.h"
#include<bits/stdc++.h>
#include"users.h"
#include<conio.h>
#include<stdlib.h>
#include<windows.h>
#include<graphics.h>
#include<ColorDlg.h>
#include"resource.h"
using namespace std;
void products::store()
{
	fstream storein;
	char file[8] = { "product" };
	storein.open(file, ios::app | ios::binary);
	if (!storein)
	{
		std::cout << "商品文件打开失败！" << endl;
		exit(0);
	}
	int store_num = 0;
	char go_on;
	do {
		std::cout << "请输入本次要录入的商品数量:" << endl;
		std::cin >> store_num;
		product pro;
		cout << "请输入商品信息:" << endl;
		for (int i = 0; i < store_num; i++)
		{
			std::cout << "名称:";
			std::cin >> pro.titles;
			std::cout << "种类:";
			std::cin >> pro.kind;
			std::cout << "价格:";
			std::cin >> pro.price;
			storein.write((char*)&pro, sizeof(product));
			//cin >> pro.titles >> pro.kind >> pro.price;
		}
		std::cout << "本次录入结束！" << endl
			<< "你想继续录入吗(Y or N)" << endl;
		std::cin >> go_on;
	} while (go_on == 'Y');
}
void products::search()
{
	std::cout << "请输入要查询的商品种类:" << endl;
	char ki[50] = {'\0'};
	product pro_se;
	cin >> ki;
	fstream store_search;
	char filesea[8] = { "product" };
	store_search.open(filesea, ios::in | ios::binary);
	if (store_search.fail())
	{
		std::cout << "商品查询失败！" << endl;
	}
	store_search.read((char*)&pro_se, sizeof(product));
	while (!store_search.eof())
	{
		if (!strcmp(pro_se.kind, ki))
		{
			std::cout << pro_se.titles << "  " << pro_se.kind << "  " << pro_se.price << endl;
		}
		store_search.read((char*)&pro_se, sizeof(product));
	}
	std::cout << "查询完成！" << endl;
}
void products::show_product()
{
	fstream pro_show;
	char fileshow[8] = { "product" };
	pro_show.open(fileshow, ios::in | ios::binary);
	products_num = 0;
	if (pro_show.fail())
	{
		std::cout << "商品信息显示失败" << endl;
		system("pause");
		exit(0);
	}
	product proo;
	pro_show.read((char*)&proo, sizeof(product));
	cout << "*************************************商品列表*************************************" << endl;
	while (!pro_show.eof())
	{
		//pro_show.read((char*)&proo, sizeof(product));
		std::cout << proo.titles << "  " << proo.kind << "  " << proo.price << endl;
		products_num++;
		pro_show.read((char*)&proo, sizeof(product));
	}
	std::cout << "已显示所有商品！  共:" <<shownum()<< endl;
}
void products::getpro()
{
	int rec = 0, iob = 0;
	double sumproce = 0.0;
	products now;
	now.show_product();
	std::cout << "请输入要选择的商品名称及其数量(输入e结束选择):" << endl;
	for (rec = 0; ; rec++)
	{
		std::cin >> fir_tit[rec];
		if (fir_tit[rec][0] == 'e')
		{
			break;
		}
		std::cin >> price_how[rec];
	}
	fstream get_proinfo;
	char getinfo[8] = { "product" };
	get_proinfo.open(getinfo, ios::in | ios::binary);
	//如下的结算尚未完成
	product getpro;
	get_proinfo.read((char*)&getpro, sizeof(product));
	while (!get_proinfo.eof())
	{
		for (iob = 0; iob < 5; iob++)
		{
			if (fir_tit[iob][0] == getpro.titles[0])
			{
				sumproce += getpro.price * price_how[iob];
			}
		}
		get_proinfo.read((char*)&getpro, sizeof(product));
	}
	std::cout << "本次共消费:" << sumproce << "元" << endl;
	
	IMAGE code;
	loadimage(&code, _T("pay_code.jpg"));
	int height = code.getheight();
	int width = code.getwidth();
	initgraph(height, width);
	putimage(0, 0, &code);
	system("pause");
	closegraph();
	//putimage(400, 400, &code);
	  
}
/*double products::pro_settle()
{
	double total_pri = 0.0;
	ifstream in;
	char filein[8] = { "product" };
	in.open(filein);
	if (in.fail())
	{
		cout << "结算时出现文件故障！" << endl;
	}
	in.read((char*)headpro, sizeof(product));
	int reca = 0;
	while (!in.eof())
	{
		if (*(fir_tit + reca) == headpro->titles[0])
		{
			total_pri += headpro->price;
		}
		in.read((char*)headpro, sizeof(product));
	}
	return total_pri;
}功能不完善*/
int products::shownum()
{
	return products_num;
}
int products::products_num = 0;