import os, threading, sys
from concurrent.futures import ThreadPoolExecutor
import cv2
import pickle
import face_recognition
import numpy as np

stranger_path = 'person/stranger/'
acquaintance_path = 'person/recongnition/'
datapickle_path = 'person/data.pickle'

def empty_task():
    pass

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
        self.is_face_start = False
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.face_compare_future = self.executor.submit(empty_task)

    # 从文件中反序列化对象
    def read_data():
        with open(datapickle_path, 'rb') as f:
            if (os.path.getsize(datapickle_path) > 0):
                return pickle.load(f)
    
    def face_handle(self,frame):
        # 转换图片的格式
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 检测当前帧中的人脸
        face_locations = face_recognition.face_locations(frame)
        if face_locations:
            capture_face_encodings = face_recognition.face_encodings(frame, face_locations)
        else:
            return frame
        
        if not self.is_face_start:
            self.is_face_start = True
            # 开辟一个线程用于比较人脸
            self.face_compare_future = self.executor.submit(self.face_compare, capture_face_encodings)
        elif self.is_face_start and self.face_compare_future.done():
            self.is_face_start = False
            capture_names, find_face_encodings = self.face_compare_future.result()
            for face_encoding in capture_face_encodings:
                matches = face_recognition.compare_faces(find_face_encodings, face_encoding)
                if False in matches:
                    for top, right, bottom, left in face_locations:
                        frame = cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    return frame
            # 对检测到的人脸进行识别和跟踪
            for (top, right, bottom, left), capture_name in zip(face_locations, capture_names):
                name = capture_name 
                frame = cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                frame = cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
        else:
            for top, right, bottom, left in face_locations:
                frame = cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        return frame
    
    def face_compare(self,capture_face_encodings):
        capture_names = []
        is_find = False
        if self.face_encodings:
            # 对每个人脸进行编码
            for face_encoding in capture_face_encodings:
                matches = face_recognition.compare_faces(self.face_encodings, face_encoding, 0.03)
                count = 0
                for matche in matches:
                    count_true = np.sum(matche)/np.size(matche)
                    if count_true > 0.6:
                        is_find = True
                        capture_names.append(self.face_names[count])
                        break
                    count += 1
                if not is_find:
                        capture_names.append("stranger")
                is_find = False
        return capture_names, capture_face_encodings