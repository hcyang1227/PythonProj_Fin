import cv2
import numpy as np
import os
from datetime import datetime as dt


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') # 載入人臉追蹤模型

faces = []   # 儲存人臉位置大小的串列

while True:
    print('請輸入要進行人臉辨識訓練的工號後面4位數字(ex:0115)，或按(q)離開...')
    ipt = input()
    if (ipt[0] == "Q") or (ipt[0] == "q"):
        print("離開人臉訓練程序...")
        exit()
    if str.isnumeric(ipt):
        if len(ipt) <= 4:
            iptnum = int(ipt)
            break
        else:
            print("請輸入工號後面\"4位\"數字...(可不寫前面的0，ex:115)")
    else:
        print("請輸入工號後面4位\"數字\"...")

#創造該員工ID的資料夾
fullnum = str(iptnum).zfill(4)
if os.path.exists('TW'+fullnum) == False:
    os.makedirs('TW'+fullnum)

print('開啟相機...')                               # 提示啟用相機
cap = cv2.VideoCapture(0)                         # 啟用相機
if not cap.isOpened():
    print("無法啟用相機")
    exit()
k = 0
while k < 30:
    ret, img = cap.read()                         # 讀取影片的每一幀
    if not ret:
        print("無法取得frame")
        break
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 色彩轉換成黑白
    img_np = np.array(gray,'uint8')               # 轉換成指定編碼的 numpy 陣列
    face = face_cascade.detectMultiScale(gray)    # 擷取人臉區域
    for(x,y,w,h) in face:
        if (w > 100) & (h > 100):
            cv2.imwrite('.\\TW'+fullnum+"\\"+dt.now().strftime("%Y%m%d%H%M%S%f")+"123.png", gray[y:y+h, x:x+w])
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
            k += 1
        else:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
    cv2.imshow('Capturing Mode...', img)            # 顯示攝影機畫面
    cv2.waitKey(100)
print('OK!')

