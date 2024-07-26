import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QPushButton, QVBoxLayout

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('提示框示例')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()
        button = QPushButton('显示提示框', self)
        button.clicked.connect(self.showMessageBox)
        layout.addWidget(button)

        self.setLayout(layout)

    def showMessageBox(self):
        msg = QMessageBox()
        msg.setWindowTitle('提示')
        msg.setText('这是一个提示框示例')
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok) 
        msg.exec()
import os
def main():
    file_path = 'example_file.txt'
    extension = os.path.splitext(file_path)
    print(f"The file extension of '{file_path}' is '{extension}'")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()
