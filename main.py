# main.py
import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    # 设置应用样式
    app.setStyle('Fusion')  # 使用Fusion样式以更好地支持自定义样式表
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()