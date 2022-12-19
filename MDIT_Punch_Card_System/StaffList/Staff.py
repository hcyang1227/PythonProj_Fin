"""
File Name: Staff.py
Program IDE: Visual Studio Code
Date: 2022/09/28
Create File By Author: Keaton Yang
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
import os, shutil, collections

class StaffName(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 StaffName 類別

    def __init__(self, parent=None):
        """ 初始化
            - 執行 QtCore.QThread 的初始化
        """
        # 將父類初始化
        super().__init__(parent)
        initData = {
            # 'ID': ['TW0000', 'TW0008', 'TW0109', 'TW0115'],
            # 'Name': ["Guest1", "S.Y.Chang", "J Huang", "Keaton Yang"],
            # 'SFX': ['預設', '預設', '預設', '預設'],
            # 'Email': ['c5g4f4c4up2k@gmail.com', 'c5g4f4c4up2k@gmail.com', 'c5g4f4c4up2k@gmail.com', 'c5g4f4c4up2k@gmail.com']
        }
        self.Total = pd.DataFrame(initData)
        self.filelocation = r'.\StaffList\staff.txt'
        # self.dataframe_to_csv()
        # self.csv_to_dataframe()

    def dataframe_to_csv(self):
        self.Total.to_csv(self.filelocation, encoding='utf-8', index=False)

    def csv_to_dataframe(self):
        del self.Total
        self.Total = pd.read_csv(self.filelocation, encoding='utf-8')
        self.Total = self.Total.sort_values(by=['ID'])

    def create_folder_name(self, id):
        if not os.path.exists('Images/'+id):
            os.mkdir('Images/'+id)

    def delete_folder_name(self, id):
        if os.path.exists('Images/'+id):
            shutil.rmtree('Images/'+id)

    def change_folder_name(self, id1, id2):
        dplctFlg = False
        for i in self.Total['ID']:
            if i == id2:
                dplctFlg = True
        if id2 == "":
            dplctFlg = True
        if not dplctFlg:
            row = self.Total[(self.Total.ID == id1)].index.tolist()[0]
            self.Total['ID'][row] = id2
            if os.path.exists('Images/'+id1):\
                #Python修改文件夹名称
                #https://blog.csdn.net/Z_Silence/article/details/104559172
                os.rename('Images/'+id1, 'Images/'+id2)
            else:
                os.mkdir('Images/'+id2)
            return True
        else:
            return False

    def insert_new_row(self, istr):
        df = pd.DataFrame({'ID': [istr], 'Name': ['YourName'], 'SFX': ['預設'], 'Email': ['user@mitsuboshi-dia.co.jp']})
        self.Total = pd.concat([df, self.Total], axis=0, ignore_index=True)

    def change_user_name(self, row, name):
        self.Total['ID'][row] = name

    def change_sfx_route(self, row, route):
        self.Total['SFX'][row] = route

    def change_email_address(self, row, email):
        self.Total['Email'][row] = email



# test = StaffName()