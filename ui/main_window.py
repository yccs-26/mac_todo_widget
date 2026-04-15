from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QFrame, QListWidgetItem, QSizePolicy, QLayout
)
from PyQt6.QtCore import Qt, QPoint

from db.database import db_manager
from core.command_processor import CommandProcessor, ActionType
from ui.todo_list import TodoListWidget
from ui.todo_item import TodoItemWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.drag_pos = QPoint()
        self.is_list_visible = True
        self.is_block_mode = False
        
        self.init_ui()
        self.load_todos()

    def init_ui(self):
        # 다크 모드 기본 상태 설정
        self.is_dark = True
        
        # 1. Frameless 및 투명 배경 설정
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(350, 500)

        # 2. 메인 컨테이너 위젯 (둥근 모서리와 배경색 적용)
        self.central_widget = QFrame()
        self.central_widget.setObjectName("MainFrame")
        self.setCentralWidget(self.central_widget)

        # 전체 레이아웃
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)

        # 3. 헤더 영역
        self.header_layout = QHBoxLayout()
        
        # 목록 보이기/숨기기 토글 아이콘 버튼
        self.toggle_list_btn = QPushButton("▲")
        self.toggle_list_btn.setFixedSize(30, 30)
        self.toggle_list_btn.clicked.connect(self.toggle_list_visibility)
        
        # 버튼을 우측 정렬하여 추가
        self.header_layout.addWidget(self.toggle_list_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        self.main_layout.addLayout(self.header_layout)

        # 4. 리스트 위젯 (Drag & Drop 지원)
        self.list_widget = TodoListWidget()
        self.main_layout.addWidget(self.list_widget)

        # 5. 입력 영역
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.add_todo)
        self.main_layout.addWidget(self.input_field)

        # 초기 상태(최대화) 적용
        self.apply_maximized_mode()

    def load_todos(self):
        """DB에서 활성화된 할 일 목록을 불러와서 UI에 렌더링"""
        self.list_widget.clear()
        todos = db_manager.get_active_todos()
        for todo in todos:
            self.add_todo_item_to_list(todo)

    def add_todo_item_to_list(self, todo_data):
        """단일 Todo 항목을 리스트 위젯에 추가"""
        item_widget = TodoItemWidget(todo_data)
        item_widget.set_theme(self.is_dark)
        
        # 시그널 연결 (진행률 변경, 상태 변경)
        item_widget.progress_changed.connect(self.on_progress_changed)
        item_widget.status_changed.connect(self.on_status_changed)
        
        # ListWidget의 아이템 생성
        list_item = QListWidgetItem(self.list_widget)
        # 아이템 크기를 위젯 크기에 맞춤
        list_item.setSizeHint(item_widget.sizeHint())
        
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, item_widget)
        
        # 커스텀 데이터를 저장하여 순서 변경 시 id를 식별할 수 있도록 함
        list_item.setData(Qt.ItemDataRole.UserRole, todo_data['id'])

    def add_todo(self):
        """입력 필드에서 텍스트를 받아 CommandProcessor를 통해 명령 분석 및 처리"""
        text = self.input_field.text()
        
        # 비즈니스 로직(파싱/DB저장)을 분리된 Processor로 위임
        result = CommandProcessor.process(text)
        action = result["action"]
        data = result["data"]
        
        if action == ActionType.EMPTY:
            return
            
        elif action == ActionType.THEME_CHANGE:
            self.set_theme(data["is_dark"])
            self.input_field.clear()
            
        elif action == ActionType.BLOCK_MODE:
            self.enable_block_mode()
            self.input_field.clear()
            
        elif action == ActionType.EXIT:
            self.close()
            
        elif action == ActionType.ADD_TODO:
            self.add_todo_item_to_list(data)
            self.input_field.clear()
            
        elif action == ActionType.INVALID:
            # 유효하지 않은 입력인 경우 처리 (분리)
            pass

    def enable_block_mode(self):
        """블록 모드 (Drag Grip Mode) 진입"""
        self.is_block_mode = True
        self.input_field.setPlaceholderText("[블록 모드] 창 이동 가능 (더블 클릭하여 해제)")
        self.input_field.setReadOnly(True)
        self.input_field.clearFocus()
        
        # 핵심 원리: QLineEdit가 마우스 이벤트를 가로채고 독점하는 것을 방지하기 위해 
        # WA_TransparentForMouseEvents 속성을 켭니다.
        # 이렇게 되면 QLineEdit는 마우스 클릭/이동/더블클릭 이벤트를 모두 무시하고, 
        # 이벤트가 부모(MainWindow) 위젯으로 그대로 통과하게 됩니다. 
        # 결과적으로 입력창 어디를 잡아도 부모의 mouseMoveEvent가 동작하여 원활한 창 드래그가 발생합니다.
        self.input_field.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def disable_block_mode(self):
        """블록 모드 해제"""
        self.is_block_mode = False
        self.input_field.setReadOnly(False)
        # 이벤트를 부모로 넘기던 속성을 다시 꺼주어 정상적인 텍스트 입력을 가능하게 복구합니다.
        self.input_field.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.input_field.setFocus()

    def on_progress_changed(self, todo_id, percent):
        """프로그레스 텍스트 박스에서 드래그로 진행률이 변경되었을 때 호출"""
        db_manager.update_progress(todo_id, percent)

    def on_status_changed(self, todo_id, new_status):
        """체크박스 클릭(COMPLETED) 또는 삭제 버튼(DELETED) 클릭 시 호출"""
        db_manager.update_status(todo_id, new_status)
        # UI에서 항목 제거 및 순서 재배치
        self.remove_item_by_id(todo_id)
        self.update_all_orders()

    def remove_item_by_id(self, todo_id):
        """특정 id를 가진 항목을 리스트 위젯에서 삭제"""
        for count in range(self.list_widget.count()):
            item = self.list_widget.item(count)
            if item.data(Qt.ItemDataRole.UserRole) == todo_id:
                self.list_widget.takeItem(count)
                break

    def update_all_orders(self):
        """현재 UI상에 있는 리스트 항목들의 순서를 DB에 업데이트"""
        ordered_ids = []
        for count in range(self.list_widget.count()):
            item = self.list_widget.item(count)
            todo_id = item.data(Qt.ItemDataRole.UserRole)
            ordered_ids.append(todo_id)
            
        if ordered_ids:
            db_manager.update_orders(ordered_ids)

    def set_theme(self, is_dark):
        """전체 앱 테마 전파"""
        self.is_dark = is_dark
        
        # 현재 화면 상태(최대화/최소화)에 맞춰 프레임 및 버튼 색상 즉각 갱신
        if getattr(self, 'is_list_visible', None) is not None:
            if self.is_list_visible:
                self.apply_maximized_mode()
            else:
                self.apply_minimized_mode()
                
        # 등록되어 있는 모든 아이템에 테마 전파
        for count in range(self.list_widget.count()):
            item = self.list_widget.item(count)
            widget = self.list_widget.itemWidget(item)
            if widget:
                widget.set_theme(is_dark)

    def toggle_list_visibility(self):
        """리스트 및 입력 영역 숨기기/보이기 토글"""
        self.is_list_visible = not self.is_list_visible
        self.list_widget.setVisible(self.is_list_visible)
        
        if self.is_list_visible:
            self.apply_maximized_mode()
        else:
            self.apply_minimized_mode()

    def apply_maximized_mode(self):
        """최대화(기본) 모드 UI 설정"""
        self.toggle_list_btn.setText("▲")
        
        # 가로 사이즈 350 고정 및 높이 제약 초기화
        self.main_layout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.setFixedWidth(350)
        self.setMinimumHeight(400)
        self.setMaximumHeight(16777215)
        
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        bg_color = "rgba(30, 30, 30, 230)" if self.is_dark else "rgba(240, 240, 240, 230)"
        text_color = "white" if self.is_dark else "black"
        input_bg = "rgba(255, 255, 255, 0.1)" if self.is_dark else "rgba(0, 0, 0, 0.1)"
        input_hover = "rgba(255, 255, 255, 0.2)" if self.is_dark else "rgba(0, 0, 0, 0.2)"
        
        self.central_widget.setStyleSheet(f"""
            #MainFrame {{
                background-color: {bg_color};
                border-radius: 15px;
            }}
        """)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {input_bg};
                color: {text_color};
                border: 1px solid #555;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }}
            QLineEdit:focus {{ border: 1px solid #3A7CA5; }}
        """)
        
        # [수정] 아이콘 버튼을 텍스트 박스와 똑같은 배경색 및 라운드로 맞춤
        self.toggle_list_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {input_bg};
                color: {text_color};
                font-size: 16px;
                font-weight: bold;
                border: 1px solid transparent;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {input_hover};
            }}
        """)
        
        # 레이아웃 재배치 및 창 크기 복구
        self.main_layout.addWidget(self.input_field)
        self.resize(350, 500)

    def apply_minimized_mode(self):
        """극단적 최소화 모드 UI 설정"""
        self.toggle_list_btn.setText("▼")
        
        # [수정] 최소화 시 가로 길이 350으로 유지
        self.setFixedWidth(350)
        self.main_layout.setContentsMargins(5, 0, 5, 0) 
        
        bg_color = "rgba(45, 45, 45, 180)" if self.is_dark else "rgba(255, 255, 255, 180)"
        text_color = "white" if self.is_dark else "black"
        
        self.central_widget.setStyleSheet(f"""
            #MainFrame {{
                background-color: {bg_color};
                border-radius: 4px;
            }}
        """)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                color: {text_color};
                border: none;
                padding: 2px 0px;
                font-size: 13px;
            }}
        """)
        self.toggle_list_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {text_color};
                font-size: 16px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                color: #888888;
            }}
        """)
        
        # 레이아웃 재배치 및 스냅
        self.header_layout.insertWidget(0, self.input_field)
        self.main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.resize(350, 0)

    # --- Mouse Events for dragging Frameless Window ---
    def mousePressEvent(self, event):
        # 마우스 왼쪽 버튼 클릭 시 빈 공간(배경) 클릭인지 확인
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            # 창 이동
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
            
    def mouseDoubleClickEvent(self, event):
        # 블록 모드였을 때, 텍스트 상자 더블클릭 이벤트가 부모(여기)로 전달되면 모드를 다시 해제.
        if event.button() == Qt.MouseButton.LeftButton and self.is_block_mode:
            self.disable_block_mode()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)
