import os, threading, sys
from concurrent.futures import ThreadPoolExecutor
import cv2
import pickle
import face_recognition
import numpy as np

import sys
from PyQt6.QtCore import (QThread, QWaitCondition, QMutex, pyqtSignal, QMutexLocker)
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QProgressBar, QApplication)


class MyThread(QThread):
    valueChange = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.is_paused = bool(0)  # 标记线程是否暂停
        self.progress_value = int(0)  # 进度值
        self.mutex = QMutex()  # 互斥锁，用于线程同步
        self.cond = QWaitCondition()  # 等待条件，用于线程暂停和恢复

    def pause_thread(self):
        with QMutexLocker(self.mutex):
            self.is_paused = True  # 设置线程为暂停状态

    def resume_thread(self):
        if self.is_paused:
            with QMutexLocker(self.mutex):
                self.is_paused = False  # 设置线程为非暂停状态
                self.cond.wakeOne()  # 唤醒一个等待的线程

    def run(self):
        while True:
            with QMutexLocker(self.mutex):
                while self.is_paused:
                    self.cond.wait(self.mutex)  # 当线程暂停时，等待条件满足
                if self.progress_value >= 100:
                    self.progress_value = 0
                    return  # 当进度值达到 100 时，重置为 0 并退出线程
                self.progress_value += 1
                self.valueChange.emit(self.progress_value)  # 发送进度值变化信号
                self.msleep(30)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.thread_running = False  # 标记线程是否正在运行
        self.setup_ui()
        self.setup_thread()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.progressBar = QProgressBar(self)
        layout.addWidget(self.progressBar)
        layout.addWidget(QPushButton(r'启动', self, clicked=self.start_thread))
        layout.addWidget(QPushButton(r'停止', self, clicked=self.paused_thread))
        layout.addWidget(QPushButton(r'恢复', self, clicked=self.resume_thread))
        layout.addWidget(QPushButton(r'结束', self, clicked=self.stop_thread))
        self.show()

    def setup_thread(self):
        self.thread = MyThread()
        self.thread.valueChange.connect(self.progressBar.setValue)
        self.thread_running = True

    def start_thread(self):
        if self.thread_running:
            self.thread.start()
        if not self.thread_running:
            self.setup_thread()
            self.thread.start()

    def paused_thread(self):
        if not self.thread_running:
            return
        if not self.thread.isRunning():
            self.thread.start()
        else:
            self.thread.pause_thread()

    def resume_thread(self):
        if not self.thread_running:
            return
        self.thread.resume_thread()

    def stop_thread(self):
        self.thread.quit()  # 终止线程的事件循环
        self.thread_running = False  # 标记线程停止
        self.progressBar.setValue(0)  # 重置进度条的值


if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # window = MainWindow()
    # sys.exit(app.exec())
    datapickle_path = 'person/data.pickle'
    with open(datapickle_path, 'rb') as f:
        if (os.path.getsize(datapickle_path) > 0):
            faces = pickle.load(f)
    face_encodings = list(faces.values())
    
    image1 = face_recognition.load_image_file('person/stranger/BB1qN7L6.jpg')

    face_encoding1 = face_recognition.face_encodings(image1)

    if face_encoding1:
        # 对每个人脸进行编码
        for face_encoding in face_encoding1:
            # 比较人脸编码
            matches = face_recognition.compare_faces(face_encodings, face_encoding,0.02)
            print(matches)
            # 如果找到匹配的人脸
            count = 0
            for matche in matches:
                count_true = np.sum(matche)/np.size(matche)
                print("找到匹配的人脸",count_true)
                matches[count] = True
                count += 1

            print(matches)


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
    matches = []
    # 开启人脸比对线程并提交给线程池
    if not self.is_face_start:
        is_face_start = True
        face_compare_future = self.executor.submit(self.face_compare, capture_face_encodings, self.face_encodings, matches)
    elif is_face_start and face_compare_future.done():
        self.is_face_start = False
        matches = face_compare_future.result()
        # 对检测到的人脸进行识别和跟踪
        for (top, right, bottom, left), matche in zip(face_locations, matches):
            if matche:
                # 如果找到匹配的人脸，从映射中获取姓名
                name = 'pass' # self.face_names[matches]
                # 在图像上标注姓名
                frame = cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                frame = cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
            else:
                frame = cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                frame = cv2.putText(frame, 'stanger', (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
    return frame
