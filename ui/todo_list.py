from PyQt6.QtWidgets import QListWidget, QAbstractItemView

class TodoListWidget(QListWidget):
    """Drag & Drop을 지원하고 순서 변경 시 이벤트를 처리하는 커스텀 리스트 위젯"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                background-color: transparent;
                margin-bottom: 2px;
            }
        """)

    def dropEvent(self, event):
        super().dropEvent(event)
        # 드롭 이벤트가 끝난 후 순서 업데이트를 위해 메인 윈도우에 알림
        main_window = self.window()
        if hasattr(main_window, 'update_all_orders'):
            main_window.update_all_orders()
