import os, sys, cv2, requests
import numpy as np
from PyQt6.QtWidgets import  QApplication, QWidget, QMainWindow, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt, QTimer, QPoint, QThread,  QWaitCondition, QMutex, pyqtSignal, QMutexLocker
from PyQt6.QtGui import QPixmap, QImage, qRgb
from datetime import datetime

import fileUpLoad,faceCongnition,faceUpload

stranger_path = 'person/stranger/'
face_handl = faceCongnition.FaceRecongnition()

def start_cpature():
    # 摄像头的IP地址,http://用户名：密码@IP地址：端口/
    ip_camera_url = 'http://192.168.4.1:81/stream'
    try:
        # 创建一个VideoCapture
        cap = cv2.VideoCapture(ip_camera_url)
        #调节摄像头分辨率
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        #设置FPS
        cap.set(cv2.CAP_PROP_FPS, 30)
    except:
        cap = cv2.VideoCapture()
    return cap

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.cap = cv2.VideoCapture()
        self.is_paused = bool(0)    #标记线程是否暂停
        self.mutex = QMutex()   #互斥锁，用于线程同步
        self.cond = QWaitCondition()    #等待条件，用于线程恢复和暂停

    def pause_thread(self):
        with QMutexLocker(self.mutex):
            self.is_paused = True   #设置线程为暂停状态
            self.cap.release()
    
    def resume_thread(self):
        if self.is_paused:
            with QMutexLocker(self.mutex):
                self.is_paused = False  #设置线程为非暂停状态
                self.cap = start_cpature()
                self.cond.wakeOne() #唤醒一个等待的线程

    def run(self):
        if not self.cap.isOpened():
            self.cap = start_cpature()
        while self._run_flag:
            with QMutexLocker(self.mutex):
                while self.is_paused:
                    self.cond.wait(self.mutex)  # 当线程暂停时，等待条件满足
                ret, frame = self.cap.read()
                if not ret:
                    return
                frame = face_handl.face_handle(frame)
                # OpenCV 图片转换为 QImage
                height, width, channel = frame.shape
                bytes_per_line = channel * width
                # 将 QImage 转换为 QPixmap 显示在 QLabel 上
                q_frame = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                self.change_pixmap_signal.emit(q_frame)

    def stop(self):
        self.cap.release()
        self.terminate() 

class MainWindow(QMainWindow):

    mWindow_pos_x = 900
    mWindow_pos_y = 400

    def __init__(self):
        super().__init__()
        self.thread_running = False  # 标记线程是否正在运行
        self.setup_ui()
        self.setup_thread()
    
    def setup_ui(self):
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
        self.button3.setEnabled(False)
        button_layout.addWidget(self.button3)

        self.button4 = QPushButton('导入人脸')
        self.button4.clicked.connect(self.file_upoload)
        button_layout.addWidget(self.button4)

    def setup_thread(self):
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_frame)
        self.thread_running = True

    def start_video(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.button3.setEnabled(True)
        if self.thread_running:
            self.thread.start()
        if not self.thread_running:
            self.setup_thread()
            self.thread.start()

    def stop_video(self):
        self.video_label.clear()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.button3.setEnabled(False)
        self.thread.stop()
        self.thread_running = False  # 标记线程停止

    def update_frame(self, frame):
        q_frame = QPixmap.fromImage(frame)
        q_frame = q_frame.scaled(self.video_label.width(), self.video_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
        self.video_label.setPixmap(q_frame)
    
    # 捕获人脸
    def face_capture(self):
        self.thread.pause_thread()
        img_src = 'http://192.168.4.1/capture'
        try:
            response = requests.get(img_src)
        except:
            self.thread.resume_thread()
            return
        out_path = stranger_path + datetime.now().strftime("%Y%m%d%H%M%S") + '.jpg'
        with open(out_path,'wb') as file_obj:
            file_obj.write(response.content)
        face_window = faceUpload.FaceUpload(out_path)
        face_window_center = self.rect().center() - face_window.rect().center() 
        face_window.move(face_window_center)
        face_window.exec()
        if os.path.exists(out_path):
            os.remove(out_path)
        self.thread.resume_thread()
            
    # 人脸上传
    def file_upoload(self):
        qpoint = QPoint(self.mWindow_pos_x, self.mWindow_pos_y)
        file_window = fileUpLoad.FileUpload()
        file_window_center = self.rect().center() - file_window.rect().center() + qpoint
        file_window.move(file_window_center)
        file_window.exec()

    def closeEvent(self, event):
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()