# coding=utf-8
import sys

from PyQt5 import Qt
from PyQt5.QtGui import QIcon, QEnterEvent
from PyQt5.QtWidgets import QWidget
from qtpy import QtWidgets

from GUI盘搜.GUI import Ui_window
from UI import StyleSheet, LeftBottom, RightTop, RightBottom, LeftTop, Left, Right, Top, Bottom


class MyPyQT_Form(QtWidgets.QWidget, Ui_window):
    def __init__(self):
        super(MyPyQT_Form, self).__init__()
        self.setupUi(self)
        # self.setToolTip("这是提示!!")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)
    my_pyqt_form = MyPyQT_Form()
    my_pyqt_form.setWindowTitle('Pan嗖嗖')
    my_pyqt_form.setWindowIcon(QIcon(r'搜索.png'))
    my_pyqt_form.setWindowFlags(Qt.Qt.FramelessWindowHint)
    my_pyqt_form.show()
    sys.exit(app.exec_())
