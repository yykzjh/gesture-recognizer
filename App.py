import sys
import os
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, QToolTip,
    QMessageBox, QDesktopWidget, QHBoxLayout, QVBoxLayout, QApplication, 
    QGridLayout, QLabel, QLineEdit, QTextEdit, QLCDNumber, QSlider, QInputDialog, 
    QFrame, QColorDialog, QSizePolicy, QAction, QFileDialog, QFontDialog, 
    QCheckBox, QSlider, QProgressBar, QCalendarWidget, QSplitter, QStyleFactory, QComboBox, 
    )
from PyQt5.QtGui import (QFont, QIcon, QPixmap)
from PyQt5.QtCore import (pyqtSignal, QObject, QCoreApplication, Qt, QBasicTimer, QDate)



class Recognizer(QWidget):
    
    def __init__(self):
        super().__init__()
        self.cwd = os.getcwd() # 获取当前程序文件位置
        self.initUI()
        
        
    def initUI(self):
        hbox = QHBoxLayout(self) #定义框布局

        leftFrame = QFrame(self) #定义左框架
        leftFrame.setMaximumWidth(900)
        leftFrame.setFrameShape(QFrame.StyledPanel)

        rightFrame = QFrame(self) #定义右框架
        rightFrame.setMaximumWidth(900)
        rightFrame.setFrameShape(QFrame.StyledPanel)

        splitter = QSplitter(Qt.Horizontal) #定义子控件边界可变
        splitter.addWidget(leftFrame) #将左框架添加到可变边界
        splitter.addWidget(rightFrame) #将右框架添加到可变边界

        hbox.addWidget(splitter) #为主窗口添加可变边界控件
        self.setLayout(hbox) #为主窗口设置布局

        leftBoxLayout = QVBoxLayout() #左边总体垂直框布局
        leftBoxLayout.setContentsMargins(100, 20, 100, 20) #设置左边总体布局的内边界
        
        label1 = QLabel("手势数据") #手势数据的标题
        label1.setAlignment(Qt.AlignCenter) #手势数据标题水平居中
        label1.setStyleSheet("font-size:24px;font-weight:bold;font-family:Microsoft YaHei") #手势数据标题字体样式
        leftBoxLayout.addWidget(label1,2) #手势数据标题添加到布局

        leftFrame.setLayout(leftBoxLayout) #将左边的总体垂直布局添加到左框架

        gestureData = pd.DataFrame([[1,2.2,3.14,4,2.54],[1.1,2.2,3.3,4.4,5.5]],columns=['A','B','C','D','E']) #手势数据的集合形式
        gestureDataString = "" #手势数据的字符串形式
        for index, row in gestureData.iterrows(): #遍历手势数据转换格式
            for i in range(row.shape[0]):
                gestureDataString += str(row[i])+"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" #每列数据用空格分隔
            gestureDataString += "<br>" #每行数据换行
        gestureDataString += "......"
        
        gestureDataBox = QTextEdit() #显示手势数据的文本框
        gestureDataBox.setStyleSheet("font-size:16px;font-family:Arial;padding:20 20 20 20;")
        gestureDataBox.setMaximumHeight(400) #设置手势数据框最大高度
        gestureDataBox.setAlignment(Qt.AlignCenter) #设置手势数据文本框水平居中
        gestureDataBox.setHtml(gestureDataString) #设置手势数据的内容
        gestureDataBox.setReadOnly(True) #设置手势数据文本框不可编辑
        leftBoxLayout.addWidget(gestureDataBox,10) #将手势数据框添加到布局
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
        lineBoxLayout3.addStretch(1) #添加空白占位

        label5 = QLabel("分割数据存储位置") #第四行的功能
        label5.setWordWrap(True)
        label5.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        label5.setStyleSheet("font-size:20px;font-weight:bold;font-family:Microsoft YaHei") #各功能名称字体样式
        lineBoxLayout4.addWidget(label5,2) #第四行添加功能名
        lineBoxLayout4.addStretch(1) #添加空白占位

        #第一行的功能控件
        combo1 = QComboBox()
        combo1.setMinimumHeight(50)
        combo1.setStyleSheet("font-size:16px;font-family:Microsoft YaHei") #下拉列表字体样式
        qleTmp = QLineEdit() #下面都是设置字体居中
        qleTmp.setAlignment(Qt.AlignCenter)
        qleTmp.setReadOnly(True)
        combo1.setLineEdit(qleTmp)

        comboLists = [8080,22,21,8888,7079] #下拉列表的项
        for item in comboLists:
            combo1.addItem(str(item)) #将各项添加到下拉列表中

        lineBoxLayout1.addWidget(combo1,3)
        lineBoxLayout1.addStretch(1) #添加空白占位

        btn1 = QPushButton("打开端口")
        btn1.setStyleSheet("font-size:16px;font-weight:550;font-family:Microsoft YaHei") #按钮字体样式
        btn1.setMinimumHeight(50)
        lineBoxLayout1.addWidget(btn1,3)
        lineBoxLayout1.addStretch(1) #添加空白占位

        btn2 = QPushButton("关闭端口")
        btn2.setStyleSheet("font-size:16px;font-weight:550;font-family:Microsoft YaHei") #按钮字体样式
        btn2.setMinimumHeight(50)
        lineBoxLayout1.addWidget(btn2,3)

        #第二行的功能控件
        self.qle1 = QLineEdit()
        self.qle1.setMinimumHeight(30)
        self.qle1.setPlaceholderText("可在本地电脑保存的地址(D:\\...)")
        self.qle1.setReadOnly(True)
        lineBoxLayout2.addWidget(self.qle1,11)

        self.openFileBtn1 = QPushButton()
        self.openFileBtn1.setStyleSheet("background-image:url(shengluehao.ico);\
            background-repeat:no-repeat;\
            background-position:center;\
            border: 1px solid grey")
        self.openFileBtn1.setMinimumHeight(30)
        self.openFileBtn1.clicked.connect(self.selectFile) #给打开文件按钮绑定点击事件
        lineBoxLayout2.addWidget(self.openFileBtn1)

        #第三行的功能控件
        btn3 = QPushButton("开始识别")
        btn3.setStyleSheet("font-size:16px;font-weight:550;font-family:Microsoft YaHei") #按钮字体样式
        btn3.setMinimumHeight(50)
        lineBoxLayout3.addWidget(btn3,3)
        lineBoxLayout3.addStretch(2) #添加空白占位

        btn4 = QPushButton("结束识别")
        btn4.setStyleSheet("font-size:16px;font-weight:550;font-family:Microsoft YaHei") #按钮字体样式
        btn4.setMinimumHeight(50)
        lineBoxLayout3.addWidget(btn4,3)
        lineBoxLayout3.addStretch(2) #添加空白占位

        #第四行的功能控件
        self.qle2 = QLineEdit()
        self.qle2.setMinimumHeight(30)
        self.qle2.setPlaceholderText("可在本地电脑保存的地址(D:\\...)")
        self.qle2.setReadOnly(True)
        lineBoxLayout4.addWidget(self.qle2,11)
        
        self.openFileBtn2 = QPushButton()
        self.openFileBtn2.setStyleSheet("background-image:url(shengluehao.ico);\
            background-repeat:no-repeat;\
            background-position:center;\
            border: 1px solid grey")
        self.openFileBtn2.setMinimumHeight(30)
        self.openFileBtn2.clicked.connect(self.selectFile) #给打开文件按钮绑定点击事件
        lineBoxLayout4.addWidget(self.openFileBtn2)

        #将各行功能添加到左边总布局中
        leftBoxLayout.addLayout(lineBoxLayout1,2)
        leftBoxLayout.addStretch(1) #添加一段占位空白
        leftBoxLayout.addLayout(lineBoxLayout2,2)
        leftBoxLayout.addStretch(1) #添加一段占位空白
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

        pixmap1 = QPixmap("界面.png") #读入图片
        label8 = QLabel() #定义用于存放图片的标签
        label8.setPixmap(pixmap1) #将图片放入标签中
        label8.setMaximumHeight(300) #设置图片最大显示高度
        label8.setAlignment(Qt.AlignHCenter) #设置显示图片的标签水平居中
        label8.setScaledContents (True) #设置图片自适应标签大小
        label8.setStyleSheet("border:1px solid black;margin:0 250;"); #设置显示手势图片标签的样式
        rightBoxLayout.addWidget(label8) #将显示图片的标签添加到右布局


        label9 = QLabel("手势含义") #手势含义的标题
        label9.setAlignment(Qt.AlignHCenter) #手势含义标题水平居中
        label9.setStyleSheet("font-size:24px;font-weight:bold;font-family:Microsoft YaHei;margin-top:30px") #手势含义标题字体样式
        rightBoxLayout.addWidget(label9) #手势含义标题添加到布局

        label10 = QLabel("历史记录：") #显示历史记录的标题
        label10.setAlignment(Qt.AlignLeft) #历史记录标题左对齐
        label10.setStyleSheet("font-size:16px;font-weight:bold;font-family:Microsoft YaHei;")
        rightBoxLayout.addWidget(label10) #历史记录标题添加到右布局

        historyData = [5,4,3,2,1,7,8,9,4,5,6,3,2,1,4,8,4,5,6,3,2,1,1,7,8,9,5,5,
                        3,6,4,8,9,5,1,2,3,7,8,9,4,5,6,3] #历史记录数组
        historyDataString = "&nbsp;&nbsp;&nbsp;" #历史记录字符串
        rowNum = 6 #每行显示记录个数
        for index,item in enumerate(historyData):
            historyDataString += str(item)
            if (index+1)%rowNum==0 :
                historyDataString += "<br></br><br></br>&nbsp;&nbsp;&nbsp;" #显示一定量记录后换行
            else: #一行中的每个记录有间隔
                historyDataString += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"

        historyDataBox = QTextEdit() #显示历史记录的文本框
        historyDataBox.setMaximumHeight(200) #设置历史记录框最大高度
        historyDataBox.setStyleSheet("font-size:20px;font-weight:500;font-family:Arial;margin:0 100 10 100;padding:20 0 20 20;")
        historyDataBox.setAlignment(Qt.AlignCenter) #设置历史记录文本框水平居中
        historyDataBox.setHtml(historyDataString) #设置历史记录的内容
        historyDataBox.setReadOnly(True) #设置历史记录文本框不可编辑
        rightBoxLayout.addWidget(historyDataBox) #将历史记录框添加到布局
        
        lineBoxLayout5 = QHBoxLayout() #翻译和清空功能的框布局
        lineBoxLayout5.addStretch(4) #添加空白占位

        btn5 = QPushButton("翻译") #翻译按钮
        btn5.setStyleSheet("font-size:16px;font-weight:550;font-family:Microsoft YaHei") #按钮字体样式
        btn5.setMinimumHeight(50) #设置按钮最小高度
        lineBoxLayout5.addWidget(btn5,2) #将按钮添加到行布局
        lineBoxLayout5.addStretch(2) #添加空白占位

        btn6 = QPushButton("清空") #清空按钮
        btn6.setStyleSheet("font-size:16px;font-weight:550;font-family:Microsoft YaHei") #按钮字体样式
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

        if fileName_choose == "":
            sender.clearFocus()
            return
        
        sender = self.sender()
        if sender == self.openFileBtn1 :
            self.qle1.setText(fileName_choose)
            self.qle1.clearFocus()
        else :
            self.qle2.setText(fileName_choose)
            self.qle2.clearFocus()
        
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Recognizer()
    sys.exit(app.exec_())