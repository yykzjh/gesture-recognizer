import pandas as pd
import numpy as np



def processDataset(filePath,fileName):
    dataset = pd.read_excel(filePath+fileName,sheet_name=0)

    dataset.iloc[::4,:].to_excel(filePath+r"处理后的数据集/P_"+fileName,index=False)












if __name__ == "__main__":
    fileNames = ["组合-0-1-2-3-4-握拳-点赞","组合-1-3-4-2-0-4-握拳-点赞","组合-3-0-握拳-点赞-1-2-3","组合-点赞-1-3-2-4-0-握拳(2)",
    "组合-点赞-1-3-2-4-0-握拳","组合-点赞-握拳-0-4-3-2-1","组合-握拳-4-0-4-点赞-握拳-点赞-0","校正"]
    for filename in fileNames:
        processDataset(r"./第二次手套数据/手套1/第8组/",r"手套1-8次-"+filename+r".xlsx")
    





