import face_recognition
import os
import numpy as np
import cv2
import pickle
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QHBoxLayout, QDialog, QPushButton, QVBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap


def move_file(source_path, destination_path):
    try:
        os.replace(source_path,destination_path)
    except FileNotFoundError:
        print(f"文件{source_path}不存在")
    except PermissionError:
        print(f"没有权限移动文件{source_path}")

#self.
class FaceUpload(QDialog):
    stranger_path = 'person/stranger/'
    acquaintance_path = 'person/recongnition/'
    datapickle_path = 'person/data.pickle'
    face_encodings = {}

    def __init__(self,image_path):
        self.setWindowTitle('文件上传工具')

        self.layout = QVBoxLayout()
        self.image_label = QLabel()
        self.layout.addWidget(self.image_label)
        
        pixmap = QPixmap(self.file_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)  # 图片自适应 QLabel 大小

        # 创建水平布局，用于放置按键
        enter_layout = QHBoxLayout()
        self.layout.addLayout(enter_layout)

        # 创建一个标签和一个输入框
        self.text_label = QLabel('请输入名字:', self)
        enter_layout.addWidget(self.text_label)
        
        self.line_edit = QLineEdit(self)
        enter_layout.addWidget(self.textbox)

        self.ok_button = QPushButton("确定", self)
        self.ok_button.clicked.connect(self.on_ok_button_clicked)
        enter_layout.addWidget(self.ok_button)

        self.image_path = image_path
        self.file_name = os.path.basename(image_path)

        # 从文件中反序列化对象
        with open(self.datapickle_path, 'rb') as f:
            if (os.path.getsize(self.datapickle_path) > 0):
                self.face_encodings = pickle.load(f)
    
    def on_ok_button_clicked(self):
        self.close()

    def face_encoding(self):
        person_names = os.path.splitext(self.file_name)[0]
        image = face_recognition.load_image_file(self.stranger_path+self.file_name)
        #获取图像中所有人脸的编码
        self.face_encodings[person_names] = face_recognition.face_encodings(image)[0]
        move_file(self.stranger_path+self.file_name, self.acquaintance_path+self.file_name)

        # 序列化对象到文件
        with open(self.datapickle_path, 'wb') as f:
            pickle.dump(self.face_encodings, f)

    def face_compare():
        pass
        # #获取图片
        # image = face_recognition.load_image_file('person/recongnition/leijun.jpg')
        # #找到人脸的位置
        # face_locations = face_recognition.face_locations(image)
        # #获取图像中所有人脸的编码
        # face_encoding = face_recognition.face_encodings(image,face_locations)
        # #比对人脸
        # matches = face_recognition.compare_faces(face_encodings['leijun'],face_encoding)
        # print(face_locations)
        # for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        #     if True in matches:
        #         cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
        #         cv2.putText(image, 'leijun', (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)


