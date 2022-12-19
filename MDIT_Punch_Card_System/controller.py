"""
File Name: controller.py
Program IDE: Visual Studio Code
Date: 2022/10/06
Create File By Author: Keaton Yang
"""
# PyQt5：完成一個 WebCam GUI 程式
# https://yang10001.yia.app/wp/2021/05/15/pyqt5-%E5%AE%8C%E6%88%90%E4%B8%80%E5%80%8B-webcam-gui-%E7%A8%8B%E5%BC%8F/
# 引入相關模組
import time
from datetime import datetime
import random

# 引入介面的模組
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from UI_raw import UI_MDIT, UI_MDIT_About, UI_MDIT_Training, UI_MDIT_Staff
from FacialRecognition.Rec_DetectFaceAlign import DetectFaceAlign
from FacialRecognition.Rec_Record import ImageRecorder
from FacialRecognition.Rec_GetFaceFeature import GetFaceFeature
from TextToSpeech.Speech import Speech
from SMTP.SMTP import SendEmail
from StaffList.Staff import StaffName

# 開始來設計我們的 controller.py，改以「程式角度」來說明如何建立 PyQt 的系統
# https://ithelp.ithome.com.tw/articles/10268341
# 建立類別來繼承 Ui_MainWindow 介面程式
class MainWindow_controller(QtWidgets.QMainWindow):

    greatings = ["您好", "歡迎來到MDIT", "嗨，您好", "歡迎使用打卡系統", "今天氣色不錯喔", "哈嘍您好", "開啟打卡系統介面", "好喔"]
    message = "歡迎使用MDIT人臉識別系統..."
    punchID = []
    coolingdown = 0

    # 初始化方法
    def __init__(self):
        """ 初始化
            - 物件配置
            - 相關屬性配置
        """
        # 繼承視窗程式所有的功能
        super().__init__()  # in python3, super(Class, self).xxx = super().xxx
        self.ui = UI_MDIT.Ui_MainWindow()
        # 配置 pyqt5 的物件
        self.ui.setupUi(self)
        self.ui.cameraVis.setScaledContents(True)
        self.setup_control()
        # 設定相機功能
        self.ProcessCam = DetectFaceAlign()  # 建立相機物件
        if self.ProcessCam.connect:
            # 連接影像訊號 (rawdata) 至 getRaw()
            self.ProcessCam.rawdata.connect(self.getRaw)  # 槽功能：取得並顯示影像
            self.ProcessCam.rawid.connect(self.getRawID)
            self.ProcessCam.rawstr.connect(self.getRawStr)
            self.ProcessCam.open()   # 影像讀取功能開啟
            self.ProcessCam.start()  # 在子緒啟動影像讀取
        self.Speech = Speech()  # 建立語音物件
        self.Speech.speak(self.greatings[random.randint(0,7)], 'zh-tw')
        self.Staff = StaffName()  # 建立人員物件
        self.Staff.csv_to_dataframe()
        self.Email = SendEmail()  # 建立寄信物件
        self.Email.rawstr.connect(self.getRawStrE)

    def getRaw(self, data):  # data 為接收到的影像
        """ 取得影像 """
        self.showData(data)  # 將影像傳入至 showData()

    def showData(self, img):
        """ 顯示攝影機的影像 """
        self.Ny, self.Nx, _ = img.shape  # 取得影像尺寸
        # 建立 Qimage 物件 (灰階格式)
        # qimg = QtGui.QImage(img[:,:,0].copy().data, self.Nx, self.Ny, QtGui.QImage.Format_Indexed8)
        # 建立 Qimage 物件 (RGB格式)
        qimg = QtGui.QImage(img.data, self.Nx, self.Ny, QtGui.QImage.Format_BGR888)
        # viewData 的顯示設定
        self.ui.cameraVis.setScaledContents(True)  # 尺度可變
        ### 將 Qimage 物件設置到 cameraVis 上
        self.ui.cameraVis.setPixmap(QtGui.QPixmap.fromImage(qimg))

    def getRawStr(self, iptstr):  # str 為接收到的文字
        self.message = iptstr
        self.set_status_label(self.message)

    def getRawStrE(self, iptstr):  # str 為接收到的文字
        self.message = iptstr
        self.set_status_label(self.message)

    def getRawID(self, lists):  # data 為接收到的影像
        """ 取得成員 """
        name = lists[0]
        # punchID是累積打卡能量的list
        # str_match會篩出ID名稱name的數量，如果不等於1則做增加或清除
        str_match = list(filter(lambda x: name in x, self.punchID))
        if (len(str_match)) == 0:
            self.punchID.append([name, 1])
        elif (len(str_match)) > 1:
            rowpid = self.id_name_to_punchid_row(name)[0]
            self.punchID.pop(rowpid)
        elif (len(str_match) == 1) & (self.coolingdown < time.time()-5.0) & (name != 'unknown'):
            # 取出該ID在punchID這個list的哪一列
            rowpid = self.id_name_to_punchid_row(name)[0]
            # 取出該ID在Total這個DataFrame的哪一列
            rowttl = self.Staff.Total[(self.Staff.Total.ID == name)].index.tolist()[0]
            self.punchID[rowpid][1] += max(2.1-lists[1], 0.5)*100.0  #面孔越相像累加器累加速度越快
            self.ui.pgBar.setValue(int(self.punchID[rowpid][1]))
            self.ui.pgBar.setVisible(True)
            #如果確定要打卡，則將冷卻時間設為50
            if self.punchID[rowpid][1] > 1000:
                if self.ui.rdb1_work.isChecked():
                    self.punch_card_method(name, rowpid, rowttl, 1, 36.0)
                elif self.ui.rdb2_offwork.isChecked():
                    self.punch_card_method(name, rowpid, rowttl, 2, 36.0)
                elif self.ui.rdb3_out.isChecked():
                    self.punch_card_method(name, rowpid, rowttl, 3, 36.0)
                elif self.ui.rdb4_back.isChecked():
                    self.punch_card_method(name, rowpid, rowttl, 4, 36.0)
                else:
                    self.punch_card_method(name, rowpid, rowttl, 0, 36.0)

    def punch_card_method(self, name, rowpid, rowttl, typ, temp):
        if typ == 1: punchstr = "上班"
        elif typ == 2: punchstr = "下班"
        elif typ == 3: punchstr = "外出"
        elif typ == 4: punchstr = "返回"
        self.punchID[rowpid][1] = 0
        self.coolingdown = time.time()
        self.ui.pgBar.setValue(1000)
        if (typ >= 1) and (typ <= 4):
            self.set_status_label(punchstr+"打卡："+name+", "+self.Staff.Total['Name'][rowttl])
            if self.Staff.Total['SFX'][rowttl] == '預設':
                self.Speech.speak(punchstr+"打卡："+self.Staff.Total['Name'][rowttl], 'zh-tw', '')
            else:
                self.Speech.speak(punchstr+"打卡：", 'zh-tw', self.Staff.Total['SFX'][rowttl])
            # self.Email.send(typ, temp, [self.Staff.Total['Email'][rowttl]])
            # 寫入到檔案
            fp = open(datetime.now().strftime("%Y%m%d")+".txt", "a")
            fp.write(datetime.now().strftime("%Y%m%d")+" "+datetime.now().strftime("%H%M")+" "+name+" 00"+str(typ)+"\n")
            fp.close()
        else:
            self.set_status_label("請選擇上下班打卡類別...")
            self.Speech.speak(self.message, 'zh-tw')

    def id_name_to_punchid_row(self, v):
        for i, x in enumerate(self.punchID):
            if v in x:
                return i, x.index(v)

    #將要改寫的功能寫在這邊
    def setup_control(self):
        # TODO
        self.ui.actionTraining.triggered.connect(self.open_train_window)
        # self.ui.actionTraining.setEnabled(False) ##################################
        # self.ui.actionTraining.setVisible(False) ##################################
        self.ui.actionEditStaff.triggered.connect(self.open_staff_window)
        # self.ui.actionEditStaff.setEnabled(False) ##################################
        # self.ui.actionEditStaff.setVisible(False) ##################################
        self.ui.actionExit.triggered.connect(self.exit_window)
        self.ui.actionAbout.triggered.connect(self.open_about_dlg)
        self.ui.actionPassword.triggered.connect(self.ask_for_password)
        self.set_status_label(self.message)

    def set_status_label(self, message):
        self.message = message
        self.ui.lblStatusPunch.setText(message)

    #開啟訓練視窗
    def open_train_window(self):
        #PyQt5 - 关闭当前窗体同时打开新窗体（登录界面）
        #https://blog.csdn.net/qq_42292831/article/details/92184905
        self.close()
        time.sleep(0.5)
        self.trainWin = TrainingWindow_controller()
        self.trainWin.show()

    #開啟編輯視窗
    def open_staff_window(self):
        self.close()
        self.staffWin = StaffWindow_controller()
        self.staffWin.show()

    #開啟關於程序對話框
    def open_about_dlg(self):
        self.aboutDialog = AboutDialog_controller()
        self.aboutDialog.show()

    #啟用有密碼輸入列的對話框
    def ask_for_password(self):
        #PyQt5的输入对话框使用
        #https://blog.csdn.net/panrenlong/article/details/79948261
        password, ok = QtWidgets.QInputDialog.getText(self, "密碼", "請輸入密碼", QtWidgets.QLineEdit.Normal, "****")
        if ok:
            if password == "24384532":
                self.set_status_label("權限開啟，可以使用訓練與編輯成員功能...")
                self.ui.actionTraining.setEnabled(True)
                self.ui.actionTraining.setVisible(True)
                self.ui.actionEditStaff.setEnabled(True)
                self.ui.actionEditStaff.setVisible(True)

    #離開程序
    def exit_window(self):
        #python按鈕點選關閉視窗的實現
        #https://www.796t.com/article.php?id=15669
        app = QtWidgets.QApplication.instance()
        app.quit()

    def closeEvent(self, event):
        self.ProcessCam.close()

#############################################################################################################

class TrainingWindow_controller(QtWidgets.QMainWindow):
    message = "閒置中..."
    # 初始化方法
    def __init__(self):
        # 繼承視窗程式所有的功能
        super().__init__()  # in python3, super(Class, self).xxx = super().xxx
        self.ui = UI_MDIT_Training.Ui_MainWindow()
        # 配置 pyqt5 的物件
        self.ui.setupUi(self)
        # 設定相機功能
        self.frame_num = 0
        self.ProcessCam = ImageRecorder()  # 建立相機物件
        if self.ProcessCam.connect:
            # 連接影像訊號 (rawdata) 至 getRaw()
            self.ProcessCam.rawdata.connect(self.getRaw)  # 槽功能：取得並顯示影像
            self.ProcessCam.rawnum.connect(self.getRawNum)
            self.ProcessCam.rawstr.connect(self.getRawStr)
            self.ProcessCam.open()   # 影像讀取功能開啟
            self.ProcessCam.start()  # 在子緒啟動影像讀取
        self.Training = GetFaceFeature()  # 建立相機物件
        self.Training.rawstr.connect(self.getRawStrT)
        self.Training.rawnum.connect(self.getRawNumT)
        self.Speech = Speech()  # 建立語音物件
        self.Staff = StaffName()  # 建立人員物件
        self.Staff.csv_to_dataframe()
        self.setup_control()

    def set_status_label(self, message):
        self.message = message
        self.ui.lblStatusTrain.setText(message)

    def getRaw(self, data):  # data 為接收到的影像
        """ 取得影像 """
        self.showData(data)  # 將影像傳入至 showData()

    def showData(self, img):
        """ 顯示攝影機的影像 """
        self.Ny, self.Nx, _ = img.shape  # 取得影像尺寸
        # 建立 Qimage 物件 (灰階格式)
        # qimg = QtGui.QImage(img[:,:,0].copy().data, self.Nx, self.Ny, QtGui.QImage.Format_Indexed8)
        # 建立 Qimage 物件 (RGB格式)
        qimg = QtGui.QImage(img.data, self.Nx, self.Ny, QtGui.QImage.Format_BGR888)
        # viewData 的顯示設定
        self.ui.cameraCapture.setScaledContents(True)  # 尺度可變
        ### 將 Qimage 物件設置到 cameraCapture 上
        self.ui.cameraCapture.setPixmap(QtGui.QPixmap.fromImage(qimg))
        # Frame Rate 計算並顯示到狀態欄上
        if self.frame_num == 0:
            self.time_start = time.time()
        if self.frame_num >= 0:
            self.frame_num += 1
            self.t_total = time.time() - self.time_start
            if self.frame_num % 100 == 0:
                self.frame_rate = float(self.frame_num) / self.t_total
                self.ui.lblStatusTrain.setText(self.message+"FPS:"+str(round(self.frame_rate, 3)))

    def getRawNum(self, num):  # num 為接收到的數字
        if num < 100:    # 改變進度條的數字
            self.ui.pgBar.setValue(num)
            self.ui.pgBar.setMaximum(100)
        elif num == 100:    # 釋放所有按鈕功能
            self.ui.btnRecord.setEnabled(True)
            self.ui.btnTrain.setEnabled(True)
            self.ui.btnClear.setEnabled(True)
            self.ui.lineEdit.setEnabled(True)
            self.ui.pgBar.setValue(100)
            self.ui.pgBar.setMaximum(100)
            self.Speech.speak("擷取完成", 'zh-tw')

    def getRawNumT(self, num):  # num 為接收到的數字
        if num < 1.0:    # 改變進度條的數字
            self.ui.pgBar.setValue(int(num*10000))
            self.ui.pgBar.setMaximum(10000)
        elif num == 1.0:    # 釋放所有按鈕功能
            self.ui.btnRecord.setEnabled(True)
            self.ui.btnTrain.setEnabled(True)
            self.ui.btnClear.setEnabled(True)
            self.ui.lineEdit.setEnabled(True)
            self.ui.pgBar.setValue(10000)
            self.ui.pgBar.setMaximum(10000)
            self.Speech.speak(self.message, 'zh-tw')

    def getRawStr(self, iptstr):  # str 為接收到的文字
        self.message = iptstr
        self.set_status_label(self.message)

    def getRawStrT(self, iptstr):  # str 為接收到的文字
        self.message = iptstr
        self.set_status_label(self.message)

    #將要改寫的功能寫在這邊
    def setup_control(self):
        # TODO
        self.ui.btnRecord.clicked.connect(self.start_record)
        self.ui.btnTrain.clicked.connect(self.start_training)
        self.ui.btnClear.clicked.connect(self.delete_photos)
        self.ui.cbbCode.currentTextChanged.connect(self.select_code_name)

    def start_record(self):   # 凍結所有按鈕功能
        if self.examine_id(self.ui.lineEdit.text()):
            self.set_status_label("從相機擷取人臉圖片中，共擷取100張...")
            self.Speech.speak("開始擷取", 'zh-tw')
            self.ui.btnRecord.setEnabled(False)
            self.ui.btnTrain.setEnabled(False)
            self.ui.btnClear.setEnabled(False)
            self.ui.lineEdit.setEnabled(False)
            iptnum = int(self.ui.lineEdit.text())
            self.ProcessCam.create_folder(iptnum)
            self.ProcessCam.recordFlg = True
            iptstr = self.ProcessCam.recordCode + str(iptnum).zfill(4)
            iptflg = True
            for i in self.Staff.Total['ID']:
                if i == iptstr: iptflg = False
            if iptflg:
                self.Staff.insert_new_row(iptstr)
            self.Staff.dataframe_to_csv()

    def start_training(self):
        self.set_status_label("開始用所有成員照片進行AI訓練...")
        self.Speech.speak(self.message, 'zh-tw')
        self.ui.btnRecord.setEnabled(False)
        self.ui.btnTrain.setEnabled(False)
        self.ui.btnClear.setEnabled(False)
        self.ui.lineEdit.setEnabled(False)
        self.Training.train_from_all_photos()

    def delete_photos(self):
        # Create a message box with Python PyQt5
        # https://pythonprogramminglanguage.com/pyqt5-message-box/
        self.Speech.speak("Warning", 'en')
        ret = QMessageBox.warning(self, "警告", "此步驟將清除您輸入的ID的所有訓練相片！", QMessageBox.Ok | QMessageBox.Abort)
        if ret == QMessageBox.Ok:
            if self.examine_id(self.ui.lineEdit.text()):
                self.set_status_label("將" + self.ProcessCam.recordCode + str(int(self.ui.lineEdit.text())).zfill(4) + "的相片全數刪除...")
                self.Speech.speak("將" + self.ProcessCam.recordCode + str(int(self.ui.lineEdit.text())).zfill(4) + "的相片全數刪除...", 'zh-tw')
                self.ProcessCam.delete_folder(int(self.ui.lineEdit.text()))

    def select_code_name(self, value):
        self.ProcessCam.recordCode = value

    def examine_id(self, text):
        if str.isnumeric(text):
            if len(text) <= 4:
                return True
            else:
                self.set_status_label("請輸入工號後面\"4位\"數字...(可不寫前面的0，ex:115)")
                self.Speech.speak("工號格式錯誤", 'zh-tw')
                return False
        else:
            self.set_status_label("請輸入工號後面4位\"數字\"...")
            self.Speech.speak("工號格式錯誤", 'zh-tw')
            return False

    #截获窗口Widget组件的关闭事件
    #https://blog.csdn.net/LaoYuanPython/article/details/102511143
    def closeEvent(self, event):
        self.ProcessCam.close()
        time.sleep(0.5)
        self.mainWin = MainWindow_controller()
        self.mainWin.show()

#############################################################################################################

class StaffWindow_controller(QtWidgets.QMainWindow):
    message = "閒置中..."
    # 初始化方法
    def __init__(self):
        # 繼承視窗程式所有的功能
        super().__init__()  # in python3, super(Class, self).xxx = super().xxx
        self.ui = UI_MDIT_Staff.Ui_MainWindow()
        # 配置 pyqt5 的物件
        self.ui.setupUi(self)
        self.Staff = StaffName()  # 建立人員物件
        self.setup_control()
        self.ui.tblStaff.cellChanged.connect(self.cell_changed)

    def setup_control(self):
        # TODO
        self.ui.btnDelete.clicked.connect(self.delete_selection)
        self.ui.btnInsert.clicked.connect(self.insert_one_row)
        #表格初始化
        self.TotalList = []
        self.Staff.csv_to_dataframe()
        numrows = len(self.Staff.Total)
        self.ui.tblStaff.setColumnCount(5)
        self.ui.tblStaff.setRowCount(numrows)
        self.ui.tblStaff.setColumnWidth(0, 120)
        self.ui.tblStaff.setColumnWidth(1, 120)
        self.ui.tblStaff.setColumnWidth(2, 180)
        self.ui.tblStaff.setColumnWidth(3, 180)
        self.ui.tblStaff.setColumnWidth(4, 180)
        for i in range(len(self.Staff.Total['ID'])):
            ID = self.Staff.Total['ID'][i]
            self.create_table_item(i, 0, ID, True)
            self.create_table_item(i, 1, self.Staff.Total['Name'][i], True)
            self.create_table_item(i, 2, "/Images/"+ID+"/", False)
            self.create_table_item(i, 3, self.Staff.Total['SFX'][i], True)
            self.create_table_item(i, 4, self.Staff.Total['Email'][i], True)
            self.TotalList.append(ID)

    def set_status_label(self, message):
        self.message = message
        self.ui.lblStatus.setText(message)

    def create_table_item(self, row, col, content, enable):
        item = QtWidgets.QTableWidgetItem(content)
        item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        if enable: item.setFlags(QtCore.Qt.ItemFlag(63))  #恢復儲存格的默認設置
        else: item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)  #儲存格設定為不可編輯
        self.ui.tblStaff.setItem(row, col, item)

    def delete_selection(self):
        #[PyQt] Get a list of selected rows in a QTableWidget
        #https://riverbankcomputing.com/pipermail/pyqt/2010-March/026075.html
        self.ui.tblStaff.blockSignals(True)
        rows = []
        for idx in self.ui.tblStaff.selectionModel().selectedRows():
            rows.append(idx.row())
        if rows:
            rows = sorted(rows)
            self.set_status_label("執行刪除所選的資料列"+str(rows)+"...")
            j = 0
            for i in rows:
                #刪除表格內的列與資料夾與List與Dataframe
                row = self.Staff.Total[(self.Staff.Total.ID == self.ui.tblStaff.item(i-j,0).text())].index.tolist()[0]
                self.Staff.Total.drop(row, axis=0, inplace=True)
                self.Staff.delete_folder_name(self.ui.tblStaff.item(i-j,0).text())
                del self.TotalList[i-j]
                self.ui.tblStaff.removeRow(i-j)
                j += 1
        else:
            self.set_status_label("請選擇\"完整的列\"方可移除！")
        self.ui.tblStaff.blockSignals(False)
        self.Staff.dataframe_to_csv()

    def insert_one_row(self):
        self.ui.tblStaff.blockSignals(True)
        inum = 0
        while inum <= 9999:
            istr = "TW"+str(inum).zfill(4)
            if istr not in self.TotalList:
                break
            inum += 1
        if inum <= 9999:
            self.ui.tblStaff.insertRow(0)
            self.TotalList.insert(0, istr)
            self.Staff.insert_new_row(istr)
            self.Staff.create_folder_name(istr)
            self.create_table_item(0, 0, istr, True)
            self.create_table_item(0, 1, "YourName", True)
            self.create_table_item(0, 2, "/Images/"+istr+"/", False)
            self.create_table_item(0, 3, "預設", True)
            self.create_table_item(0, 4, "user@mitsuboshi-dia.co.jp", True)
            self.set_status_label("插入一行新資料...")
        else:
            self.set_status_label("達到TW系列序號最大值，已經無法再創建新ID...")
        self.ui.tblStaff.blockSignals(False)
        self.Staff.dataframe_to_csv()

    def cell_changed(self, row, column):
        #python QTableWidget单元格更改信号cellChanged()的使用
        #https://blog.csdn.net/qq_45773419/article/details/120026736
        self.ui.tblStaff.blockSignals(True)
        if column == 0:
            #如果要改變的字串沒有跟其他重複到，則改資料夾名稱與List與Dataframe
            if (self.Staff.change_folder_name(self.TotalList[row], self.ui.tblStaff.item(row, 0).text())):
                self.set_status_label("更改ID:"+self.TotalList[row]+"為"+self.ui.tblStaff.item(row, 0).text()+"成功，並同步變更目錄...")
                self.TotalList[row] = self.ui.tblStaff.item(row, 0).text()
                self.create_table_item(row, 2, "/Images/"+self.ui.tblStaff.item(row, 0).text()+"/", False)
            #如果要改變的字串有跟其他重複到，則不改資料夾名稱，List與Dataframe維持相同，Table改寫成原本的數值
            else:
                self.set_status_label("更改ID:"+self.TotalList[row]+"為"+self.ui.tblStaff.item(row, 0).text()+"失敗！ID名稱重複...")
                self.create_table_item(row, 0, self.TotalList[row], True)
        elif column == 1:
                self.set_status_label("更改名稱為"+self.ui.tblStaff.item(row, column).text()+"成功！")
                self.Staff.Total['Name'][row] = self.ui.tblStaff.item(row, column).text()
        elif column == 3:
                self.set_status_label("更改音效為"+self.ui.tblStaff.item(row, column).text()+"成功！")
                self.Staff.Total['SFX'][row] = self.ui.tblStaff.item(row, column).text()
        elif column == 4:
                self.set_status_label("更改信箱為"+self.ui.tblStaff.item(row, column).text()+"成功！")
                self.Staff.Total['Email'][row] = self.ui.tblStaff.item(row, column).text()
        self.ui.tblStaff.blockSignals(False)
        self.Staff.dataframe_to_csv()

    def closeEvent(self, event):
        self.mainWin = MainWindow_controller()
        self.mainWin.show()

#############################################################################################################

class AboutDialog_controller(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = UI_MDIT_About.Ui_Dialog()
        #視窗永遠顯示在最上層
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.ui.setupUi(self)