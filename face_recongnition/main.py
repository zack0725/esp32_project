import sys
import requests
import cv2
img_src = 'http://192.168.4.1/capture'
response = requests.get(img_src)
# with open('F:/project/esp32_project/face_recongnition/images/2tmp.jpg','wb') as file_obj:
#     file_obj.write(response.content)
cv2.namedWindow('Window', flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
#打开USB摄像头
cap = cv2.VideoCapture(0)
# 摄像头的IP地址,http://用户名：密码@IP地址：端口/
ip_camera_url = 'http://192.168.4.1:81/stream'
# 创建一个VideoCapture
cap = cv2.VideoCapture(ip_camera_url)
print('IP摄像头是否开启： {}'.format(cap.isOpened()))

# 显示缓存数
print(cap.get(cv2.CAP_PROP_BUFFERSIZE))
# 设置缓存区的大小
cap.set(cv2.CAP_PROP_BUFFERSIZE,1)

#调节摄像头分辨率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#设置FPS
print('setfps', cap.set(cv2.CAP_PROP_FPS, 20))
print(cap.get(cv2.CAP_PROP_FPS))

while(True):
    #逐帧捕获
    ret, frame = cap.read()  #第一个参数返回一个布尔值（True/False），代表有没有读取到图片；第二个参数表示截取到一帧的图片
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('Window', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#当一切结束后，释放VideoCapture对象
cap.release()
cv2.destroyAllWindows()