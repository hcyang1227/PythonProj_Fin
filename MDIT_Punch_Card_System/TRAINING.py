"""
File Name: TRAINING.py
Program IDE: Visual Studio Code
Date: 2022/10/12
Create File By Author: Keaton Yang
"""

import cv2
import os
from PyQt5 import QtCore, QtGui, QtWidgets
import pickle
import numpy as np

class arcface_dnn(QtCore.QThread):
    def __init__(self, model_path='FacialRecognition/arcface/resnet18_110.onnx'):
        self.model = cv2.dnn.readNetFromONNX(model_path)
        self.input_size = (128, 128)
    def get_feature(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, self.input_size, interpolation=cv2.INTER_AREA)
        blob = cv2.dnn.blobFromImage(img, scalefactor=1 / 127.5, mean=127.5)
        self.model.setInput(blob)
        output = self.model.forward(['output'])
        return output

# device = 'cuda' if torch.cuda.is_available() else 'cpu'
# face_embdnet = arcface(device=device)
face_embdnet = arcface_dnn()   ###已调试通过，与pytorch版本的输出结果吻合
# detect_face = SCRFD()

out_emb_path = 'MDIT_members_arcface.pkl'
imgroot = 'Images'
dirlist = os.listdir(imgroot)    ### imgroot里有多个文件夹，每个文件夹存放着一个人物的多个肖像照，文件夹名称是人名
feature_list, name_list = [], []
for i,name in enumerate(dirlist):
    print("讀取第"+str(i+1)+"位成員照片並辨識"+name+"...", end="")
    imgdir = os.path.join(imgroot, name)
    imglist = os.listdir(imgdir)
    for j,imgname in enumerate(imglist):
        print(".", end="")
        if imgname.endswith('png'):
            faceencrypt = cv2.imread(os.path.join(imgdir, imgname))
            facekey = cv2.imread(os.path.join(imgdir, imgname[:-3]+'tif'))
            srcimg = cv2.bitwise_xor(faceencrypt, facekey)
            # cv2.imshow('face',srcimg)
            # cv2.waitKey(1)
            feature_out = face_embdnet.get_feature(srcimg)
            feature_list.append(np.squeeze(feature_out))
            name_list.append(name)
    print()

print('訓練中...')

if len(feature_list)>0:
    face_feature = (np.asarray(feature_list), name_list)
    with open(out_emb_path, 'wb') as f:
        pickle.dump(face_feature, f)

print('訓練完成！')