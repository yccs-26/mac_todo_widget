import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo_data.db")

class DatabaseManager:
    def __init__(self):
        self.init_db()

    def _get_connection(self):
        return sqlite3.connect(DB_PATH)

    def init_db(self):
        """데이터베이스 및 테이블 초기화"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    raw_text TEXT NOT NULL,
                    progress_percent INTEGER DEFAULT 0,
                    display_order INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'ACTIVE',
                    created_at DATETIME,
                    checked_at DATETIME,
                    updated_at DATETIME
                )
            ''')
            conn.commit()

    def get_active_todos(self):
        """활성화된(ACTIVE) Todo 목록을 display_order 순서로 가져옴"""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM todos 
                WHERE status = 'ACTIVE' 
                ORDER BY display_order ASC, id ASC
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def add_todo(self, text):
        """새로운 Todo 항목 추가"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 현재 가장 큰 display_order 값 가져오기
            cursor.execute('SELECT MAX(display_order) FROM todos WHERE status = "ACTIVE"')
            result = cursor.fetchone()
            max_order = result[0] if result and result[0] is not None else -1
            new_order = max_order + 1

            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO todos (raw_text, progress_percent, display_order, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (text, 0, new_order, 'ACTIVE', now, now))
            conn.commit()
            return cursor.lastrowid

    def update_progress(self, todo_id, percent):
        """진행률(0~150%) 업데이트"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                UPDATE todos 
                SET progress_percent = ?, updated_at = ?
                WHERE id = ?
            ''', (percent, now, todo_id))
            conn.commit()

    def update_status(self, todo_id, new_status):
        """상태(COMPLETED 또는 DELETED)로 변경하여 소프트 삭제 처리"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if new_status == 'COMPLETED':
                cursor.execute('''
                    UPDATE todos 
                    SET status = ?, updated_at = ?, checked_at = ?
                    WHERE id = ?
                ''', (new_status, now, now, todo_id))
            else:
                cursor.execute('''
                    UPDATE todos 
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                ''', (new_status, now, todo_id))
            conn.commit()

    def update_orders(self, ordered_id_list):
        """Drag & Drop 등으로 변경된 리스트의 순서(display_order)를 일괄 업데이트"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for index, todo_id in enumerate(ordered_id_list):
                cursor.execute('''
                    UPDATE todos 
                    SET display_order = ?, updated_at = ?
                    WHERE id = ?
                ''', (index, now, todo_id))
            conn.commit()

db_manager = DatabaseManager()
