import os, threading, sys
from concurrent.futures import ThreadPoolExecutor
import cv2
import pickle
import face_recognition
import numpy as np

stranger_path = 'person/stranger/'
acquaintance_path = 'person/recongnition/'
datapickle_path = 'person/data.pickle'

class FaceRecongnition:
    # 创建人脸编码和人名的映射
    faces = {}
    face_encodings = []
    face_names = []

    def __init__(self):
        with open(datapickle_path, 'rb') as f:
            if (os.path.getsize(datapickle_path) > 0):
                self.faces = pickle.load(f)
        self.face_encodings = list(self.faces.values())
        self.face_names = list(self.faces.keys())

    # 从文件中反序列化对象
    def read_data():
        with open(datapickle_path, 'rb') as f:
            if (os.path.getsize(datapickle_path) > 0):
                return pickle.load(f)
    
    def face_handle(self,frame):
        # 将抓取的帧转换为RGB
        # rgb_frame = frame[:, :, ::-1]
        # 创建一个可编辑的副本
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 检测当前帧中的人脸
        face_locations = face_recognition.face_locations(frame)
        if face_locations:
            capture_face_encodings = face_recognition.face_encodings(frame, face_locations)
        else:
            return frame
        matches = self.face_compare_future(capture_face_encodings)
        # 对检测到的人脸进行识别和跟踪
        for (top, right, bottom, left), capture_face_encoding in zip(face_locations, capture_face_encodings):
            if matches:
                # 如果找到匹配的人脸，从映射中获取姓名
                name = 'know' # self.face_names[matches]
                # 在图像上标注姓名
                frame = cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                frame = cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
            else:
                frame = cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                frame = cv2.putText(frame, 'stanger', (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
        return frame
    
    def face_compare_future(self,capture_face_encodings):
        capture_names = []
        if self.face_encodings:
            # 对每个人脸进行编码
            for face_encoding in capture_face_encodings:
                matches = face_recognition.compare_faces(self.face_encodings, face_encoding, 0.03)
                count = 0
                for matche in matches:
                    count_true = np.sum(matche)/np.size(matche)
                    if count_true > 0.8:
                        capture_names.append(self.face_names[count])
                    count += 1
        return capture_names