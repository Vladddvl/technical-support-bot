# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Admin_panel.ui'
#
# Created by: PyQt5 UI code generator 5.15.5
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5 import QtCore, QtGui, QtWidgets
from DB import workDB
from Table_Admin import Ui_Dialog


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1006, 732)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(20, 100, 951, 501))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(20, 60, 181, 21))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(790, 630, 171, 28))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(600, 630, 171, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(410, 630, 171, 28))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(220, 630, 171, 28))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(30, 630, 171, 28))
        self.pushButton_5.setObjectName("pushButton_5")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(690, 60, 211, 21))
        self.checkBox.setObjectName("checkBox")
        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_6.setGeometry(QtCore.QRect(460, 20, 181, 31))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_7 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_7.setGeometry(QtCore.QRect(460, 60, 181, 28))
        self.pushButton_7.setObjectName("pushButton_7")
        self.comboBox_2 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_2.setGeometry(QtCore.QRect(220, 60, 181, 21))
        self.comboBox_2.setObjectName("comboBox_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(230, 10, 171, 31))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 10, 171, 31))
        self.label_2.setObjectName("label_2")
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2.setGeometry(QtCore.QRect(690, 20, 211, 21))
        self.checkBox_2.setObjectName("checkBox_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1006, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.pushButton_6.clicked.connect(self.open_main_admin_panel)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.comboBox.setItemText(0, _translate("MainWindow", "Настройки"))
        self.comboBox.setItemText(1, _translate("MainWindow", "Установка"))
        self.comboBox.setItemText(2, _translate("MainWindow", "Инструкции"))
        self.comboBox.setItemText(3, _translate("MainWindow", "Операторы"))
        self.comboBox.setItemText(4, _translate("MainWindow", "Пожелание пользователей"))
        self.comboBox.setItemText(5, _translate("MainWindow", "Вопросов и ответов"))
        self.pushButton.setText(_translate("MainWindow", "Отмена"))
        self.pushButton_2.setText(_translate("MainWindow", "Изменить"))
        self.pushButton_3.setText(_translate("MainWindow", "Сохранить"))
        self.pushButton_4.setText(_translate("MainWindow", "Удалить"))
        self.pushButton_5.setText(_translate("MainWindow", "Добавить"))
        self.checkBox.setText(_translate("MainWindow", "не просмотренные инструкции"))
        self.pushButton_6.setText(_translate("MainWindow", "Таблица Суперадмнов"))
        self.pushButton_7.setText(_translate("MainWindow", "История"))
        self.comboBox_2.setItemText(0, _translate("MainWindow", "Все"))
        self.label.setText(_translate("MainWindow", "Программа:"))
        self.label_2.setText(_translate("MainWindow", "Таблица:"))
        self.checkBox_2.setText(_translate("MainWindow", "Свободные операторы"))

        programs = workDB.get_programs()
        for id, program in programs.items():
            self.comboBox_2.addItem(program)



    def open_main_admin_panel(self):
        Dialog = QtWidgets.QDialog()
        ui_cart = Ui_Dialog()
        # Передача номера заказа в следующее окно

        ui_cart.setupUi(Dialog)

        Dialog.show()
        Dialog.exec_()



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())