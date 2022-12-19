"""
File Name: Rec_GetFaceFeature.py
Program IDE: Visual Studio Code
Date: 2022/09/30
Create File By Author: Keaton Yang
"""

import cv2
from FacialRecognition.arcface.resnet import resnet_face18
import torch
import numpy as np
import os
import pickle
import sys
from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets

# from FacialRecognition.Rec_SCRFD import SCRFD    ###你还可以选择其他的人脸检测器

def convert_onnx():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model_path = 'FacialRecognition/arcface/resnet18_110.pth'
    model = resnet_face18(use_se=False)
    # model = torch.nn.DataParallel(model)
    # model.load_state_dict(torch.load(model_path, map_location=device))

    state_dict = torch.load(model_path, map_location=device)
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        new_state_dict[k.replace('module.', '')] = v    ## remove 'module.'
    model.load_state_dict(new_state_dict)

    model.to(device)
    model.eval()
    dummy_input = torch.randn(1, 1, 128, 128).to(device)
    onnx_path = 'FacialRecognition/arcface/resnet18_110.onnx'
    torch.onnx.export(model, dummy_input, onnx_path, input_names=['input'], output_names=['output'])

class arcface(QtCore.QThread):
    def __init__(self, model_path='FacialRecognition/arcface/resnet18_110.pth'):
        self.model = resnet_face18(use_se=False)
        # self.model = torch.nn.DataParallel(self.model)
        # self.model.load_state_dict(torch.load(model_path, map_location=device))

        state_dict = torch.load(model_path, map_location=torch.device('cpu'))
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            new_state_dict[k.replace('module.', '')] = v  ## remove 'module.'
        self.model.load_state_dict(new_state_dict)

        self.model.to(torch.device('cpu'))
        self.model.eval()
        self.device = torch.device('cpu')
    def get_feature(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, (128, 128), interpolation=cv2.INTER_AREA)
        img = img[np.newaxis, np.newaxis, :, :]
        # img = np.transpose(img, axes=(2,0,1))
        # img = img[np.newaxis, :, :, :]
        img = img.astype(np.float32, copy=False)
        img -= 127.5
        img /= 127.5
        with torch.no_grad():
            data = torch.from_numpy(img).to(self.device)
            output = self.model(data)
            output = output.data.cpu().numpy()
        return output

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

class GetFaceFeature(QtCore.QThread):

    rawstr = QtCore.pyqtSignal(str)
    rawnum = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

    def train_from_all_photos(self):
        # device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # face_embdnet = arcface(device=device)
        face_embdnet = arcface_dnn()   ###已调试通过，与pytorch版本的输出结果吻合
        # detect_face = SCRFD()

        out_emb_path = 'FacialRecognition/MDIT_members_arcface.pkl'
        imgroot = 'Images'
        dirlist = os.listdir(imgroot)    ### imgroot里有多个文件夹，每个文件夹存放着一个人物的多个肖像照，文件夹名称是人名
        feature_list, name_list = [], []
        for i,name in enumerate(dirlist):
            self.rawstr.emit("讀取第"+str(i+1)+"位成員照片並辨識"+name+"...")
            self.rawnum.emit(i/len(dirlist)*0.9999)
            imgdir = os.path.join(imgroot, name)
            imglist = os.listdir(imgdir)
            for j,imgname in enumerate(imglist):
                self.rawnum.emit(((i+j/len(imglist))/len(dirlist))*0.9999)
                if imgname.endswith('png'):
                    faceencrypt = cv2.imread(os.path.join(imgdir, imgname))
                    facekey = cv2.imread(os.path.join(imgdir, imgname[:-3]+'tif'))
                    srcimg = cv2.bitwise_xor(faceencrypt, facekey)
                    # cv2.imshow('face',srcimg)
                    # cv2.waitKey(1)
                    feature_out = face_embdnet.get_feature(srcimg)
                    feature_list.append(np.squeeze(feature_out))
                    name_list.append(name)

        self.rawstr.emit('訓練中...')
        self.rawnum.emit(0.9999)

        if len(feature_list)>0:
            face_feature = (np.asarray(feature_list), name_list)
            with open(out_emb_path, 'wb') as f:
                pickle.dump(face_feature, f)

        self.rawstr.emit('訓練完成！')
        self.rawnum.emit(1.0)