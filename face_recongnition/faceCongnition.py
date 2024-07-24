from shelve import Shelf
import face_recognition
import os
import numpy as np
import cv2
import pickle
import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QPixmap, QImage, qRgb

stranger_path = 'person/stranger/'
acquaintance_path = 'person/recongnition/'
datapickle_path = 'person/data.pickle'

class FaceRecongnition:
    # 创建人脸编码和人名的映射
    face_encodings = {}
    def __init__(self):
        with open(datapickle_path, 'rb') as f:
            if (os.path.getsize(datapickle_path) > 0):
                self.face_encodings = pickle.load(f)

    # 从文件中反序列化对象
    def read_data():
        with open(datapickle_path, 'rb') as f:
            if (os.path.getsize(datapickle_path) > 0):
                return pickle.load(f)
    
    def face_handle(self,frame):
        # 将抓取的帧转换为RGB
        rgb_frame = frame[:, :, ::-1]
    
        print(rgb_frame)
        # 检测当前帧中的人脸
        face_locations = face_recognition.face_locations(rgb_frame)
        if face_locations:
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        else:
            return frame
        # 对检测到的人脸进行识别和跟踪
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # 比对已知人脸编码
            matches = face_recognition.compare_faces(Shelf.face_encodings, face_encoding)
            if True in matches:
                # 如果找到匹配的人脸，从映射中获取姓名
                name = 'pass'
                # 在图像上标注姓名
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
            else:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        return frame