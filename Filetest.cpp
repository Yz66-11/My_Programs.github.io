#include<fstream>
#include<string>
#include<iostream>
#include<stdlib.h>
using namespace std;
int main()
{
	string filename;
	cin >> filename;
	ofstream in(filename);
	in << "abcdef" << endl
		<< "ghijklmn";
	in.close();
	ifstream out0(filename);
	string filenames;
	cin >> filenames;
	ofstream out(filenames);
	char* ch = new char[30];
	int i = 0;
	ch[0] = { '0' };
	while (!out0.eof())
	{
		out0 >> ch[i];
		ch[i] = ch[i] - 32;
		i++;
	}
	i = 0;
	while (1)
	{
		out << *(ch + i);
		i++;
		if (ch[i - 1] == 'F')
		{
			out << endl;
		}
		if (ch[i - 1] == 'N')
			break;
	}
	out0.close();
	out.close();
	return 0;
}