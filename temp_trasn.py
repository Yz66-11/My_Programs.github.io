from unicodedata import category
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore

#读取Excel文件
data1=pd.read_excel('排名前三国家.xlsx', sheet_name='Sheet1')
data2=pd.read_excel('排名前三国家.xlsx', sheet_name='Sheet2')
np1,np2,np3, nummy1, nummy2,nummy3=[],[],[],[],[],[]
categories=[1, 2, 4, 5]
bar_width=0.3
nummy1=data1['美国']
nummy2=data1['中国']
nummy3=data1['日本']
np1=data2['美国']
np2=data2['中国']
np3=data2['日本']
print(nummy1, nummy2, nummy3)

#创建图形
fig = plt.figure()
ax1 = fig.add_subplot(1, 2, 1)
ax2 = fig.add_subplot(1, 2,2)
                      
ax1.bar(categories, nummy1, bar_width, label='美国')
ax1.bar([x + bar_width for x in categories], nummy2, bar_width, label='中国')
ax1.bar([x + 2*bar_width for x in categories], nummy3, bar_width, label='日本')

ax2.bar(categories, np1, bar_width, label='美国')
ax2.bar([x + bar_width for x in categories], np2, bar_width, label='中国')
ax2.bar([x + 2*bar_width for x in categories], np3, bar_width,label='日本')
        
# 设置x轴刻度位置
ax1.set_xticks([x + bar_width for x in categories])
ax1.set_xticklabels([2018, 2019, 2020,2021,2022])
ax2.set_xticks([x + bar_width for x in categories])
ax2.set_xticklabels([2018, 2019,2020,2021,2022])

plt.rcParams['font.sans-serif']=['SimHei']
# 添加图例和标签
ax1.set_title('2018-2022gdp排名前三的国家的gdp的数据的多柱形图')
ax2.set_title('2018-2022gdp排名前三的国家的人口数的数据的多柱形图')

ax1.set_xlabel('年份')
ax2.set_xlabel('年份')

ax1.set_ylabel('GDP/万亿美元')
ax2.set_ylabel('人口数/亿人')

ax1.legend()
ax2.legend()
#显示两个图表
plt.show()
