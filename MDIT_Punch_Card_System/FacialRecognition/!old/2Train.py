import cv2
import numpy as np
import os
import re

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') # 載入人臉追蹤模型
recog = cv2.face.LBPHFaceRecognizer_create()      # 啟用訓練人臉模型方法
faces = []   # 儲存人臉位置大小的串列
ids = []     # 記錄該人臉 id 的串列

allfile = []

for root, dirs, files in os.walk("."):
    for filename in files:
        path = root +"\\"+ filename
        if re.match('.*TW\d{4}.*png', path):
            allfile.append(path)

for path in allfile:
    num = int(path[5:8])
    print("讀取並辨識"+path+"...")
    img = cv2.imread(path)                        # 依序開啟每一張照片
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 色彩轉換成黑白
    img_np = np.array(gray,'uint8')               # 轉換成指定編碼的 numpy 陣列
    face = face_cascade.detectMultiScale(gray)    # 擷取人臉區域
    for(x,y,w,h) in face:
        faces.append(img_np[y:y+h,x:x+w])         # 記錄人臉的位置和大小內像素的數值
        ids.append(num)                        # 記錄人臉對應的 id，只能是整數，都是 1 表示蔡英文的 id 為 1
print('訓練中...')                                # 提示開始訓練
recog.train(faces, np.array(ids))                 # 開始訓練
recog.save('.\\face.yaml')         # 訓練完成儲存
print('OK!')