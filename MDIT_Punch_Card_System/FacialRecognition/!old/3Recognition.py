import cv2

recognizer = cv2.face.LBPHFaceRecognizer_create()         # 啟用訓練人臉模型方法
recognizer.read('face.yaml')
# 載入人臉追蹤模型
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')        # 啟用人臉追蹤


cap = cv2.VideoCapture(0)                                 # 開啟攝影機
if not cap.isOpened():
    print("不能開啟相機")
    exit()
while True:
    ret, img = cap.read()
    if not ret:
        print("不能獲取frame")
        break
    img = cv2.resize(img,(640,480))              # 縮小尺寸，加快辨識效率
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)  # 轉換成黑白
    faces = face_cascade.detectMultiScale(gray)  # 追蹤人臉 ( 目的在於標記出外框 )

    face_id_conf = []
    # 依序判斷每張臉屬於哪個 id
    for(x,y,w,h) in faces:
        idnum, confidence = recognizer.predict(gray[y:y+h, x:x+w])
        if confidence < 50:
            # text = name[str(idnum)]                               # 如果信心指數小於 60，取得對應的名字
            text = "id="+str(idnum)+" conf="+str(round(confidence,1))
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)        # 標記人臉外框
            cv2.putText(img, text, (x,y-5),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA) # 在人臉外框旁加上名字
        else:
            text = "??? conf="+str(round(confidence,1))                                   # 不然名字就是 ???
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)        # 標記人臉外框
            cv2.putText(img, text, (x,y-5),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA) # 在人臉外框旁加上名字

    cv2.imshow('Recognizing Faces...', img)
    if cv2.waitKey(5) == ord('q'):
        break    # 按下 q 鍵停止
cap.release()
cv2.destroyAllWindows()