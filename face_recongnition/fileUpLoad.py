import sys
from PyQt6.QtWidgets import QApplication, QWidget, QDialog, QPushButton, QVBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import faceUpload

class FileUpload(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('文件上传工具')
        self.setGeometry(100, 100, 300, 150)

        self.layout = QVBoxLayout()

        self.image_label = QLabel()
        self.layout.addWidget(self.image_label)

        self.file_label = QLabel('未选择文件')
        self.layout.addWidget(self.file_label)

        self.tip_label = QLabel('')
        self.layout.addWidget(self.tip_label)

        self.select_button = QPushButton('选择文件')
        self.select_button.clicked.connect(self.select_file)
        self.layout.addWidget(self.select_button)

        self.upload_button = QPushButton('人脸录入')
        self.upload_button.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_button)

        self.setLayout(self.layout)

    def select_file(self):
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle('选择文件')
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.file_path = selected_files[0]
                self.file_label.setText(f'已选择文件：{self.file_path}')

    def upload_file(self):
        try:
            # self.close()
            # qpoint = QPoint(self.mWindow_pos_x, self.mWindow_pos_y)
            face_window = face_window.FileUpload(self.file_path)
            face_window_center = self.rect().center() - face_window.rect().center() 
            face_window.move(face_window_center)
            face_window.exec()
        except AttributeError:
            print('请先选择文件')
