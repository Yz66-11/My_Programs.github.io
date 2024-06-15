#pragma once
#include<iostream>
#ifndef TYPEDEF_PRODUCT
#define TYPEDEF_PRODUCT
typedef struct product
{
	char titles[66] = {'\0'};
	char kind[50] = {'\0'};
	double price = 0.0;
	struct product* nexts;
}product;
#endif
class users;
class products
{
protected:
	static int products_num;
	product* headpro;
	char fir_tit[50][50] = { '\0' };
	double price_how[50] = { 0.0 };
public:
	void store();
	products()
	{
		//products_num++;
		headpro = new product[sizeof(product)];

	}
	~products()
	{
		products_num--;
	}
	void search();
	void show_product();
	int shownum();
	//double pro_settle();
	void getpro();
};