import face_recognition
import os
import numpy as np
import cv2
import pickle

stranger_path = 'person/stranger/'
acquaintance_path = 'person/recongnition/'
datapickle_path = 'person/data.pickle'

def move_file(source_path, destination_path):
    try:
        os.replace(source_path,destination_path)
    except FileNotFoundError:
        print(f"文件{source_path}不存在")
    except PermissionError:
        print(f"没有权限移动文件{source_path}")


face_encodings = {}
# 从文件中反序列化对象
with open(datapickle_path, 'rb') as f:
    if (os.path.getsize(datapickle_path) > 0):
        face_encodings = pickle.load(f)

# 读取person文件夹中的图像和姓名
for filename in os.listdir(stranger_path):
    if filename.endswith('.jpg'):
        person_names = os.path.splitext(filename)[0]
        image = face_recognition.load_image_file(stranger_path+filename)
        #获取图像中所有人脸的编码
        face_encodings[person_names] = face_recognition.face_encodings(image)[0]
        move_file(stranger_path+filename, acquaintance_path+filename)

# 序列化对象到文件
with open(datapickle_path, 'wb') as f:
    pickle.dump(face_encodings, f)

#获取图片
image = face_recognition.load_image_file('person/recongnition/leijun.jpg')
#找到人脸的位置
face_locations = face_recognition.face_locations(image)
#获取图像中所有人脸的编码
face_encoding = face_recognition.face_encodings(image,face_locations)
#比对人脸
matches = face_recognition.compare_faces(face_encodings['leijun'],face_encoding)
print(face_locations)
for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
    if True in matches:
        cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(image, 'leijun', (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

while True:
    cv2.imshow('imag',image)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break