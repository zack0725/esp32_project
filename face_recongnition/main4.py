import os
import numpy as np
import cv2
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPixmap, QImage, qRgb
import fileUpLoad,faceCongnition

face_handl = faceCongnition.FaceRecongnition()

def start_cpature():
    # 摄像头的IP地址,http://用户名：密码@IP地址：端口/
    ip_camera_url = 'http://192.168.4.1:81/stream'
    # 创建一个VideoCapture
    cap = cv2.VideoCapture(ip_camera_url)
    #调节摄像头分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    #设置FPS
    cap.set(cv2.CAP_PROP_FPS, 30)
    return cap

class MainWindow(QMainWindow):

    mWindow_pos_x = 900
    mWindow_pos_y = 400
    cap = cv2.VideoCapture()
    timer = QTimer()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('OpenCV 图片显示')
        self.setGeometry(self.mWindow_pos_x, self.mWindow_pos_y, 800, 500)
        
        # 创建central_widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建 QLabel 控件用于显示图片
        self.video_label = QLabel()
        self.video_label.setGeometry(0, 0, 500, 300)
        # self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 图片居中显示
        
        # 创建垂直主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        # 放置视频
        main_layout.addWidget(self.video_label)

        # 创建水平布局，用于放置按键
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        # 配置开始按钮
        self.start_button = QPushButton('start')
        self.start_button.clicked.connect(self.start_video)
        button_layout.addWidget(self.start_button)

        # 配置停止按钮
        self.stop_button = QPushButton('stop')
        self.stop_button.clicked.connect(self.stop_video)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        self.button3 = QPushButton('捕获人脸')
        self.button3.clicked.connect(self.face_capture)
        button_layout.addWidget(self.button3)

        self.button4 = QPushButton('导入人脸')
        self.button4.clicked.connect(self.file_upoload)
        button_layout.addWidget(self.button4)

        self.timer.timeout.connect(self.update_frame)
        

    def start_video(self):
        if not self.cap.isOpened():
            self.cap = start_cpature()
        self.timer.start(50) 
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_video(self):
        self.timer.stop()
        self.cap.release()
        self.video_label.clear()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = face_handl.face_handle(frame)
        # 加载并显示图片
        # OpenCV 图片转换为 QImage
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        # 将 QImage 转换为 QPixmap 显示在 QLabel 上
        q_frame = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        # 调整图像大小
        q_frame = q_frame.scaled(self.video_label.width(), self.video_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
        q_frame = QPixmap.fromImage(q_frame)
        self.video_label.setPixmap(q_frame)
    
    # 捕获人脸
    def face_capture(self):
        pass

    # 人脸上传
    def file_upoload(self):
        qpoint = QPoint(self.mWindow_pos_x, self.mWindow_pos_y)
        file_window = fileUpLoad.FileUpload()
        file_window_center = self.rect().center() - file_window.rect().center() + qpoint
        file_window.move(file_window_center)
        file_window.exec()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()