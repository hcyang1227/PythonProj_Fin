"""
File Name: Recognition.py
Program IDE: Visual Studio Code
Date: 2022/09/28
Create File By Author: Keaton Yang
"""
# 使用OpenCV & Dlib來做人臉偵測，大概可以分為四種方式：
# OpenCV Haar cascades
# OpenCV deep neural networks(DNNs)
# Dlib HOG + Linear SVM
# Dlib max-margin object detector(MMOD)

import cv2            # 引入 OpenCV 的模組，製作擷取攝影機影像之功能
import sys, time      # 引入 sys 跟 time 模組
import numpy as np    # 引入 numpy 來處理讀取到得影像矩陣
import os

from PyQt5 import QtCore, QtGui, QtWidgets

recognizer = cv2.face.LBPHFaceRecognizer_create()         # 啟用訓練人臉模型方法
cascade_path = "haarcascade_frontalface_default.xml"      # 載入人臉追蹤模型
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_path)        # 啟用人臉追蹤

class CameraA(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 Camera 類別
    rawdata = QtCore.pyqtSignal(np.ndarray)  # 建立傳遞信號，需設定傳遞型態為 np.ndarray
    rawid = QtCore.pyqtSignal(list)

    recogFlg = False

    def __init__(self, parent=None):
        """ 初始化
            - 執行 QtCore.QThread 的初始化
            - 建立 cv2 的 VideoCapture 物件
            - 設定屬性來確認狀態
              - self.connect：連接狀態
              - self.running：讀取狀態
        """
        # 將父類初始化
        super().__init__(parent)
        # 建立 cv2 的攝影機物件
        self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # 判斷攝影機是否正常連接
        if self.cam is None or not self.cam.isOpened():
            self.connect = False
            self.running = False
        else:
            self.connect = True
            self.running = False

    def read_yaml(self):
        if os.path.exists('.\\FacialRecognition\\face.yaml'):
            recognizer.read('.\\FacialRecognition\\face.yaml')
            self.recogFlg = True

    def run(self):
        """ 執行多執行緒
            - 讀取影像
            - 發送影像
            - 簡易異常處理
        """
        # 當正常連接攝影機才能進入迴圈
        while self.running and self.connect:
            ret, img = self.cam.read()    # 讀取影像
            if ret:
                img = cv2.resize(img, (640, 480))              # 縮小尺寸，加快辨識效率
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 轉換成黑白
                faces = face_cascade.detectMultiScale(gray)  # 追蹤人臉 ( 目的在於標記出外框 )
                # 依序判斷每張臉屬於哪個 id
                for(x,y,w,h) in faces:
                    idnum = 0
                    confidence = 9999
                    if self.recogFlg:
                        idnum, confidence = recognizer.predict(gray[y:y+h, x:x+w])
                    if confidence < 70:
                        # text = name[str(idnum)]                               # 如果信心指數小於 60，取得對應的名字
                        text = "id="+str(idnum)+" conf="+str(round(confidence,1))
                        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)        # 標記人臉外框
                        cv2.putText(img, text, (x,y-5),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA) # 在人臉外框旁加上名字
                        self.rawid.emit([idnum, confidence])
                    else:
                        text = "??? conf="+str(round(confidence,1))                                   # 不然名字就是 ???
                        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)        # 標記人臉外框
                        cv2.putText(img, text, (x,y-5),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA) # 在人臉外框旁加上名字
                self.rawdata.emit(img)    # 發送影像
            else:    # 例外處理
                print("Warning!!!")
                self.connect = False

    def open(self):
        """ 開啟攝影機影像讀取功能 """
        if self.connect:
            self.running = True    # 啟動讀取狀態

    # def stop(self):
    #     """ 暫停攝影機影像讀取功能 """
    #     if self.connect:
    #         self.running = False    # 關閉讀取狀態

    def close(self):
        """ 關閉攝影機功能 """
        if self.connect:
            self.running = False    # 關閉讀取狀態
            time.sleep(1)
            self.cam.release()      # 釋放攝影機
