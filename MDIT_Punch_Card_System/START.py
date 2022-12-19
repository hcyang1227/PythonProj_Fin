"""
File Name: START.py
Program IDE: Visual Studio Code
Date: 2022/09/28
Create File By Author: Keaton Yang
"""
# 引入相關模組
import sys
from PyQt5 import QtWidgets
from controller import MainWindow_controller

if __name__ == '__main__':
    # 這個蠻複雜的，簡單講建立一個應用程式都需要它
    # 然後將 sys.argv 這個參數引入進去之後
    # 就能執行最後一行的 sys.exit(app.exec_())
    app = QtWidgets.QApplication(sys.argv)
    #建立視窗程式的物件，並顯示視窗
    win = MainWindow_controller()
    win.show()
    # 離開程式
    sys.exit(app.exec_())