"""
File Name: Speech.py
Program IDE: Visual Studio Code
Date: 2022/09/28
Create File By Author: Keaton Yang
"""
# Python: Convert Text to Speech [Beginner’s Guide]
#https://www.codingem.com/python-text-to-speech/
#Python文字轉語音(Text TO Speech)
#https://yanwei-liu.medium.com/python%E6%96%87%E5%AD%97%E8%BD%89%E8%AA%9E%E9%9F%B3-text-to-speech-f16609f80df9
from gtts import gTTS
from pygame import mixer
import tempfile


from PyQt5 import QtCore, QtGui, QtWidgets

class Speech(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 Speech 類別

    sentence = ''
    lang = 'zh-tw'
    sfx = ''

    def __init__(self, parent=None):
        """ 初始化
            - 執行 QtCore.QThread 的初始化
        """
        # 將父類初始化
        super().__init__(parent)

    def speak(self, sentence, lang, sfx=''):
        self.sentence = sentence
        self.lang = lang
        self.sfx = sfx
        self.start()

    def run(self):
        with tempfile.NamedTemporaryFile(delete=True) as fp:
            self.tts = gTTS(text=self.sentence, lang=self.lang)
            self.tts.save('{}.mp3'.format(fp.name))
            mixer.init()
            mixer.music.load('{}.mp3'.format(fp.name))
        if self.sfx != '':
            mixer.music.queue('SFXs/'+self.sfx)
            self.sfx = ''
        mixer.music.play()
