import os
import numpy as np
import cv2
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, qRgb
import fileUpLoad,faceCongnition

face_handl = faceCongnition.FaceRecongnition()

# 摄像头的IP地址,http://用户名：密码@IP地址：端口/
ip_camera_url = 'http://192.168.4.1:81/stream'
# 创建一个VideoCapture
cap = cv2.VideoCapture(ip_camera_url)
#调节摄像头分辨率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
#设置FPS
cap.set(cv2.CAP_PROP_FPS, 30)


def gui_display():
    window = QWidget()
    window.setWindowTitle('OpenCV 图片显示')
    window.setGeometry(100, 100, 800, 600)

    # 创建 QLabel 控件用于显示图片
    window.image_label = QLabel()
    window.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 图片居中显示
    # 创建布局并将 QLabel 添加到布局中
    layout = QVBoxLayout()
    layout.addWidget(window.image_label)
    # 设置主窗口的布局
    window.setLayout(layout)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            return
        frame = face_handl.face_handle(frame)
        # 加载并显示图片
        # OpenCV 图片转换为 QImage
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        # 将 QImage 转换为 QPixmap 显示在 QLabel 上
        pixmap = QPixmap.fromImage(q_image)
        window.image_label.setPixmap(pixmap)
        window.image_label.setScaledContents(True)  # 图片自适应控件大小
        window.show()
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    return window

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = gui_display()
    #关闭摄像头并销毁窗口
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(app.exec())
