# -*- coding:utf-8 -*-
import pymysql.cursors
import pandas as pd


# -*- coding:utf-8 -*-
'''
    603个数据
    上轨线 （UP）
    中轨线（MB) 20天移动平均线
    下轨线 (DN)
    '''

'''
    RSI=A／（A+B）*100
    A是涨幅
    B是跌幅
    '''

'''
    买入信号：
    1. shRSI<50,shRSI>lgRSI（形成交叉点）,close>MB
    卖出信号：
    1. shRSI<70,shRSI<lgRSI（形成交叉点）
    2.close<MB（形成交叉点）
    卖出警告：
    1.close<UP（形成交叉点）
    '''

'''
    买入信号：1
    卖出信号：2
    卖出警告：3
    '''

import pandas as pd
import stockstats
import matplotlib.pyplot as plt
import matplotlib
import sys
reload(sys)
import warnings
warnings.filterwarnings("ignore")
sys.setdefaultencoding('utf-8')
matplotlib.rcParams['font.sans-serif']=['SimHei'] # 用来正常显示中文标签
matplotlib.rcParams['axes.unicode_minus']=False # 用来正常显示负号

#计算RSI函数
def caculate_RSI(up, down, day):
    roll_up = pd.rolling_sum(up.shift(1), day)
    roll_down = pd.rolling_sum(down.shift(1).abs(), day)
    RS = roll_up / roll_down
    RSI = 100.0 - (100.0 / (1.0 + RS))
    return RSI

#计算买入卖出信号函数
def calculate_sellOrbuy(data):
    data = pd.concat([data, pd.DataFrame(columns=['predict'])])
    data = data[
                ['close', 'bl_mid', 'bl_top', 'bl_bottom', 'bottom', 'up', 'shRSI', 'lgRSI', 'predict', 'change', 'date']]
                shRSI_lgRSI_g =0  # 长期和短期RSI信号,金叉为1
                
                shRSI_flag = 0 # 短期下穿70线为1
                
                for i in range(len(data)-1):
                    if i == 0 :
                        continue
                            j=i+1
                                # 买入：1
                                if (data.iloc[i:i + 1, 6:7].values < 50):
                                    if (data.iloc[i:i + 1, 6:7].values < data.iloc[i:i + 1, 7:8].values) and (data.iloc[i-1:i , 6:7].values > data.iloc[i-1:i, 7:8].values):
                                        shRSI_lgRSI_g = 1
                                            elif((data.iloc[i:i+1 , 6:7].values > data.iloc[i:i+1, 7:8].values)):
                                                shRSI_lgRSI_g = 0
                                                    if (data.iloc[i:i + 1, 0:1].values > data.iloc[i:i + 1,1:2].values) and shRSI_lgRSI_g == 1:
                                                        data.iloc[j:j + 1, 8:9] = 1
                                                            shRSI_lgRSI_g = 0
                                                                # 卖出：2
                                                                if (data.iloc[i-1:i , 6:7].values > 70)and(data.iloc[i:i + 1, 6:7].values < 70) and shRSI_flag == 0: #短期RSI下穿70
                                                                    shRSI_flag = 1
                                                                        elif (data.iloc[i:i + 1, 6:7].values > 70):
                                                                            shRSI_flag=0
                                                                                if (data.iloc[i-1:i , 6:7].values < data.iloc[i-1:i , 7:8].values) and (data.iloc[i:i + 1, 6:7].values > data.iloc[i:i + 1, 7:8].values) and shRSI_flag==1:
                                                                                    data.iloc[j:j + 1, 8:9] = 2
                                                                                        shRSI_flag=0#归零
                                                                                            if ((data.iloc[i:i + 1, 0:1].values > data.iloc[i:i + 1, 1:2].values)) and ((data.iloc[i-1:i , 0:1].values < data.iloc[i-1:i, 1:2].values)):
                                                                                                data.iloc[j:j + 1, 8:9] = 2
                                                                                                    
                                                                                                    # 卖出警告：3
                                                                                                    if (data.iloc[i:i + 1, 0:1].values > data.iloc[i:i + 1, 3:4].values) and ((data.iloc[i-1:i, 0:1].values < data.iloc[i-1:i, 3:4].values)):
                                                                                                        data.iloc[j:j + 1, 8:9] = 3
                                                                                                    data['predict'].fillna(0, inplace=True)
return data

# 回测收益曲线函数
def back(data,init_cap):
    data['position'] = 0 # 初始化当前仓位
        data['return'] = 1 # 相对上一个交易日的资金变化程度
        for i in range(len(data)):
            if (data.loc[i,'predict'] == 1) & (data.loc[max(i-1,0),'position'] == 0):
                data.loc[i,'position'] = 1
                if (data.loc[i,'predict'] == 2) & (data.loc[max(i-1,0),'position'] == 1):
                    data.loc[i,'position'] = 0
                if (data.loc[i,'predict'] == 0):
                    data.loc[i,'position'] = data.loc[max(i-1,0),'position']
    data['return'] = data['change'] /data['close'].astype('float')* data['position'].shift(1)
        data['capital_return'] = init_cap * (data['return'] + 1).cumprod()
        plt.plot(data['capital_return'])
        plt.legend()
        plt.title('回测收益曲线 x单位：万元',fontsize=20)
        plt.show()
        
        return data

short_day = 6  # 短期RSI时长
long_day = 12  # 长期RSI时长

#data=pd.read_csv('000514.csv',sep=',')
connect = pymysql.Connect(
                          host='localhost',
                          port=, #输入端口号
                          user=' ', #输入用户名
                          passwd=' ', #输入密码
                          db='test', #输入数据库名称
                          charset='utf8'  #输入编码方式
                          )


# 获取游标
cursor = connect.cursor()

sql = "SELECT * from myfruit"
row_list=[]
cursor.execute(sql)
for row in cursor.fetchall():
    row_tmp=list(row)
    row_list.append(row_tmp)

data=pd.DataFrame(row_list,columns=['date','close'])

#计算涨跌
data['change']=data['close'].astype(float)-data['close'].astype(float).shift(1)

#计算BOLL(26,2)
data['bl_mid']=pd.rolling_mean(data['close'].shift(1),26)
data['std']=pd.rolling_std(data['close'].shift(1),26)
data['bl_top']=data['bl_mid']+2*data['std']
data['bl_bottom']=data['bl_mid']-2*data['std']

#计算长短期RSI
up, bottom = data['change'].copy(), data['change'].copy()
up[up < 0] = 0
bottom[bottom > 0] = 0
data['up'] = up
data['bottom'] = bottom

data['shRSI'] = caculate_RSI(data['up'], data['bottom'], short_day)
data['lgRSI'] = caculate_RSI(data['up'], data['bottom'], long_day)

#计算买入卖出信号
data=calculate_sellOrbuy(data)

#data[['shRSI','lgRSI','bl_mid', 'bl_top', 'bl_bottom','close']].plot()

data.to_csv('result.csv', index=False)

buy = data[data['predict'] == 1]
print "买入时期为："
print buy['date'].values

sell= data[data['predict'] == 2]
print "卖出时期为："
print sell['date'].values

back(data,init_cap=10000)
