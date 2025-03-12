# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!
import requests
from configparser import ConfigParser
from datetime import datetime
from PyQt5 import QtCore, QtWidgets, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QHeaderView, QTableView, QAbstractItemView, QPushButton, QHBoxLayout


class Ui_window(object):
    def __init__(self):
        super(Ui_window, self).__init__()
        # ====================加载配置文件================开始
        self.cont = 1
        self.flag2 = False
        self.flag1 = False
        self.max_n = 1
        self.saved = None
        cf = ConfigParser()
        try:
            cf.read("./config.ini", encoding='utf-8')
            self.appKey = cf.get("pan_api1", "appKey")
            self.openId = cf.get("pan_api1", "openId")
        except:
            self.appKey = "8gAVslllRt5N"
            self.openId = "90gApkBpk5NYJ900"
            cf.add_section("pan_api1")
            cf.set("pan_api1", "appKey", self.appKey)
            cf.set("pan_api1", "openId", self.openId)
            cf.write(open('./config.ini', "w"))
        # ====================加载配置文件================结束

    def check(self, flag):
        # ====================获取编辑内容================开始
        content = self.seabar.text()  # 获取文本框内容   self.seabar.displayText()
        self.seabar.setFocus()  # 设置焦点
        if self.seabar.text().isspace() or content == '':
            self.seabar.setPlaceholderText('输入内容不能为空')
            return
        # ====================获取编辑内容================结束

        # ====================选择状态判断================开始
        if self.CoboBox == self.cmbox.currentIndex():
            self.flag1 = True
        else:
            self.CoboBox = self.cmbox.currentIndex()
            self.cont = 1
            self.flag1 = False

        if self.rbtn == self.rdbtn1.isChecked():
            self.flag2 = True
        else:
            self.rbtn = self.rdbtn1.isChecked()
            self.cont = 1
            self.flag1 = False
        # ====================选择状态判断================结束

        # ====================按钮按下状态================开始
        fg = True
        if flag == 0:
            if content == self.txt and self.flag1 is True and self.flag2 is True:
                self.flag1 = False
                self.flag2 = False
                self.cont = 1
                self.page.setText('第%s页' % ' ')
                self.datasum.setText("共%s条数据" % ' ')
                self.current.setText("共%s页数" % ' ')
                self.seabar.clear()  # 清空文本内容
                self.seabar.setPlaceholderText('搜索重复，换个关键字搜索吧')
                self.previs.setEnabled(False)
                self.next.setEnabled(False)
                return
            else:
                self.cont = 1
                self.previs.setEnabled(False)
                self.next.setEnabled(False)
            self.txt = content

        elif flag == 1:
            self.cont += 1
            if self.cont <= self.max_n:
                if self.cont == self.max_n:
                    self.next.setEnabled(False)
                    fg = False
                if not self.previs.isEnabled():
                    self.previs.setEnabled(True)
            if self.cont > 0 and self.flag1 is False or self.flag2 is False:
                self.previs.setEnabled(False)
                self.next.setEnabled(False)
                self.cont = 1
                self.seabar.clear()  # 清空文本内容
                self.page.setText('第%s页' % ' ')
                self.datasum.setText("共%s条数据" % ' ')
                self.current.setText("共%s页数" % ' ')
                self.seabar.setPlaceholderText('请使用回车或点击搜索，而不是下一页')
                return

        elif flag == 2:
            if not self.cont > 1:
                self.previs.setEnabled(False)
                self.next.setEnabled(False)
                self.cont = 1
                self.seabar.clear()  # 清空文本内容
                self.page.setText('第%s页' % ' ')
                self.datasum.setText("共%s条数据" % ' ')
                self.current.setText("共%s页数" % ' ')
                self.seabar.setPlaceholderText('请使用回车或点击搜索，而不是上一页')
                return

            self.cont -= 1
            if self.cont < 2:
                self.previs.setEnabled(False)
            if not self.next.isEnabled():
                self.next.setEnabled(True)

        # ====================按钮按下状态================结束
        self.page.setText('第%s页'%self.cont)

        # ====================组合按钮================开始
        combox = self.cmbox.currentIndex()
        # self.cmbox.clear()    # 清空内容
        if combox == 0:
            combox = ""
        elif combox == 8:
            combox = 0
        # ====================组合按钮================结束
        url = "http://api.xiaocongjisuan.com/data/skydriverdata/get"
        # self.next.setEnabled(False)
        # self.previs.setEnabled(False)
        header = {}
        data = {
            "appKey": self.appKey,  # 接口唯一标识，在用户后台->应用中心->我的接口查看
            "openId": self.openId,  # 平台id，注册后系统自动生成，在用户后台->用户中心->账户信息查看
            "dType": "json",
            "q": self.seabar.text(),  # 搜索关键词
            "currentPage": self.cont,  # 当前请求页数
            "pageSize": "25",  # 请求页大小，最大值为25
            "o": "1" if self.rdbtn1.isChecked() else "2",  # 1	百度网盘    2	新浪微盘
            "highlight": "0",  # 不高亮
            "t": "down",  # 按时间排序，取两个值：up和down，代表顺序和倒序
            "tPage": "1",  # 距离现在多少天的数据
            "c": combox,  # 文件分类，请参考分类列表
        }
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动拉伸，充满界面
        self.tableView.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # 所有行自动拉伸，充满界面
        try:
            with requests.post(url=url, data=data, timeout=5) as res:
                if res.status_code == 200:
                    a = res.json()
                    self.lgtime.setText("搜索花费%s秒" % a['data']['time'])
                    self.datasum.setText("共%s条数据" % a['data']['amount'])
                    self.current.setText("共%s页数" % a['data']['totalPage'])
                    self.remind.setText('状态:%s' % a['errorMessage'])
                    self.max_n = a['data']['totalPage']
                    if self.max_n > 1:
                        if fg:
                            self.next.setEnabled(True)
                    else:
                        self.next.setEnabled(False)
                        self.previs.setEnabled(False)
                        for index in reversed(range(self.max_n, 25)):
                            self.model.removeRow(index)

                    if a['data']['amount'] == 0:
                        self.model.removeRow(0)
                        self.remind.setText('状态:%s' % '未找到数据')
                        return
                    else:
                        self.tableView.setModel(self.model)

                    stat = a['data']['result']
                    x = []
                    q = 0
                    for i in stat:
                        x.append(i['title'])
                        x.append(i['shareUser'])
                        x.append(i['url'])
                        x.append(i['password'])
                        local_dt_time = datetime.fromtimestamp(i['shareTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
                        x.append(local_dt_time)
                        w = 0
                        for na in x:
                            ta = QStandardItem("%s" % na)
                            self.model.setItem(q, w, ta)
                            w += 1
                        x.clear()
                        q += 1
                else:
                    self.remind.setText('网络状态:%s,请重试' % res.status_code)

        except BaseException as e:
            try:
                self.remind.setText('状态:%s' % a['errorMessage'])
                self.lgtime.setText("搜索花费%s秒" % " ")
                self.datasum.setText("共%s条数据" % " ")
                self.current.setText("共%s页数" % " ")
            except:
                self.remind.setText('状态:%s' % '网络状况不好')

    def sendData(self):
        self.check(0)

    def setupUi(self, window):
        window.setObjectName("window")
        window.setMinimumSize(QtCore.QSize(1024, 850))
        self.gridLayout = QtWidgets.QGridLayout(window)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(120, 80, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout.addItem(spacerItem, 8, 1, 1, 6)  # 布局弹簧
        spacerItem1 = QtWidgets.QSpacerItem(60, 20, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 6, 0, 1, 1)  # 布局弹簧
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 4, 1, 1)
        # ====================搜索文本框================开始
        self.seabar = QtWidgets.QLineEdit(window)
        self.seabar.setFocus()  # 设置焦点
        self.seabar.setMaxLength(33)
        self.seabar.setMaximumSize(QtCore.QSize(480, 25))
        self.seabar.returnPressed.connect(self.sendData)
        self.horizontalLayout_2.addWidget(self.seabar)
        # ====================搜索文本框================结束

        self.txt = self.seabar.text()
        # ====================搜索按钮================开始
        self.search = QtWidgets.QPushButton(window)
        self.search.setMaximumSize(QtCore.QSize(75, 25))
        self.search.setObjectName("search")
        self.gridLayout.addWidget(self.search, 2, 5, 1, 1)
        self.search.clicked.connect(lambda: self.check(0))  # 按下按钮获取文本内容函数
        # ====================搜索按钮================结束

        # ====================多选一按钮================开始
        self.cmbox = QtWidgets.QComboBox(window)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHeightForWidth(self.cmbox.sizePolicy().hasHeightForWidth())
        self.cmbox.setMaximumSize(QtCore.QSize(75, 25))
        self.cmbox.setObjectName("cmbox")
        self.cmbox.addItem("")
        self.cmbox.addItem("")
        self.cmbox.addItem("")
        self.cmbox.addItem("")
        self.cmbox.addItem("")
        self.cmbox.addItem("")
        self.cmbox.addItem("")
        self.cmbox.addItem("")
        self.cmbox.addItem("")
        self.gridLayout.addWidget(self.cmbox, 2, 3, 1, 1)
        # ====================多选一按钮================结束

        spacerItem2 = QtWidgets.QSpacerItem(60, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem2, 0, 1, 1, 6)  # 布局弹簧
        spacerItem3 = QtWidgets.QSpacerItem(60, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 2, 6, 1, 1)  # 布局弹簧

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # ====================单选按钮================开始
        self.rdbtn1 = QtWidgets.QRadioButton(window)
        self.rdbtn1.setChecked(True)  # 默认单选被选中
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.rdbtn1.sizePolicy().hasHeightForWidth())
        self.rdbtn1.setSizePolicy(sizePolicy)
        self.rdbtn1.setObjectName("rdbtn1")
        self.horizontalLayout.addWidget(self.rdbtn1)
        self.rdbtn2 = QtWidgets.QRadioButton(window)
        self.rdbtn2.setObjectName("rdbtn2")
        self.horizontalLayout.addWidget(self.rdbtn2)
        self.rdbtn3 = QtWidgets.QRadioButton(window)
        self.rdbtn3.setEnabled(False)
        self.rdbtn3.setObjectName("rdbtn3")
        self.horizontalLayout.addWidget(self.rdbtn3)
        self.rdbtn4 = QtWidgets.QRadioButton(window)
        self.rdbtn4.setEnabled(False)
        self.rdbtn4.setObjectName("rdbtn4")
        self.horizontalLayout.addWidget(self.rdbtn4)
        self.rdbtn5 = QtWidgets.QRadioButton(window)
        self.rdbtn5.setEnabled(False)
        self.rdbtn5.setObjectName("rdbtn5")
        self.horizontalLayout.addWidget(self.rdbtn5)
        self.rdbtn6 = QtWidgets.QRadioButton(window)
        self.rdbtn6.setEnabled(False)
        self.rdbtn6.setObjectName("rdbtn6")
        self.horizontalLayout.addWidget(self.rdbtn6)
        self.rdbtn7 = QtWidgets.QRadioButton(window)
        self.rdbtn7.setEnabled(False)
        self.rdbtn7.setObjectName("rdbtn7")
        self.horizontalLayout.addWidget(self.rdbtn7)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 4, 1, 1)  # 单选按钮布局
        # ====================单选按钮================结束

        spacerItem4 = QtWidgets.QSpacerItem(60, 20, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 6, 8, 1, 1)  # 布局弹簧
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem5, 3, 5, 1, 1)  # 布局弹簧

        # ====================提示文本================开始
        self.remind = QtWidgets.QLabel(window)
        self.remind.setObjectName("remind")
        self.gridLayout.addWidget(self.remind, 5, 2, 1, 1)
        # ====================提示文本================结束

        # ====================表单数据================开始
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.model = QStandardItemModel(25, 5)  # 存储任意结构数据
        self.model.setHorizontalHeaderLabels(['文件名', '用户名', '链接', '提取码', '时间'])
        self.tableView = QtWidgets.QTableView()
        self.tableView.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.tableView.setToolTip('点击链接ctrl+c复制')
        self.tableView.setSortingEnabled(True)  # 启用排序
        self.verticalLayout.addWidget(self.tableView)

        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置只能选中一行
        self.tableView.setEditTriggers(QTableView.NoEditTriggers)  # 不可编辑
        # ====================表单数据================结束

        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.lgtime = QtWidgets.QLabel(window)
        self.lgtime.setMaximumSize(QtCore.QSize(180, 16777215))
        self.lgtime.setObjectName("lgtime")
        self.horizontalLayout_8.addWidget(self.lgtime)
        spacerItem6 = QtWidgets.QSpacerItem(60, 20, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem6)

        # ====================上下页按钮================开始
        self.next = QtWidgets.QPushButton(window)
        self.next.setMaximumSize(QtCore.QSize(60, 16777215))
        self.next.setObjectName("next")
        self.next.clicked.connect(lambda: self.check(1))  # 按下按钮获取文本内容函数
        self.horizontalLayout_8.addWidget(self.next)  # 按钮布局
        self.next.setEnabled(False)

        self.page = QtWidgets.QLabel(window)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.page.sizePolicy().hasHeightForWidth())
        self.page.setSizePolicy(sizePolicy)
        self.page.setMaximumSize(QtCore.QSize(50, 16777215))
        self.page.setAlignment(QtCore.Qt.AlignCenter)
        self.page.setObjectName("page")
        self.horizontalLayout_8.addWidget(self.page)

        self.previs = QtWidgets.QPushButton(window)
        self.previs.setMaximumSize(QtCore.QSize(60, 16777215))
        self.previs.setObjectName("previs")
        self.previs.clicked.connect(lambda: self.check(2))  # 按下按钮获取文本内容函数
        self.previs.setEnabled(False)
        # ====================上下页按钮================结束

        self.horizontalLayout_8.addWidget(self.previs)
        self.datasum = QtWidgets.QLabel(window)
        self.datasum.setMaximumSize(QtCore.QSize(120, 16777215))
        self.datasum.setObjectName("datasum")
        self.horizontalLayout_8.addWidget(self.datasum)
        self.current = QtWidgets.QLabel(window)
        self.current.setMaximumSize(QtCore.QSize(120, 16777215))
        self.current.setObjectName("current")
        self.horizontalLayout_8.addWidget(self.current)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.gridLayout.addLayout(self.verticalLayout, 6, 1, 1, 6)

        spacerItem7 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem7, 5, 3, 1, 4)  # 布局弹簧
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem8, 2, 2, 1, 1)  # 布局弹簧
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.gridLayout.addLayout(self.horizontalLayout_5, 7, 1, 1, 1)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem9, 3, 2, 1, 1)  # 布局弹簧
        self.CoboBox = self.cmbox.currentIndex()
        self.rbtn = self.rdbtn1.isChecked()
        self.retranslateUi(window)
        QtCore.QMetaObject.connectSlotsByName(window)

    def retranslateUi(self, window):
        _translate = QtCore.QCoreApplication.translate
        window.setWindowTitle(_translate("window", "Form"))
        self.cmbox.setItemText(5, _translate("window", "  压缩"))
        self.cmbox.setItemText(8, _translate("window", "  影视"))
        self.cmbox.setItemText(1, _translate("window", "  音乐"))
        self.cmbox.setItemText(2, _translate("window", "  图片"))
        self.cmbox.setItemText(3, _translate("window", "  文档"))
        self.cmbox.setItemText(4, _translate("window", "  软件"))
        self.cmbox.setItemText(6, _translate("window", "  种子"))
        self.cmbox.setItemText(7, _translate("window", "  文件"))
        self.cmbox.setItemText(0, _translate("window", "  默认"))
        self.rdbtn1.setText(_translate("window", "百度网盘"))
        self.rdbtn2.setText(_translate("window", "新浪网盘"))
        self.rdbtn3.setText(_translate("window", "待定"))
        self.rdbtn4.setText(_translate("window", "待定"))
        self.rdbtn5.setText(_translate("window", "待定"))
        self.rdbtn6.setText(_translate("window", "待定"))
        self.rdbtn7.setText(_translate("window", "待定"))
        self.search.setText(_translate("window", "搜索"))
        self.remind.setText(_translate("window", "温馨提示"))
        self.lgtime.setText(_translate("window", "搜索时长："))
        self.next.setText(_translate("window", "下一页"))
        self.page.setText(_translate("window", " 页"))
        self.previs.setText(_translate("window", "上一页"))
        self.datasum.setText(_translate("window", "共 条数据"))
        self.current.setText(_translate("window", "当前第 页"))

    # def closeEvent(self, QCloseEvent):  # 关闭事件函数
    #     self.saved_func()  # 调用函数进行保存
    #
    # def saved_func(self):
    #     print('结果')