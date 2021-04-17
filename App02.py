import sys
import os
import math
import numpy as np
import serial
import serial.tools.list_ports
import binascii
import struct
import threading
import pandas as pd
from time import sleep
from Recognizer import Dtw
# from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, QToolTip,
#     QMessageBox, QDesktopWidget, QHBoxLayout, QVBoxLayout, QApplication, 
#     QGridLayout, QLabel, QLineEdit, QTextEdit, QLCDNumber, QSlider, QInputDialog, 
#     QFrame, QColorDialog, QSizePolicy, QAction, QFileDialog, QFontDialog, 
#     QCheckBox, QSlider, QProgressBar, QCalendarWidget, QSplitter, QStyleFactory, QComboBox, 
#     QTableWidget)
from PyQt5.QtWidgets import *
from PyQt5.QtGui import (QFont, QIcon, QPixmap)
# from PyQt5.QtCore import (pyqtSignal, QObject, QCoreApplication, Qt, QBasicTimer, QDate)
from PyQt5.QtCore import *



def find(list, char):
    for index, item in enumerate(list):
        if item==char:
            return index
    return "not find"


class SerialPort:
    def __init__(self, port, buand):
        self.port = serial.Serial(port, buand,timeout=5)
        global serial_is_open
        serial_is_open = True
        if not self.port.isOpen():
            self.port.open()

    def port_open(self):
        global serial_is_open
        serial_is_open = True
        if not self.port.isOpen():
            self.port.open()

    def port_close(self):
        global serial_is_open
        serial_is_open = False
        self.port.close()

    def read_data(self):
        global serial_is_open
        global gestureData
        data_bytes=bytearray()

        serial_is_open = True
        while serial_is_open:
            count = self.port.inWaiting()
            if count > 0:
                rec_str = self.port.read(count)
                data_bytes += rec_str
                # print(len(data_bytes))
                i = 0
                while (len(data_bytes)-i)>=20:
                    if data_bytes[i]==0x55 and data_bytes[i+1]==0x61:
                        ax = struct.unpack('<h',data_bytes[i+2:i+4])[0]
                        ay = struct.unpack('<h',data_bytes[i+4:i+6])[0]
                        az = struct.unpack('<h',data_bytes[i+6:i+8])[0]
                        ax = ax / 32768 * 16
                        ay = ay / 32768 * 16
                        az = az / 32768 * 16
                        gestureData = gestureData.append([{'ax':ax,'ay':ay,'az':az}],ignore_index=True)
                        i += 20
                    else:
                        i += 1
                data_bytes[:i] = b''
            # print(gestureData.shaape)
            # sleep(1)


class WorkThread(QThread):
    #初始化线程
    def __init__(self):
        super(WorkThread, self).__init__()
    #线程运行函数
    def run(self):
        gestureDataSrc = pd.read_excel(r"./手套数据/手套传感器5列数据拼接3列加速度数据.xlsx",usecols="A:H",columns=['大拇指','食指','中指','无名指','小指','ax','ay','az']) #手势数据的集合形式
        ind = 0
        global gestureData
        while ind<gestureDataSrc.shape[0]:
            if (ind+10)<gestureDataSrc.shape[0]:
                gestureDataSlice = gestureDataSrc.iloc[ind:ind+10,:]
                gestureDataSlice.columns = ['大拇指','食指','中指','无名指','小指','ax','ay','az']
                gestureData = pd.concat([gestureData, gestureDataSlice])
                ind+=10
            else:
                gestureDataSlice = gestureDataSrc.iloc[ind:gestureDataSrc.shape[0],:]
                gestureDataSlice.columns = ['大拇指','食指','中指','无名指','小指','ax','ay','az']
                gestureData = pd.concat([gestureData, gestureDataSlice])
                ind = gestureDataSrc.shape[0]
            sleep(1)


class Recognizer(QWidget):
    
    def __init__(self):
        super().__init__()
        self.cwd = os.getcwd() # 获取当前程序文件位置
        self.initUI()
        
        
    def initUI(self):
        self.setStyleSheet("background-color:#fefcf0;")
        hbox = QHBoxLayout(self) #定义框布局

        leftFrame = QFrame(self) #定义左框架
        leftFrame.setMaximumWidth(1000)
        leftFrame.setFrameShape(QFrame.StyledPanel)

        rightFrame = QFrame(self) #定义右框架
        rightFrame.setMaximumWidth(800)
        rightFrame.setFrameShape(QFrame.StyledPanel)

        splitter = QSplitter(Qt.Horizontal) #定义子控件边界可变
        splitter.addWidget(leftFrame) #将左框架添加到可变边界
        splitter.addWidget(rightFrame) #将右框架添加到可变边界

        hbox.addWidget(splitter) #为主窗口添加可变边界控件
        self.setLayout(hbox) #为主窗口设置布局

        leftBoxLayout = QVBoxLayout() #左边总体垂直框布局
        leftBoxLayout.setContentsMargins(50, 20, 50, 20) #设置左边总体布局的内边界
        
        label1 = QLabel("手势数据") #手势数据的标题
        label1.setAlignment(Qt.AlignCenter) #手势数据标题水平居中
        label1.setStyleSheet("font-size:24px;font-weight:bold;font-family:Microsoft YaHei") #手势数据标题字体样式
        leftBoxLayout.addWidget(label1,2) #手势数据标题添加到布局

        leftFrame.setLayout(leftBoxLayout) #将左边的总体垂直布局添加到左框架

        # gestureData = pd.read_excel(r"./手势分割数据/7.xlsx",usecols="B:D") #手势数据的集合形式
        # gestureDataString = "" #手势数据的字符串形式
        # for index, row in gestureData.iterrows(): #遍历手势数据转换格式
        #     for i in range(row.shape[0]):
        #         gestureDataString += str(row[i])+"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" #每列数据用空格分隔
        #     gestureDataString += "<br>" #每行数据换行
        # gestureDataString += "......"
        
        # gestureDataBox = QTextEdit() #显示手势数据的文本框
        # gestureDataBox.setStyleSheet("font-size:16px;font-family:Arial;padding:20 20 20 20;")
        # gestureDataBox.setMaximumHeight(400) #设置手势数据框最大高度
        # gestureDataBox.setAlignment(Qt.AlignCenter) #设置手势数据文本框水平居中
        # gestureDataBox.setHtml(gestureDataString) #设置手势数据的内容
        # gestureDataBox.setReadOnly(True) #设置手势数据文本框不可编辑
        
        self.table1 = QTableWidget()
        self.table1.setColumnCount(8)
        self.table1.setMaximumHeight(400) #设置手势数据框最大高度
        self.table1.setShowGrid(False)
        self.table1.verticalHeader().setVisible(False)
        self.table1.horizontalHeader().setVisible(False)
        self.table1.setStyleSheet("font-size:16px;font-family:Arial;text-align:center;padding-left:15px;background-color:auto;")
        self.table1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # for j in range(8):
        #     self.table1.horizontalHeader().setSectionResizeMode(j, QHeaderView.ResizeToContents)
        self.table1.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # gestureData = gestureData.values
        # for i in range(gestureData.shape[0]):
        #     self.table1.setRowHeight(i, 50)
        #     newItem = QTableWidgetItem(str(i))
        #     newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        #     self.table1.setItem(i, 0, newItem)
        #     for j in range(gestureData.shape[1]):
        #         newItem = QTableWidgetItem(str(gestureData[i][j]))
        #         newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        #         self.table1.setItem(i, j+1, newItem) # 设置表格内容(行,列,文本)

        leftBoxLayout.addWidget(self.table1,10) #将手势数据框添加到布局
        leftBoxLayout.addStretch(1) #添加一段占位空白

        lineBoxLayout1 = QHBoxLayout() #设置第一行功能的水平框布局
        lineBoxLayout2 = QHBoxLayout() #设置第二行功能的水平框布局
        lineBoxLayout3 = QHBoxLayout() #设置第三行功能的水平框布局
        lineBoxLayout4 = QHBoxLayout() #设置第四行功能的水平框布局

        label2 = QLabel("端口",) #第一行的功能
        label2.setWordWrap(True)
        label2.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        label2.setStyleSheet("font-size:20px;font-weight:bold;font-family:Microsoft YaHei") #各功能名称字体样式
        lineBoxLayout1.addWidget(label2,2) #第一行添加功能名
        lineBoxLayout1.addStretch(1) #添加空白占位

        label3 = QLabel("数据文件存储位置") #第二行的功能
        label3.setWordWrap(True)
        label3.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        label3.setStyleSheet("font-size:20px;font-weight:bold;font-family:Microsoft YaHei") #各功能名称字体样式
        lineBoxLayout2.addWidget(label3,2) #第二行添加功能名
        lineBoxLayout2.addStretch(1) #添加空白占位
        
        label4 = QLabel("识别") #第三行的功能
        label4.setWordWrap(True)
        label4.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        label4.setStyleSheet("font-size:20px;font-weight:bold;font-family:Microsoft YaHei") #各功能名称字体样式
        lineBoxLayout3.addWidget(label4,2) #第三行添加功能名
        lineBoxLayout3.addStretch(2) #添加空白占位

        label5 = QLabel("分割数据存储位置") #第四行的功能
        label5.setWordWrap(True)
        label5.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        label5.setStyleSheet("font-size:20px;font-weight:bold;font-family:Microsoft YaHei") #各功能名称字体样式
        lineBoxLayout4.addWidget(label5,2) #第四行添加功能名
        lineBoxLayout4.addStretch(1) #添加空白占位

        #第一行的功能控件
        combo1 = QComboBox()
        combo1.setMinimumHeight(50)
        combo1.setStyleSheet("font-size:16px;font-family:Microsoft YaHei;QAbstractItemView::item {height: 22px;}") #下拉列表字体样式
        combo1.setView(QListView())
        qleTmp = QLineEdit() #下面都是设置字体居中
        qleTmp.setStyleSheet("background-color:white;")
        qleTmp.setAlignment(Qt.AlignCenter)
        qleTmp.setReadOnly(True)
        combo1.setLineEdit(qleTmp)

        comboLists = ['COM3','COM1','COM2','COM4'] #下拉列表的项
        for item in comboLists:
            combo1.addItem(str(item)) #将各项添加到下拉列表中

        lineBoxLayout1.addWidget(combo1,3)
        lineBoxLayout1.addStretch(1) #添加空白占位

        btn1 = QPushButton("打开端口")
        btn1.setStyleSheet("font-size:16px;font-weight:550;font-family:Microsoft YaHei;background-color:white;") #按钮字体样式
        btn1.setMinimumHeight(50)
        lineBoxLayout1.addWidget(btn1,3)
        lineBoxLayout1.addStretch(1) #添加空白占位

        btn2 = QPushButton("关闭端口")
        btn2.setStyleSheet("font-size:16px;font-weight:550;font-family:Microsoft YaHei;background-color:white;") #按钮字体样式
        btn2.setMinimumHeight(50)
        lineBoxLayout1.addWidget(btn2,3)

        #第二行的功能控件
        self.qle1 = QLineEdit()
        self.qle1.setMinimumHeight(30)
        self.qle1.setPlaceholderText("可在本地电脑保存的地址(D:\\...)")
        self.qle1.setReadOnly(True)
        lineBoxLayout2.addWidget(self.qle1,11)

        self.openFileBtn1 = QPushButton()
        self.openFileBtn1.setStyleSheet("background-image:url(./images/materials/shengluehao.ico);\
            background-repeat:no-repeat;\
            background-position:center;\
            border: 1px solid grey")
        self.openFileBtn1.setMinimumHeight(30)
        self.openFileBtn1.clicked.connect(self.selectFile) #给打开文件按钮绑定点击事件
        lineBoxLayout2.addWidget(self.openFileBtn1)

        #第三行的功能控件
        btn3 = QPushButton("开始识别")
        btn3.setStyleSheet("font-size:16px;font-weight:550;font-family:Microsoft YaHei;background-color:white;") #按钮字体样式
        btn3.setMinimumHeight(50)
        btn3.clicked.connect(self.start_recognize)
        lineBoxLayout3.addWidget(btn3,3)
        lineBoxLayout3.addStretch(2) #添加空白占位

        btn4 = QPushButton("结束识别")
        btn4.setStyleSheet("font-size:16px;font-weight:550;font-family:Microsoft YaHei;background-color:white;") #按钮字体样式
        btn4.setMinimumHeight(50)
        btn4.clicked.connect(self.end_recognize)
        lineBoxLayout3.addWidget(btn4,3)
        lineBoxLayout3.addStretch(2) #添加空白占位

        #第四行的功能控件
        self.qle2 = QLineEdit()
        self.qle2.setMinimumHeight(30)
        self.qle2.setPlaceholderText("可在本地电脑保存的地址(D:\\...)")
        self.qle2.setStyleSheet("background-color:auto;")
        self.qle2.setReadOnly(True)
        lineBoxLayout4.addWidget(self.qle2,11)
        
        self.openFileBtn2 = QPushButton()
        self.openFileBtn2.setStyleSheet("background-image:url(./images/materials/shengluehao.ico);\
            background-repeat:no-repeat;\
            background-position:center;\
            border: 1px solid grey")
        self.openFileBtn2.setMinimumHeight(30)
        self.openFileBtn2.clicked.connect(self.selectFile) #给打开文件按钮绑定点击事件
        lineBoxLayout4.addWidget(self.openFileBtn2)

        #将各行功能添加到左边总布局中
        leftBoxLayout.addLayout(lineBoxLayout1,2)
        leftBoxLayout.addStretch(1) #添加一段占位空白
        # leftBoxLayout.addLayout(lineBoxLayout2,2)
        # leftBoxLayout.addStretch(1) #添加一段占位空白
        leftBoxLayout.addLayout(lineBoxLayout3,2)
        leftBoxLayout.addStretch(1) #添加一段占位空白
        leftBoxLayout.addLayout(lineBoxLayout4,2)


        rightBoxLayout = QVBoxLayout() #右边总体垂直框布局
        rightBoxLayout.setContentsMargins(30, 30, 30, 30) #设置右边总体布局的内边界
        
        label6 = QLabel("手势识别结果") #手势识别结果的标题
        label6.setAlignment(Qt.AlignHCenter) #手势识别结果标题水平居中
        label6.setStyleSheet("font-size:24px;font-weight:bold;font-family:Microsoft YaHei") #手势识别结果标题字体样式
        rightBoxLayout.addWidget(label6) #手势识别结果标题添加到布局

        rightFrame.setLayout(rightBoxLayout) #将右边的总体垂直布局添加到右框架

        label7 = QLabel("手势图片：") #显示手势图片的标题
        label7.setAlignment(Qt.AlignLeft) #手势图片标题左对齐
        label7.setStyleSheet("font-size:16px;font-weight:bold;font-family:Microsoft YaHei")
        rightBoxLayout.addWidget(label7) #手势图片标题添加到右布局

        pixmap1 = QPixmap("./images/materials/封面.png") #读入图片
        self.label8 = QLabel() #定义用于存放图片的标签
        self.label8.setPixmap(pixmap1) #将图片放入标签中
        self.label8.setMaximumHeight(350) #设置图片最大显示高度
        self.label8.setAlignment(Qt.AlignHCenter) #设置显示图片的标签水平居中
        self.label8.setScaledContents (True) #设置图片自适应标签大小
        self.label8.setStyleSheet("border:1px solid black;margin:0 200;"); #设置显示手势图片标签的样式
        rightBoxLayout.addWidget(self.label8) #将显示图片的标签添加到右布局

        lineBoxLayout5 = QHBoxLayout() #给手势含义设置水平箱布局
        rightBoxLayout.addLayout(lineBoxLayout5) #添加行布局到右边总布局 
        lineBoxLayout5.addStretch(4) #头部添加占位空白用于实现居中

        label9 = QLabel("手势含义:") #手势含义的标题
        label9.setStyleSheet("font-size:34px;font-weight:bold;font-family:Microsoft YaHei;margin-top:30px") #手势含义标题字体样式
        lineBoxLayout5.addWidget(label9,1) #手势含义标题添加到布局

        self.gestureMeans = QLabel("暂无结果") #定义标签保存识别的手势含义
        self.gestureMeans.setStyleSheet("font-size:30px;color:red;font-weight:bold;font-family:Microsoft YaHei;margin-top:30px") #手势含义结果字体样式
        lineBoxLayout5.addWidget(self.gestureMeans,1) #手势含义结果添加到布局
        lineBoxLayout5.addStretch(4) #头部添加占位空白用于实现居中

        label10 = QLabel("历史记录：") #显示历史记录的标题
        label10.setAlignment(Qt.AlignLeft) #历史记录标题左对齐
        label10.setStyleSheet("font-size:16px;font-weight:bold;font-family:Microsoft YaHei;")
        rightBoxLayout.addWidget(label10) #历史记录标题添加到右布局

        # historyData = [5,4,3,2,1,7,8,9,4,5,6,3,2,1,4,8,4,5,6,3,2,1,1,7,8,9,5,5,
        #                 3,6,4,8,9,5,1,2,3,7,8,9,4,5,6,3] #历史记录数组
        # historyDataString = "&nbsp;&nbsp;&nbsp;" #历史记录字符串
        # rowNum = 6 #每行显示记录个数
        # for index,item in enumerate(historyData):
        #     historyDataString += str(item)
        #     if (index+1)%rowNum==0 :
        #         historyDataString += "<br></br><br></br>&nbsp;&nbsp;&nbsp;" #显示一定量记录后换行
        #     else: #一行中的每个记录有间隔
        #         historyDataString += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"

        # historyDataBox = QTextEdit() #显示历史记录的文本框
        # historyDataBox.setMaximumHeight(200) #设置历史记录框最大高度
        # historyDataBox.setStyleSheet("font-size:20px;font-weight:500;font-family:Arial;margin:0 100 10 100;padding:20 0 20 20;")
        # historyDataBox.setAlignment(Qt.AlignCenter) #设置历史记录文本框水平居中
        # historyDataBox.setHtml(historyDataString) #设置历史记录的内容
        # historyDataBox.setReadOnly(True) #设置历史记录文本框不可编辑
        # rightBoxLayout.addWidget(historyDataBox) #将历史记录框添加到布局

        self.table2 = QTableWidget()
        self.table2.setColumnCount(4)
        self.table2.setShowGrid(False)
        self.table2.setMaximumHeight(200) #设置手势数据框最大高度
        self.table2.verticalHeader().setVisible(False)
        self.table2.horizontalHeader().setVisible(False)
        self.table2.setStyleSheet("font-size:36px;font-weight:500;font-family:Arial;background-color:auto;")
        self.table2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table2.setEditTriggers(QAbstractItemView.NoEditTriggers)

        lineBoxLayout6 = QHBoxLayout()
        lineBoxLayout6.addStretch(1)
        lineBoxLayout6.addWidget(self.table2,4)
        lineBoxLayout6.addStretch(1)
        rightBoxLayout.addLayout(lineBoxLayout6) #将历史记录框添加到布局
        
        lineBoxLayout5 = QHBoxLayout() #翻译和清空功能的框布局
        lineBoxLayout5.addStretch(4) #添加空白占位

        btn5 = QPushButton("翻译") #翻译按钮
        btn5.setStyleSheet("font-size:16px;font-weight:550;font-family:Microsoft YaHei;background-color:white;") #按钮字体样式
        btn5.setMinimumHeight(50) #设置按钮最小高度
        btn5.clicked.connect(self.translate)
        lineBoxLayout5.addWidget(btn5,2) #将按钮添加到行布局
        lineBoxLayout5.addStretch(2) #添加空白占位

        btn6 = QPushButton("清空") #清空按钮
        btn6.setStyleSheet("font-size:16px;font-weight:550;font-family:Microsoft YaHei;background-color:white;") #按钮字体样式
        btn6.setMinimumHeight(50) #设置按钮最小高度
        lineBoxLayout5.addWidget(btn6,2) #将按钮添加到行布局
        lineBoxLayout5.addStretch(4) #添加空白占位

        rightBoxLayout.addLayout(lineBoxLayout5) #将翻译和清空功能的行布局添加到右布局
        

        self.setGeometry(100, 100, 1700, 850)
        self.setWindowTitle('手势识别系统')
        self.show()


    def selectFile(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,  
                                    "选取文件",  #打开的选择对话框的名称
                                    self.cwd, # 起始路径 
                                    "All Files (*);;Text Files (*.txt)")   # 设置文件扩展名过滤,用双分号间隔
        sender = self.sender()
        if fileName_choose == "":
            sender.clearFocus()
            return
        
        if sender == self.openFileBtn1 :
            self.qle1.setText(fileName_choose)
            self.qle1.clearFocus()
        else :
            self.qle2.setText(fileName_choose)
            self.qle2.clearFocus()
    

    def translate(self):
        global Tree
        global historyResults

        sentence = ""
        ind = 0
        now = 0

        while ind < len(historyResults) and (Tree[now].end==False or (historyResults[ind] not in Tree[0].nextString)):
            sentence += historyResults[ind]
            tmpIndex = find(Tree[now].nextString,historyResults[ind])
            now = int(Tree[now].nextIndex[tmpIndex])
            ind += 1
        
        if ind >= len(historyResults) and Tree[now].end==False:
            sentence = "历史手势序列不足以生成语句！"
        else:
            if ind >= len(historyResults):
                del historyResults[:]
            else:
                del historyResults[:ind]
        print(len(historyResults))
        
        messageBox1 = QMessageBox()
        messageBox1.setStyleSheet("QPushButton {"
                        "background-color:#89AFDE;"
                        " border-style: outset;"
                        " border-width: 2px;"
                        " border-radius: 10px;"
                        " border-color: beige;"
                        " font: bold 24px;"
                        " min-width: 10em;"
                        " min-height: 5em;"
                        "}"
        "QLabel { min-width: 20em;min-height:10em;font:24px;background-color:#f0f0f0;}")
        messageBox1.information(self, '翻译结果', "<div style='font-size:32px;'>"+sentence+"</div>", QMessageBox.Ok)


    

    def myTimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateUI)
        self.timer.start(100)
    

    def updateUI(self):
        global gestureData
        titleColumns = gestureData.columns
        gestureDataTmp = gestureData.values
        self.table1.clear()
        self.table1.setRowCount(math.ceil(gestureDataTmp.shape[0]))

        self.table1.setRowHeight(0, 50)
        for j in range(8):
            newItem = QTableWidgetItem(titleColumns[j])
            newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.table1.setItem(0, j, newItem) # 设置表格内容(行,列,文本)
        for i in range(1,gestureDataTmp.shape[0]):
            self.table1.setRowHeight(i, 50)
            for j in range(gestureDataTmp.shape[1]):
                newItem = QTableWidgetItem(str(gestureDataTmp[i][j]))
                newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.table1.setItem(i, j, newItem) # 设置表格内容(行,列,文本)

        global historyResults
        self.table2.clear()
        self.table2.setRowCount(math.ceil(len(historyResults)/4))
        for i in range(len(historyResults)):
            if (i%4)==0:
                self.table2.setRowHeight(int(i/4), 50)
            newItem = QTableWidgetItem(str(historyResults[i]))
            newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.table2.setItem(int(i/4), i%4, newItem) # 设置表格内容(行,列,文本)
        QApplication.processEvents()
        slider1 = self.table1.verticalScrollBar()
        slider1.setValue(slider1.maximum())
        slider2 = self.table2.verticalScrollBar()
        slider2.setValue(slider2.maximum())


    def start_recognize(self):
        # global Ser
        # global serialPort
        # global baudRate
        # Ser = SerialPort(serialPort, baudRate)
        # global t1
        # t1 = threading.Thread(target=Ser.read_data)
        # t1.setDaemon(True)
        # t1.start()

        self.workThread = WorkThread()
        self.workThread.start()

        self.myTimer()

        global t2
        t2.start()
    

    def end_recognize(self):
        # global serial_is_open
        # serial_is_open = False
        # global Ser
        # Ser.port_close()

        self.workThread.terminate()
        self.workThread.wait()

        self.timer.stop()

        global recognize_is_start
        recognize_is_start = False


class Slice:
    pass


def deal_data():
    #定义一些参数
    FrameLength = 10
    StepLength = 4
    Threshold1 = 0.010
    Threshold2 = 0.003
    global gestureData
    global startIndex
    global recognize_is_start
    global models
    global ex
    global historyResults

    recognize_is_start = True

    while recognize_is_start:
        if (gestureData.shape[0]-startIndex)<=FrameLength:
            continue
        #计算波动值序列
        fluctuation = np.zeros(gestureData.shape[0]-startIndex-FrameLength)
        for i in range(fluctuation.shape[0]):
            fluctuation[i] = np.sum(np.var(gestureData.iloc[startIndex+i:startIndex+i+FrameLength+1,:3]))
        
        # 观察波动值变化情况
        # plt.plot(fluctuation)
        # plt.xticks(np.arange(0,len(fluctuation),40))
        # plt.axhline(y=0.003,c='red',ls='--',lw=1)
        # plt.axhline(y=0.010,c='red',ls='--',lw=1)
        # plt.show()

        findStart = False
        sliceTmp = Slice()
        #遍历波动序列进行分割
        for i in  range(0,fluctuation.shape[0],StepLength):
            if not findStart and fluctuation[i] >= Threshold1:
                sliceTmp = Slice()
                sliceTmp.start = i+startIndex
                findStart = True
            elif findStart and fluctuation[i] < Threshold2:
                sliceTmp.end = i+startIndex
                findStart =  False
                distance = dict() #用于保存当前待识别的手势序列和不同手势模板的距离
                for k,v in models.items(): #与不同的手势模板比较
                    distance[k] = Dtw(gestureData.iloc[sliceTmp.start:sliceTmp.end,:3],v) #用Dtw求手势序列和手势模板的距离
                if distance[min(distance,key=distance.get)] == float('inf'):
                    print("不存在该手势的模板") #所有模板都没匹配上
                else:
                    historyResults.append(min(distance,key=distance.get))
                    pixmap2 = QPixmap("./images/results/"+min(distance,key=distance.get)+".jpg") #读入图片
                    ex.label8.setPixmap(pixmap2)
        
        if hasattr(sliceTmp, "end"):
            startIndex = sliceTmp.end+StepLength
        elif hasattr(sliceTmp, "start"):
            startIndex = sliceTmp.start
        else:
            startIndex += fluctuation.shape[0]-1+StepLength


class Node:
    nextString = []
    nextIndex = []
    end = False


def read_tree():
    with open('regular_tree.txt','r',encoding='utf-8') as fin:
        tree = []
        treeLen = int(fin.readline()) #先读入头部的搜索树长度
        tmpNode = Node()

        for index, line in enumerate(fin.readlines()):
            #数据处理
            line = line.rstrip('\n')
            line = line.split()
            #生成搜索树
            if (index%3)==0:
                tmpNode = Node()
                tmpNode.nextString = line
            elif (index%3)==1:
                tmpNode.nextIndex = line
            else:
                if line[0]=="False":
                    tmpNode.end = False
                else:
                    tmpNode.end = True
                tree.append(tmpNode)
        
        return tree

            

                
def display1():
    global ex
    sequence = ['0','1','2','3','4','5','手掌反转']
    results = ["数字0","数字1","数字2","数字3","数字4","数字5","手掌反转"]

    for i in range(7):
        sleep(3)
        historyResults.append(results[i])
        pixmap2 = QPixmap("./裁剪/"+sequence[i]+".jpg") #读入图片
        ex.label8.setPixmap(pixmap2)


def display2():
    global ex
    sequence = ['我','为','中国','加油']

    for i in range(4):
        sleep(2)
        historyResults.append(sequence[i])
        pixmap2 = QPixmap("./images/results/"+sequence[i]+".jpg") #读入图片
        ex.label8.setPixmap(pixmap2)
        ex.gestureMeans.setText(sequence[i])




gestureData = pd.DataFrame(columns=['大拇指','食指','中指','无名指','小指','ax','ay','az'])
recognize_is_start = False
startIndex = 0

global Ser
serial_is_open = False
serialPort = "COM3" #串口号
baudRate = 115200 #波特率

historyResults = []


        
if __name__ == '__main__':
    global Tree
    Tree = read_tree() #读入翻译匹配规则搜索树

    global models
    models = pd.read_excel(r"./手势分割数据/models.xlsx",sheet_name=None) #读入模板数据

    port_list = list(serial.tools.list_ports.comports())
    print(port_list)
    if len(port_list) == 0:
        print('无可用串口')
    else:
        for i in range(0,len(port_list)):
            print(port_list[i])

    global t2
    t2 = threading.Thread(target=display2)
    t2.setDaemon(True)

    app = QApplication(sys.argv)
    global ex
    ex = Recognizer()
    sys.exit(app.exec_())