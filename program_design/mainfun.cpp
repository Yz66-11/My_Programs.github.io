//这是一个面向在校学生、商品管理者(和可能的代理商)的商品系统
//开始时间：2024.3.29
#pragma once
#include<iostream>
#include<string>
#include<fstream>
#include<ctype.h>
#include<conio.h>
#include<windows.h>
#include"person.h"
#include"users.h"
#include"administrator.h"
#include"products.h"
#include"agency.h"
#include<ctime>
#include<cstdio>
using namespace std;
char change;
static void show_time()
{
	time_t timenow;
	struct tm* np;
	time(&timenow);
	np = localtime(&timenow);
	std::cout << "                                                                                   "<<"             当地时间:" << 1900 + np->tm_year << "." << 1 + np->tm_mon << "." << np->tm_mday << endl;
}
int main()
{
	users use;
	administrator admi;//用于演示程序功能
	agency agent;
	agenunion group[3] = { agenunion('A',0.8),agenunion('B',0.9),agenunion('C',0.7) };

	//在此处进行了一些小测试
	/*users Atry;
	Atry.signin();
	Atry.loadup();*/
	std::cout << "****************************************************欢迎进入零食小铺****************************************************" << endl;
	std::cout << "***************************************************天大地大，吃饭最大***************************************************" << endl;
	show_time();
	int flag_login = 1;
	do
	{
		std::cout << "请选择您的身份(输入0退出)：" << endl;
		std::cout << "1.管理员         2.用户          3.代理商" << endl;
		//下面执行对应的登录操作(flag分别用于登录之后的功能选择中)

		int flag_users = 0;
		int flag_admis = 0;
		int flag_product = 0;
		std::cin >> flag_login;
		if (flag_login)
			system("cls");
		if (flag_login == 1)
		{
			int admi_step = 0;
			std::cout << "请选择您要进行的操作:" << endl;
			std::cout << "1.管理员登录                2.管理员注册" << endl;
			std::cin >> admi_step;
			if (admi_step == 1)
			{
				if (admi_step)
					system("cls");
				int admi_sort = 0;
				std::cout << "请输入您的管理员序号:" << endl;
				std::cin >> admi_sort;
				if (admi.loadup())
				{
					std::cout << "请选择您要执行的功能:" << endl;
					std::cout << "1.查看商品信息                             2.查看用户信息" << endl
						<< "3.查看管理员信息                           4.录入商品信息" << endl
						<< "5.搜索商品信息                             6.查看代理商信息" << endl;
					std::cout << "输入0退出" << endl;
					std::cin >> flag_admis;
					do {
						if (flag_admis == 1)
						{
							system("cls");
							admi.admi_proshow();
						}
						else if (flag_admis == 2)
						{
							system("cls");
							admi.admi_usershow();
						}
						else if (flag_admis == 3)
						{
							system("cls");
							admi.show_info();
						}
						else if (flag_admis == 4)
						{
							system("cls");
							admi.admi_prostore();
						}

						else if (flag_admis == 5)
						{
							system("cls");
							admi.admi_prosearch();
						}
						else if (flag_admis == 6)
						{
							system("cls");
							admi.admi_agentshow();
						}
						std::cout << "还要进行其它操作吗？(输入0结束)" << endl
							<< "1.查看商品信息                             2.查看用户信息" << endl
							<< "3.查看管理员信息                           4.录入商品信息" << endl
							<< "5.搜索商品信息                             6.查看代理商信息" << endl;
						std::cin >> flag_admis;
						if (flag_admis)
							system("cls");
					} while (flag_admis != 0);
				}
				else
				{
					std::cout << "请检查您的账号和密码！" << endl;
					//admi.loadup();
					int admi_sort = 0;
					bool value = true;
					std::cout << "请输入您的管理员序号:" << endl;
					std::cin >> admi_sort;
					do {
						if (value = admi.loadup())
						{
							std::cout << "请选择您要执行的功能:" << endl;
							std::cout << "1.查看商品信息                             2.查看用户信息" << endl
								<< "3.查看管理员信息                           4.录入商品信息" << endl
								<< "5.搜索商品信息                             6.查看代理商信息" << endl;
							std::cout << "输入0退出" << endl;
							std::cin >> flag_admis;
							do {
								if (flag_admis == 1)
								{
									system("cls");
									admi.admi_proshow();
								}
								else if (flag_admis == 2)
								{
									system("cls");
									admi.admi_usershow();
								}
								else if (flag_admis == 3)
								{
									system("cls");
									admi.show_info();
								}
								else if (flag_admis == 4)
								{
									system("cls");
									admi.admi_prostore();
								}

								else if (flag_admis == 5)
								{
									system("cls");
									admi.admi_prosearch();
								}
								else if (flag_admis == 6)
								{
									system("cls");
									admi.admi_agentshow();
								}
								std::cout << "还要进行其它操作吗？(按0退出)" << endl
									<< "1.查看商品信息                             2.查看用户信息" << endl
									<< "3.查看管理员信息                           4.录入商品信息" << endl
									<< "5.搜索商品信息                             6.查看代理商信息" << endl;
								std::cin >> flag_admis;
								if (flag_admis)
									system("cls");
							} while (flag_admis != 0);
						}
					} while (!value);
				}
			}
			else if (admi_step == 2)
			{
				admi.signin();
				std::cout << "您要继续登录吗？(Y or N)" << endl;
				char touch;
				std::cin >> touch;
				if (touch == 'Y')
				{
					system("cls");
					int admi_sort = 0;
					std::cout << "请输入您的管理员序号:" << endl;
					std::cin >> admi_sort;
					if (admi.loadup())
					{
						std::cout << "1.查看商品信息                             2.查看用户信息" << endl
							<< "3.查看管理员信息                           4.录入商品信息" << endl
							<< "5.搜索商品信息                             6.查看代理商信息" << endl;
						std::cout << "输入0退出" << endl;
						std::cin >> flag_admis;
						do {
							if (flag_admis == 1)
							{
								system("cls");
								admi.admi_proshow();
							}
							else if (flag_admis == 2)
							{
								system("cls");
								admi.admi_usershow();
							}
							else if (flag_admis == 3)
							{
								system("cls");
								admi.show_info();
							}
							else if (flag_admis == 4)
							{
								system("cls");
								admi.admi_prostore();
							}

							else if (flag_admis == 5)
							{
								system("cls");
								admi.admi_prosearch();
							}
							else if (flag_admis == 6)
							{
								system("cls");
								admi.admi_agentshow();
							}
							std::cout << "还要进行其它操作吗？(按0退出)" << endl
								<< "1.查看商品信息                             2.查看用户信息" << endl
								<< "3.查看管理员信息                           4.录入商品信息" << endl
								<< "5.搜索商品信息                             6.查看代理商信息" << endl;
							std::cin >> flag_admis;
							if (flag_admis)
								system("cls");
						} while (flag_admis != 0);
					}
					else
					{
						std::cout << "请检查您的账号和密码！" << endl;
					}
				}
				else if (touch == 'N')
				{
					std::cout << "欢迎再次使用！" << endl;
				}
			}
		}
		else if (flag_login == 2)
		{
			int user_step = 0;
			std::cout << "请选择您的业务:" << endl;
			std::cout << "1.用户登录                                          2.用户注册" << endl;
			std::cin >> user_step;
			if (user_step == 1)
			{
				system("cls");
				int user_sort = 0;
				std::cout << "请输入您的用户序号:" << endl;
				std::cin >> user_sort;
				bool valuex;
				if (valuex = use.loadup())
				{
					std::cout << "请选择您要执行的功能:" << endl;
					std::cout << "1.仅查看商品信息                             2.搜索商品" << endl
						<< "3.消费结算                                   4.选择商品(待完善)" << endl;
					std::cout << "输入0退出" << endl;
					std::cin >> flag_users;
					do {
						system("cls");
						if (flag_users == 1)
						{
							use.user_proshow();
						}
						else if (flag_users == 2)
						{
							system("cls");
							use.user_prosearch();
						}
						else if (flag_users == 3)
						{
							system("cls");
							use.settle();
						}
						/*else if (flag_users == 4)
						{
							use.get_product();
						}*/
						std::cout << "还要进行其它操作吗？(按0退出)" << endl
							<< "1.仅查看商品信息                             2.搜索商品" << endl
							<< "3.消费结算                                   4.选择商品(待完善)" << endl;
						std::cin >> flag_users;
						if (flag_users)
							system("cls");
					} while (flag_users != 0);
				}
				else
				{
					std::cout << "请检查您的账号和密码！" << endl;
					int user_sort = 0;
					std::cout << "请输入您的用户序号:" << endl;
					std::cin >> user_sort;
					bool valuev;
					do {
						
						if (valuev = use.loadup())
						{
							system("cls");
							std::cout << "请选择您要执行的功能:" << endl;
							std::cout << "1.仅查看商品信息                             2.搜索商品" << endl
								<< "3.消费结算                                   4.选择商品(待完善)" << endl;
							std::cout << "输入0退出" << endl;
							std::cin >> flag_users;
							do {
								if (flag_users == 1)
								{
									system("cls");
									use.user_proshow();
								}
								else if (flag_users == 2)
								{
									system("cls");
									use.user_prosearch();
								}
								else if (flag_users == 3)
								{
									system("cls");
									use.settle();
								}
								/*else if (flag_users == 4)
								{
									use.get_product();
								}*/
								std::cout << "还要进行其它操作吗？" << endl
									<< "1.仅查看商品信息                             2.搜索商品" << endl
									<< "3.消费结算                                   4.选择商品(待完善)" << endl;
								std::cout << "输入0退出" << endl;
								std::cin >> flag_users;
								if (flag_users)
								{
									system("cls");
								}
							} while (flag_users != 0);
						}
					} while (!valuev);
				}
			}
			else if (user_step == 2)
			{
				use.signin();
				std::cout << "您要继续登录吗？(Y or N)" << endl;
				char touch;
				std::cin >> touch;
				if (touch == 'Y')
				{
					system("cls");
					int user_sort = 0;
					std::cout << "请输入您的用户序号:" << endl;
					std::cin >> user_sort;
					if (use.loadup())
					{
						std::cout << "请选择您要执行的功能:" << endl;
						std::cout << "1.仅查看商品信息                             2.搜索商品" << endl
							<< " 3.消费结算                                  4.选择商品(待完善)" << endl;
						std::cout << "输入0退出" << endl;
						std::cin >> flag_users;
						do {
							if (flag_users == 1)
							{
								system("cls");
								use.user_proshow();
							}
							else if (flag_users == 2)
							{
								system("cls");
								use.user_prosearch();
							}
							else if (flag_users == 3)
							{
								system("cls");
								use.settle();
							}
							/*else if (flag_users == 4)
							{
								use.get_product();
							}*/
							std::cout << "还要进行其它操作吗？(按0退出)" << endl
								<< "1.仅查看商品信息                             2.搜索商品" << endl
								<< "3.消费结算                                   4.选择商品(待完善)" << endl;
							std::cin >> flag_users;
							if (flag_users)
							{
								system("cls");
							}
						} while (flag_users != 0);
					}
					else
					{
						std::cout << "请检查您的账号和密码！" << endl;

					}
				}
				else if (touch == 'N')
				{
					std::cout << "欢迎再次使用！" << endl;
				}
			}
		}
		else if (flag_login == 3)
		{
			int agent_step = 0;
			std::cout << "请选择您要进行的操作:" << endl
				<< "1.代理商登录                        2.代理商注册" << endl;
			std::cin >> agent_step;
			system("cls");
			if (agent_step == 1)
			{
				if (agent.loadup())
				{

					std::cout << "请选择您要执行的功能:" << endl
						<< "1.查看商品信息                     2.选择批发商品" << endl
						<< "3.显示代理商信息                   4.显示加盟商信息" << endl;
					std::cout << "输入0退出" << endl;
					int agent_choose = 0;
					std::cin >> agent_choose;
					do
					{
						if (agent_choose == 1)
						{
							system("cls");
							agent.agency_showpro();
						}
						else if (agent_choose == 2)
						{
							system("cls");
							agenunion tempo;
							double disacount = 0.0;
							if (change == 'A')
							{
								std::cout << "您是否和其它加盟商有合作？(0 or 1)" << endl;
								std::cout << "B商为1，C商为2" << endl;
								int adjust_if = 0;
								std::cin >> adjust_if;
								if (adjust_if == 1)
								{
									int cooperation = 0;
									std::cin >> cooperation;
									tempo = group[0] * group[cooperation];

									disacount = tempo.get_discount();
									agent.agency_choose(disacount);
								}
								else
								{
									disacount = group[0].get_discount();
									agent.agency_choose(disacount);
								}
							}
							else if (change == 'B')
							{
								std::cout << "您是否和其它加盟商有合作？(0 or 1)" << endl;
								std::cout << "A商为0，C商为2" << endl;
								int adjust_if = 0;
								std::cin >> adjust_if;
								if (adjust_if == 1)
								{
									int cooperation = 0;
									std::cin >> cooperation;
									tempo = group[1] * group[cooperation];

									disacount = tempo.get_discount();
									agent.agency_choose(disacount);
								}
								else
								{
									disacount = group[1].get_discount();
									agent.agency_choose(disacount);
								}
							}
							else if (change == 'C')
							{
								std::cout << "您是否和其它加盟商有合作？(0 or 1)" << endl;
								std::cout << "A商为0，B商为1" << endl;
								int adjust_if = 0;
								std::cin >> adjust_if;
								if (adjust_if == 1)
								{
									int cooperation = 0;
									std::cin >> cooperation;
									tempo = group[2] * group[cooperation];

									disacount = tempo.get_discount();
									agent.agency_choose(disacount);
								}
								else
								{
									disacount = group[2].get_discount();
									agent.agency_choose(disacount);
								}
							}
						}
						else if (agent_choose == 3)
						{
							system("cls");
							agent.show_info();
						}
						else if (agent_choose == 4)
						{
							system("cls");
							group[0].union_showinfo();
						}
						std::cout << "还要进行其他操作吗:" << endl
							<< "1.查看商品信息                     2.选择批发商品" << endl
							<< "3.显示代理商信息                   4.显示加盟商信息" << endl;
						std::cout << "输入0退出" << endl;
						std::cin >> agent_choose;
						if (agent_choose)
						{
							system("cls");
						}
					} while (agent_choose != 0);
				}
				else
				{
					std::cout << "登录失败！" << endl;
					bool value0 = true;
					do
					{
						if (value0 = agent.loadup())
						{
							system("cls");
							std::cout << "请选择您要执行的功能:" << endl
								<< "1.查看商品信息                     2.选择批发商品" << endl
								<< "3.显示代理商信息                   4.显示加盟商信息" << endl;
							std::cout << "输入0退出" << endl;
							int agent_choose = 0;
							std::cin >> agent_choose;
							do
							{
								if (agent_choose == 1)
								{
									system("cls");
									agent.agency_showpro();
								}
								else if (agent_choose == 2)
								{
									system("cls");
									agenunion tempo;
									double disacount = 0.0;
									if (change == 'A')
									{
										std::cout << "您是否和其它加盟商有合作？(0 or 1)" << endl;
										std::cout << "B商为1，C商为2" << endl;
										int adjust_if = 0;
										std::cin >> adjust_if;
										if (adjust_if == 1)
										{
											int cooperation = 0;
											std::cin >> cooperation;
											tempo = group[0] * group[cooperation];

											disacount = tempo.get_discount();
											agent.agency_choose(disacount);
										}
										else
										{
											disacount = group[0].get_discount();
											agent.agency_choose(disacount);
										}
									}
									else if (change == 'B')
									{
										std::cout << "您是否和其它加盟商有合作？(0 or 1)" << endl;
										std::cout << "A商为0，C商为2" << endl;
										int adjust_if = 0;
										std::cin >> adjust_if;
										if (adjust_if == 1)
										{
											int cooperation = 0;
											std::cin >> cooperation;
											tempo = group[1] * group[cooperation];

											disacount = tempo.get_discount();
											agent.agency_choose(disacount);
										}
										else
										{
											disacount = group[1].get_discount();
											agent.agency_choose(disacount);
										}
									}
									else if (change == 'C')
									{
										std::cout << "您是否和其它加盟商有合作？(0 or 1)" << endl;
										std::cout << "A商为0，B商为1" << endl;
										int adjust_if = 0;
										std::cin >> adjust_if;
										if (adjust_if == 1)
										{
											int cooperation = 0;
											std::cin >> cooperation;
											tempo = group[2] * group[cooperation];

											disacount = tempo.get_discount();
											agent.agency_choose(disacount);
										}
										else
										{
											disacount = group[2].get_discount();
											agent.agency_choose(disacount);
										}
									}
								}
								else if (agent_choose == 3)
								{
									system("cls");
									agent.show_info();
								}
								else if (agent_choose == 4)
								{
									system("cls");
									group[0].union_showinfo();
								}
								std::cout << "还要进行其他操作吗:" << endl
									<< "1.查看商品信息                     2.选择批发商品" << endl
									<< "3.显示代理商信息                   4.显示加盟商信息" << endl;
								std::cout << "输入0退出" << endl;
								std::cin >> agent_choose;
								if (agent_choose)
								{
									system("cls");
								}
							} while (agent_choose != 0);
						}
					} while (!value0);
				}
			}
			if (agent_step == 2)
			{
				agent.signin();
				std::cout << "您要继续登录吗:(Y or N)" << endl;
				char IF = 0;
				std::cin >> IF;
				if (IF == 'Y')
				{
					system("cls");
					if (agent.loadup())
					{

						std::cout << "请选择您要执行的功能(按0退出):" << endl
							<< "1.查看商品信息                     2.选择批发商品" << endl
							<< "3.显示代理商信息                   4.显示加盟商信息" << endl;
						int agent_choose = 0;
						std::cin >> agent_choose;
						do
						{
							if (agent_choose == 1)
							{
								system("cls");
								agent.agency_showpro();
							}
							else if (agent_choose == 2)
							{
								system("cls");
								double disacount = 0.0;
								agenunion temp;
								if (change == 'A')
								{
									std::cout << "您是否和其它加盟商有合作？(0 or 1)" << endl;
									std::cout << "B商为1，C商为2" << endl;
									int adjust_if = 0;
									std::cin >> adjust_if;
									if (adjust_if == 1)
									{
										int cooperation = 0;
										std::cin >> cooperation;

										temp = group[0] * group[cooperation];

										disacount = temp.get_discount();
										agent.agency_choose(disacount);
									}
									else
									{
										disacount = group[0].get_discount();
										agent.agency_choose(disacount);
									}
								}
								else if (change == 'B')
								{
									std::cout << "您是否和其它加盟商有合作？(0 or 1)" << endl;
									std::cout << "A商为0，C商为2" << endl;
									int adjust_if = 0;
									std::cin >> adjust_if;
									if (adjust_if == 1)
									{
										int cooperation = 0;
										std::cin >> cooperation;
										temp = group[1] * group[cooperation];

										disacount = temp.get_discount();
										agent.agency_choose(disacount);
									}
									else
									{
										disacount = group[1].get_discount();
										agent.agency_choose(disacount);
									}
								}
								else if (change == 'C')
								{
									std::cout << "您是否和其它加盟商有合作？(0 or 1)" << endl;
									std::cout << "A商为0，B商为1" << endl;
									int adjust_if = 0;
									std::cin >> adjust_if;
									if (adjust_if == 1)
									{
										int cooperation = 0;
										std::cin >> cooperation;
										temp = group[2] * group[cooperation];

										disacount = temp.get_discount();
										agent.agency_choose(disacount);
									}
									else
									{
										disacount = group[2].get_discount();
										agent.agency_choose(disacount);
									}
								}
							}
							else if (agent_choose == 3)
							{
								system("cls");
								agent.show_info();
							}
							else if (agent_choose == 4)
							{
								system("cls");
								if (change == 'A')
									group[0].union_showinfo();
								if (change == 'B')
									group[1].union_showinfo();
								if (change == 'C')
									group[2].union_showinfo();
							}
							std::cout << "还要进行其他操作吗:" << endl
								<< "1.查看商品信息                     2.选择批发商品" << endl
								<< "3.显示代理商信息                   4.显示加盟商信息" << endl;
							std::cout << "输入0退出" << endl;
							std::cin >> agent_choose;
						} while (agent_choose);
					}
					if (IF == 'N')
					{
						std::cout << "欢迎下次使用！" << endl;

					}
				}
			}
		}
		system("cls");
		std::cout << "要继续使用吗(输入0退出,1继续)：" << endl;
		//std::cout << "1.管理员         2.用户          3.代理商"<<endl;
		std::cin >> flag_login;
	} while (flag_login);
	/*if (flag_login)
	{
		system("cls");
	}*/
	return 0;

}