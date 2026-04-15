from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QCheckBox, QPushButton, QSizePolicy
)
from PyQt6.QtGui import QPainter, QColor, QFont, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QRectF

class ProgressTextBox(QWidget):
    """
    텍스트 박스 자체가 하나의 프로그레스 바 역할을 하는 커스텀 위젯입니다.
    사용자가 이 위젯 내부를 클릭하고 좌우로 드래그하여 0% ~ 150%까지 진행률을 설정할 수 있습니다.
    """
    # 진행률이 변경되었을 때 발생하는 시그널 (todo_id, percent)
    progress_changed = pyqtSignal(int, int)

    def __init__(self, todo_id, text, progress_percent=0, parent=None):
        super().__init__(parent)
        self.todo_id = todo_id
        self.text = text
        self.progress_percent = progress_percent
        
        # UI 업데이트용 변수 (드래그 중 실시간 렌더링에 사용)
        self.current_percent = progress_percent
        
        # 위젯 정책 설정 (텍스트 길이에 관계없이 가로로 최대한 늘어나도록)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        """커스텀 렌더링 (프로그레스 바와 텍스트)"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        width = rect.width()
        height = rect.height()

        is_dark = getattr(self, 'is_dark', True)

        # 1. 배경 그리기
        bg_color = QColor("#2A2A2A") if is_dark else QColor("#E0E0E0")
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 5, 5)

        # 2. 프로그레스 바 그리기 (그라데이션)
        max_percent = 150
        clamped_percent = max(0, min(max_percent, self.current_percent))
        bar_width = (width * clamped_percent) / max_percent
        hundred_x = width * 100 / max_percent  # 100% 위치 (픽셀)

        if bar_width > 0:
            from PyQt6.QtGui import QLinearGradient, QGradient

            if clamped_percent <= 100:
                # 0~100% 내: 파란색 단색
                painter.setBrush(QColor("#3A7CA5"))
                painter.drawRoundedRect(QRectF(0, 0, bar_width, height), 5, 5)
            else:
                # 100% 초과: 0에서 bar_width까지 그라데이션
                # 색상 전환이 100% 지점에서 부드럽게 일어나도록
                # gradient stop 위치: 0=파란, hundred_x/bar_width=전환점, 1.0=연한연두색  
                grad = QLinearGradient(0, 0, bar_width, 0)
                grad.setColorAt(0.0, QColor("#3A7CA5"))          # 시작: 파란
                transition_stop = hundred_x / bar_width
                grad.setColorAt(max(0.0, transition_stop - 0.15), QColor("#3A7CA5"))  # 전환 시작
                grad.setColorAt(transition_stop, QColor("#5BA87F"))                   # 100% 지점: 중간 색상
                grad.setColorAt(min(1.0, transition_stop + 0.20), QColor("#81C784")) # 전환 종료
                grad.setColorAt(1.0, QColor("#81C784"))          # 끝: 연한 초록
                painter.setBrush(grad)
                painter.drawRoundedRect(QRectF(0, 0, bar_width, height), 5, 5)

        # 3. 텍스트 + 퍼센트 표시 (항상 표시)
        text_color = QColor("#FFFFFF") if is_dark else QColor("#000000")
        painter.setPen(text_color)
        painter.setFont(QFont("Arial", 12))
        text_rect = rect.adjusted(10, 0, -10, 0)
        display_text = f"{self.text}  ({clamped_percent}%)"
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, display_text)

    def set_theme(self, is_dark):
        """테마(다크 모드/라이트 모드)를 설정합니다."""
        self.is_dark = is_dark
        self.update()

    # --- Mouse Events for Dragging Progress ---

    def _calculate_percent_from_pos(self, x_pos):
        """
        마우스의 X 좌표를 기반으로 0~150% 사이의 진행률을 계산합니다.
        위젯의 전체 너비가 150%이므로, x / width 비율에 150을 곱합니다.
        """
        width = self.rect().width()
        if width == 0:
            return 0
        
        # 비율 계산
        ratio = x_pos / width
        percent = int(ratio * 150)
        
        # 0 ~ 150 범위로 제한 (클램핑)
        return max(0, min(150, percent))

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # 클릭 시 해당 좌표에 맞게 진행률 업데이트
            new_percent = self._calculate_percent_from_pos(event.pos().x())
            if new_percent != self.current_percent:
                self.current_percent = new_percent
                self.update() # paintEvent 다시 호출 (화면 갱신)
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        # 드래그 중 실시간으로 진행률 업데이트
        new_percent = self._calculate_percent_from_pos(event.pos().x())
        if new_percent != self.current_percent:
            self.current_percent = new_percent
            self.update() # 화면 갱신
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # 드래그가 끝나면 DB에 저장할 수 있도록 시그널을 방출합니다.
            if self.current_percent != self.progress_percent:
                self.progress_percent = self.current_percent
                self.progress_changed.emit(self.todo_id, self.progress_percent)
            event.accept()


class TodoItemWidget(QWidget):
    """
    개별 Todo 항목을 표시하는 컨테이너 위젯.
    좌측 체크박스, 우측 X 버튼, 그리고 중앙에 ProgressTextBox를 포함합니다.
    """
    # 상태 변경 시그널
    status_changed = pyqtSignal(int, str) # (todo_id, "COMPLETED" 또는 "DELETED")
    
    # ProgressTextBox의 시그널을 부모(Main)로 전달하기 위한 시그널
    progress_changed = pyqtSignal(int, int) # (todo_id, percent)

    def __init__(self, todo_data, parent=None):
        super().__init__(parent)
        self.todo_id = todo_data['id']
        self.raw_text = todo_data['raw_text']
        self.progress_percent = todo_data['progress_percent']
        
        self.init_ui()

    def init_ui(self):
        # 레이아웃 마진 0으로 설정하여 깔끔하게 배치
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)

        # 1. 좌측 체크박스
        self.checkbox = QCheckBox()
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.stateChanged.connect(self._on_check)
        
        # 체크박스 스타일 (Mac 스타일을 위해 조금 크게 조정할 수 있음)
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator { width: 18px; height: 18px; }
        """)
        layout.addWidget(self.checkbox)

        # 2. 중앙 프로그레스 텍스트 박스
        self.progress_box = ProgressTextBox(self.todo_id, self.raw_text, self.progress_percent)
        # 자식 위젯의 시그널을 이 위젯의 시그널로 다시 방출(릴레이)
        self.progress_box.progress_changed.connect(self.progress_changed.emit)
        layout.addWidget(self.progress_box)

        # 3. 우측 삭제 버튼
        self.delete_btn = QPushButton("✕")
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.clicked.connect(self._on_delete)
        layout.addWidget(self.delete_btn)

    def _on_check(self, state):
        # 2는 Qt.CheckState.Checked 모델 값입니다. (0은 Unchecked)
        if state == 2: 
            # 체크되면 상태를 COMPLETED로 변경하도록 시그널 방출
            self.status_changed.emit(self.todo_id, "COMPLETED")

    def _on_delete(self):
        # 삭제 버튼 누르면 DELETED 상태로 변경하도록 시그널 방출
        self.status_changed.emit(self.todo_id, "DELETED")

    def set_theme(self, is_dark):
        """테마에 따라 UI 업데이트"""
        self.is_dark = is_dark

        self.progress_box.set_theme(is_dark)

        btn_color = "#888888" if is_dark else "#555555"
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {btn_color};
                border: none;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: #FF5252;
            }}
        """)

        # 체크박스: 다크 모드에서 테두리 없이 영역만 조금 밝게
        if is_dark:
            self.checkbox.setStyleSheet("""
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: none;
                    border-radius: 3px;
                    background-color: #555555;
                }
                QCheckBox::indicator:checked {
                    background-color: #5BB8F5;
                    border: none;
                }
            """)
        else:
            # 라이트 모드: 기본 시스템 스타일 유지
            self.checkbox.setStyleSheet("""
                QCheckBox::indicator { width: 18px; height: 18px; }
            """)
