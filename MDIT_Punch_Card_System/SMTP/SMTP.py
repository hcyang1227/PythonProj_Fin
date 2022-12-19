"""
File Name: SMTP.py
Program IDE: Visual Studio Code
Date: 2022/10/12
Create File By Author: Keaton Yang
"""

# 利用Python自動寄送Gmail電子郵件Email
# https://badgameshow.com/fly/python-%E5%88%A9%E7%94%A8python%E8%87%AA%E5%8B%95%E5%AF%84%E9%80%81gmail%E9%9B%BB%E5%AD%90%E9%83%B5%E4%BB%B6email/fly/python/

from PyQt5 import QtCore, QtGui, QtWidgets
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header



# 第三方 SMTP 服務
mail_host="smtp.gmail.com"  #設置伺服器
mail_user="hcyang1227@gmail.com"    #用戶名
mail_pass="zjngbngtzaharcvl"   #密碼

sender = 'hcyang1227@gmail.com'

class SendEmail(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 StaffName 類別

    rawstr = QtCore.pyqtSignal(str)
    punch = 1
    temp = 36.0
    receivers = ['c5g4f4c4up2k@gmail.com']

    def __init__(self, parent=None):
        """ 初始化
            - 執行 QtCore.QThread 的初始化
        """
        # 將父類初始化
        super().__init__(parent)


    def send(self, punch = 1, temp = 36.0, receivers = ['c5g4f4c4up2k@gmail.com']):
        self.punch = punch
        self.temp = temp
        self.receivers = receivers
        self.start()

    def run(self):
        if self.temp <= 38.0:
            tempstr = "打卡當下體溫為"+str(self.temp)+"°C，體溫正常。"
        else:
            tempstr = "打卡當下體溫為"+str(self.temp)+"°C，已有發燒情況！"
            self.receivers.append('hcyang1227@gmail.com')

        if self.punch == 1:
            message = MIMEText('上班打卡成功。\n'+tempstr+'\n打卡時間戳記'+datetime.now().strftime("%Y-%m-%d %H:%M")+'\n上班加油！', 'plain', 'utf-8')
            subject = '【MDIT打卡系統通知】上班打卡成功'
        elif self.punch == 2:
            message = MIMEText('下班打卡成功。\n'+tempstr+'\n打卡時間戳記'+datetime.now().strftime("%Y-%m-%d %H:%M")+'\n今天辛苦了！', 'plain', 'utf-8')
            subject = '【MDIT打卡系統通知】下班打卡成功'
        elif self.punch == 3:
            message = MIMEText('外出打卡成功。\n'+tempstr+'\n打卡時間戳記'+datetime.now().strftime("%Y-%m-%d %H:%M")+'\n出差加油！', 'plain', 'utf-8')
            subject = '【MDIT打卡系統通知】外出打卡成功'
        elif self.punch == 4:
            message = MIMEText('返回打卡成功。\n'+tempstr+'\n打卡時間戳記'+datetime.now().strftime("%Y-%m-%d %H:%M")+'\n出差辛苦了！', 'plain', 'utf-8')
            subject = '【MDIT打卡系統通知】返回打卡成功'
        else:
            message = MIMEText('打卡出現例外狀況....\n'+tempstr+'\n打卡時間戳記'+datetime.now().strftime("%Y-%m-%d %H:%M")+'\n不管如何，總之加油吧！', 'plain', 'utf-8')
            subject = '【MDIT打卡系統通知】打卡例外狀況！？請聯絡制御設計人員'

        message['From'] = Header("MDIT-Server", 'utf-8')
        message['To'] =  Header("End Users", 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')

        try:
            smtpObj = smtplib.SMTP(mail_host, "587")
            smtpObj.ehlo()  #驗證SMTP伺服器
            smtpObj.starttls()  #建立加密傳輸
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, self.receivers, message.as_string())
        except smtplib.SMTPException as exception:
            self.rawstr.emit("信件發送有誤，錯誤內容："+str(exception))