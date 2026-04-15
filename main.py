import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 애플리케이션 시작 및 창 띄우기
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
