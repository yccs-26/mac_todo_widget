import sys
import os

# 프로젝트 루트(mac_todo_widget/)에서 실행되는 경우,
# Python은 스크립트 위치(src/)를 sys.path에 추가하므로
# 'from db.database import ...', 'from ui.main_window import ...' 등이
# 그대로 동작합니다.
# 만약 다른 위치에서 실행하는 경우를 대비해 src/를 명시적으로 경로에 추가합니다.
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
