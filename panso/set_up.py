# coding=utf-8
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from qtpy import QtWidgets

from Gui_so import Ui_window


class MyPyQT_Form(QtWidgets.QWidget, Ui_window):
    def __init__(self):
        super(MyPyQT_Form, self).__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    my_pyqt_form = MyPyQT_Form()
    my_pyqt_form.setWindowTitle('Pan嗖嗖')
    my_pyqt_form.setWindowIcon(QIcon(r'./main.ico'))
    my_pyqt_form.setWindowFlags(Qt.WindowStaysOnTopHint)
    my_pyqt_form.show()
    sys.exit(app.exec_())
