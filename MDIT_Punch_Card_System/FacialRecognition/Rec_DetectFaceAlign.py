"""
File Name: Rec_DetectFaceAlign.py
Program IDE: Visual Studio Code
Date: 2022/09/30
Create File By Author: Keaton Yang
"""

from FacialRecognition.Rec_SCRFD import SCRFD
from FacialRecognition.Rec_GetFaceFeature import arcface
import pickle
import cv2
import numpy as np
from scipy import spatial
import os
import time

from PyQt5 import QtCore, QtGui, QtWidgets

class DetectFaceAlign(QtCore.QThread):

    rawdata = QtCore.pyqtSignal(np.ndarray)  # 建立傳遞信號，需設定傳遞型態為 np.ndarray
    rawid = QtCore.pyqtSignal(list)
    rawstr = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
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
        # 當正常連接攝影機才能進入迴圈
        face_embdnet = arcface()
        detect_face = SCRFD()
        emb_path = 'FacialRecognition/MDIT_members_arcface.pkl'
        pkl_exist = True
        if not os.path.exists(emb_path):
            self.rawstr.emit('沒有找到pkl訓練檔，請重新訓練產生檔案！')
            pkl_exist = False
        else:
            with open(emb_path, 'rb') as f:
                dataset = pickle.load(f)
            faces_feature, names_list = dataset

        while self.running and self.connect:
            ret, img = self.cam.read()    # 讀取影像
            if ret:
                imgfinal = img.copy()
                _, faces_img, boxs = detect_face.detect(img)
                threshold = 1.6
                pred_name = 'face_detected'
                pred_score = 9999
                if len(faces_img) > 0:
                    for i, face in enumerate(faces_img):
                        if pkl_exist & (face.shape[0] > 10) & (face.shape[1] > 10):
                            feature_out = face_embdnet.get_feature(face)
                            dist = spatial.distance.cdist(faces_feature, feature_out, metric='euclidean').flatten()
                            min_id = np.argmin(dist)
                            pred_score = dist[min_id]
                            if dist[min_id] <= threshold:
                                pred_name = names_list[min_id]
                                cv2.rectangle(imgfinal, (boxs[i][0], boxs[i][1]), (boxs[i][2], boxs[i][3]), (0, 255, 0), thickness=2)
                                cv2.putText(imgfinal, pred_name+" "+str(round(pred_score,3)), (boxs[i][0], boxs[i][1] - 12), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))
                                self.rawid.emit([pred_name, pred_score])
                            else:
                                pred_name = 'unknown'
                                cv2.rectangle(imgfinal, (boxs[i][0], boxs[i][1]), (boxs[i][2], boxs[i][3]), (0, 0, 255), thickness=2)
                                cv2.putText(imgfinal, pred_name+" "+str(round(pred_score,3)), (boxs[i][0], boxs[i][1] - 12), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
                                self.rawid.emit([pred_name, pred_score])
                self.rawdata.emit(imgfinal)    # 發送影像
            else:    # 例外處理
                self.rawstr.emit('相機開啟錯誤！請重新啟動程序...')
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