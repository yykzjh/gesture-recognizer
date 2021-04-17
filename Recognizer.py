import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from time import *
from Segment import input_data, dynamic_segment_data


def Dtw(data, model):

    #将dataframe类型转换为array类型并且确定长短数据
    if len(data)>len(model):     
        longData = data.values
        shortData = model.values
    else:
        longData = model.values
        shortData = data.values
    # print(longData)
    # print(shortData)

    if longData.shape[0] > 2 * shortData.shape[0] :
        return float('inf') #如果待识别手势序列长度和模板数据长度差距超过2倍则直接算没匹配上

    #归一化数据矩阵
    # longData = (longData - np.min(longData)) / (np.max(longData) - np.min(longData))
    # shortData = (shortData - np.min(shortData)) / (np.max(shortData) - np.min(shortData))
    
    dp = np.zeros((longData.shape[0],shortData.shape[0])) #定义动态规划矩阵
    for i in range(dp.shape[0]): #初始化距离值
        for j in range(int(i/2),min(2*i+1,dp.shape[1]),1):
            dp[i][j] = np.linalg.norm(longData[i,:] - shortData[j,:])
    
    #进行动态规划找到最优路径和最优值
    for i in range(dp.shape[0]): 
        for j in range(int(i/2),min(2*i+1,dp.shape[1]),1): #遍历有效区域
            if (j-1) >= 0: #前一列存在
                minn = float('inf') #初始化最小值变量
                for k in range(i-2,i+1): #遍历包括当前行的前三行
                    if k >= 0 and (j-1) >= int(k/2) and (j-1) <= 2*k: #前一路径也要存在有效区域内
                        minn = min(minn,dp[k][j-1]) #维护最小值
                dp[i][j] += minn #修改当前路劲最小值
    
    return dp[-1][-1]/dp.shape[1]
    


def match_distance(data, model):
    #数据转换成数组形式
    dataarr = data.values
    modelarr = model.values

    return np.sum(np.linalg.norm(dataarr-modelarr,axis=1)) / 3
    



if __name__ == "__main__":
    begin_time = time()

    models = pd.read_excel(r"./手势分割数据/models.xlsx",sheet_name=None) #读入模板数据
    # print(models)
    data = input_data(r"./手势数据/正斜圆正斜矩.xlsx") #读入待识别手势数据
    slices = dynamic_segment_data(data) #将待识别手势数据进行分割

    for i in range(len(slices)): #对分割出的每个手势序列分别进行识别
        distance = dict() #用于保存当前待识别的手势序列和不同手势模板的距离
        for k,v in models.items(): #与不同的手势模板比较
            distance[k] = Dtw(data.iloc[slices[i].start:slices[i].end,:],v) #用Dtw求手势序列和手势模板的距离
        if distance[min(distance,key=distance.get)] == float('inf'):
            print("不存在该手势的模板") #所有模板都没匹配上
        else:      
            print(min(distance,key=distance.get)) #打印与当前待识别手势序列距离最短的模板类型

    end_time = time()
    print("该程序运行时间为{:.5f}秒".format(end_time-begin_time))