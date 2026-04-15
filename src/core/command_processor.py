from enum import Enum
from db.database import db_manager

class ActionType(Enum):
    THEME_CHANGE = "THEME_CHANGE"
    BLOCK_MODE = "BLOCK_MODE"
    EXIT = "EXIT"
    ADD_TODO = "ADD_TODO"
    INVALID = "INVALID"
    EMPTY = "EMPTY"

class CommandProcessor:
    @staticmethod
    def process(text: str) -> dict:
        """
        사용자 입력 텍스트를 파싱하여 적절한 액션과 데이터를 반환합니다.
        반환 형식: {"action": ActionType, "data": Any}
        """
        stripped_text = text.strip()
        if not stripped_text:
            return {"action": ActionType.EMPTY, "data": None}

        command_text = stripped_text.lower()
        
        # 1. 테마 변경 명령어
        if command_text == "light mode":
            return {"action": ActionType.THEME_CHANGE, "data": {"is_dark": False}}
        elif command_text == "dark mode":
            return {"action": ActionType.THEME_CHANGE, "data": {"is_dark": True}}
            
        # 2. 블록 모드 명령어
        if command_text == "block":
            return {"action": ActionType.BLOCK_MODE, "data": None}
            
        # 3. 종료 명령어
        if command_text == "exit":
            return {"action": ActionType.EXIT, "data": None}
            
        # 4. 유효성 검사 (할 일 추가 시 ')' 문자가 반드시 포함되어야 함)
        if ")" not in stripped_text:
            return {"action": ActionType.INVALID, "data": None}
            
        # 4. DB에 일반 할 일 기록 로직 위임 처리
        todo_id = db_manager.add_todo(stripped_text)
        todo_data = {
            'id': todo_id,
            'raw_text': stripped_text,
            'progress_percent': 0
        }
        
        return {"action": ActionType.ADD_TODO, "data": todo_data}
