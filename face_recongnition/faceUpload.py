import face_recognition
import os
import numpy as np
import cv2
import pickle
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QLineEdit, QHBoxLayout, QDialog, QPushButton, QVBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPixmap, QImage, qRgb
from PIL import Image
from pathlib import Path

def move_file(source_path, destination_path):
    try:
        os.replace(source_path,destination_path)
    except FileNotFoundError:
        print(f"文件{source_path}不存在")
    except PermissionError:
        print(f"没有权限移动文件{source_path}")
def file_save(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

class FaceUpload(QDialog):
    stranger_path = 'person/stranger/'
    acquaintance_path = 'person/recongnition/'
    datapickle_path = 'person/data.pickle'
    face_encodings = {}
    face_encoding = []
    is_face = False
    face_count = 0

    def __init__(self,image_path):
        super().__init__()
        self.image_path = image_path
        # 从文件中反序列化对象
        with open(self.datapickle_path, 'rb') as f:
            if (os.path.getsize(self.datapickle_path) > 0):
                self.face_encodings = pickle.load(f)
        self.initUI()


    def initUI(self):
        self.setWindowTitle('文件上传工具')
        self.setGeometry(800, 500, 300, 150)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.image_label = QLabel()
        self.layout.addWidget(self.image_label)

        self.tip_label = QLabel('')
        self.tip_label.setStyleSheet('color: red;')
        self.layout.addWidget(self.tip_label)

        # 创建水平布局，用于放置按键
        enter_layout = QHBoxLayout()
        self.layout.addLayout(enter_layout)

        # 创建一个标签和一个输入框
        self.text_label = QLabel('请输入名字:', self)
        enter_layout.addWidget(self.text_label,1)
        
        self.line_edit = QLineEdit(self)
        enter_layout.addWidget(self.line_edit,5)

        self.ok_button = QPushButton("确定", self)
        self.ok_button.clicked.connect(self.on_ok_button_clicked)
        enter_layout.addWidget(self.ok_button,2)

        self.cancel_button = QPushButton("取消", self)
        self.cancel_button.clicked.connect(self.on_ok_button_clicked)
        enter_layout.addWidget(self.cancel_button,2)

        self.load_image()  # 图片自适应 QLabel 大小
    
    # 加载图片文件
    def load_image(self):
        pixmap = QPixmap(self.image_path)
        # 获取人脸的位置
        img = face_recognition.load_image_file(self.image_path)
        face_locations = face_recognition.face_locations(img)
        if face_locations:
            self.is_face = True
            # 对图片进行编码
            self.face_encoding = face_recognition.face_encodings(img,face_locations)
            for top, right, bottom, left in face_locations:
                self.face_count += 1
                cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)
            # 将 cv2imag 转换为 QPixmap 显示在 QLabel 上
            height, width, channel = img.shape
            bytes_per_line = channel * width
            img = QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(True)  # 图片自适应 QLabel 大小
            if not self.is_face:
                self.tip_label.setText("未检测到人脸")
            elif self.face_count > 1:
                self.tip_label.setText("人脸数大于1")
        else:
            self.image_label.setText("Image load failed")

    def on_ok_button_clicked(self):
        msg = QMessageBox()
        input_text = self.line_edit.text()
        if not input_text:
            self.tip_label.setText("名字不能为空")
            return
        if not self.is_face or self.face_count > 1:
            pass
            # self.tip_label.setText("保存失败,未检测到人脸或人脸数大于1")
            # msg.setWindowTitle('提示')
            # msg.setText('保存失败,未检测到人脸或人脸数大于1')
            # msg.setIcon(QMessageBox.Icon.Information)
            # msg.setStandardButtons(QMessageBox.StandardButton.Ok) 
            # msg.exec() 
        else:
            self.file_name = input_text
            self.face_data_save()
        return

    def on_ok_button_clicked(self):
        self.close()
    
    def face_data_save(self):
        person_names = self.file_name
        #获取图像中所有人脸的编码
        self.face_encodings[person_names] = self.face_encoding
        move_file(self.image_path, self.acquaintance_path+person_names+Path(self.image_path).suffix)
        
        # 序列化对象到文件
        with open(self.datapickle_path, 'wb') as f:
            pickle.dump(self.face_encodings, f)

