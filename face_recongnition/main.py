import sys
import requests
import face_recognition
import cv2
# img_src = 'http://192.168.4.1/capture'
# response = requests.get(img_src)
# with open('person/recongnition/tem1.jpg','wb') as file_obj:
#     file_obj.write(response.content)

# 摄像头的IP地址,http://用户名：密码@IP地址：端口/
ip_camera_url = 'http://192.168.4.1:81/stream'
# 创建一个VideoCapture
cap = cv2.VideoCapture(ip_camera_url)
ret, frame = cap.read()
rgb_frame = frame[:, :, ::-1]
# while True:
#     cv2.imshow('Video', rgb_frame)
#     # 按 'q' 退出循环
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#获取图片
# image = face_recognition.load_image_file(rgb_frame)
#找到人脸的位置
print('face_locations')
face_locations = face_recognition.face_locations(frame)
print(face_locations)
#获取图像中所有人脸的编码
face_encoding = face_recognition.face_encodings(frame,face_locations)