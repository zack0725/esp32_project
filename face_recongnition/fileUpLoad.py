import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class FileUpload(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('文件上传工具')
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.label = QLabel('未选择文件')
        self.layout.addWidget(self.label)

        self.select_button = QPushButton('选择文件')
        self.select_button.clicked.connect(self.select_file)
        self.layout.addWidget(self.select_button)

        self.upload_button = QPushButton('上传文件')
        self.upload_button.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_button)

        self.setLayout(self.layout)

    def select_file(self):
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle('选择文件')
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.file_path = selected_files[0]
                self.label.setText(f'已选择文件：{self.file_path}')

    def upload_file(self):
        try:
            # 这里可以编写上传文件的代码，示例中只打印文件路径
            print(f'上传文件：{self.file_path}')
        except AttributeError:
            print('请先选择文件')
