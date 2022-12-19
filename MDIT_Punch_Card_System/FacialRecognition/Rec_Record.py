"""
File Name: Rec_Record.py
Program IDE: Visual Studio Code
Date: 2022/09/30
Create File By Author: Keaton Yang
"""

import cv2            # 引入 OpenCV 的模組，製作擷取攝影機影像之功能
import sys, time      # 引入 sys 跟 time 模組
import numpy as np    # 引入 numpy 來處理讀取到得影像矩陣
import os, shutil
from datetime import datetime as dt

from PyQt5 import QtCore, QtGui, QtWidgets

from FacialRecognition.Rec_SCRFD import SCRFD

class ImageRecorder(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 Camera 類別
    rawdata = QtCore.pyqtSignal(np.ndarray)  # 建立傳遞信號，需設定傳遞型態為 np.ndarray
    rawnum = QtCore.pyqtSignal(int)
    rawstr = QtCore.pyqtSignal(str)
    recordFlg = False
    recordNum = 0
    recordID = ""
    recordCode = "TW"

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

    def run(self):
        """ 執行多執行緒
            - 讀取影像
            - 發送影像
            - 簡易異常處理
        """
        detect_face = SCRFD()
        # 當正常連接攝影機才能進入迴圈
        while self.running and self.connect:
            ret, img = self.cam.read()    # 讀取影像
            if ret:
                srcimg, face_rois, _ = detect_face.detect(img)    # 擷取人臉區域
                for face in face_rois:
                    if (face.shape[0] > 100) & (face.shape[1] > 100):
                        if self.recordFlg & (self.recordNum < 100) & (self.recordID != ""):
                            w, h, d = face.shape
                            facekey = np.random.randint(0, 256, size=[w, h, d], dtype=np.uint8)
                            faceencrypt = cv2.bitwise_xor(face, facekey)
                            tmstmp = dt.now().strftime("%Y%m%d%H%M%S%f")
                            cv2.imwrite('.\\Images\\'+self.recordCode+self.recordID+"\\" + tmstmp +".png", faceencrypt)
                            cv2.imwrite('.\\Images\\'+self.recordCode+self.recordID+"\\" + tmstmp +".tif", facekey)
                            self.rawnum.emit(self.recordNum)
                            self.recordNum += 1
                        elif self.recordFlg & (self.recordNum >= 100) & (self.recordID != ""):
                            self.recordFlg = False
                            self.recordNum = 0
                            self.rawnum.emit(100)
                            self.rawstr.emit("完成擷取！")
                            self.recordID = ""
                self.rawdata.emit(srcimg)    # 發送影像
            else:    # 例外處理
                self.rawstr.emit("攝影機\相機發生問題！請重啟程序...")
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
            time.sleep(0.1)
            self.cam.release()      # 釋放攝影機

    #創造該員工ID的資料夾
    def create_folder(self, num):
        fullnum = str(num).zfill(4)
        self.recordID = fullnum
        if os.path.exists('.\\Images\\'+self.recordCode+fullnum) == False:
            os.makedirs('.\\Images\\'+self.recordCode+fullnum)

    #刪除該員工ID的資料夾
    def delete_folder(self, num):
        fullnum = str(num).zfill(4)
        self.recordID = fullnum
        try:
            shutil.rmtree('.\\Images\\'+self.recordCode+fullnum)
        except OSError as e:
            self.rawstr.emit(str(e))
        else:
            self.rawstr.emit(self.recordCode+ fullnum + "的訓練用照片已被完整清除！")
