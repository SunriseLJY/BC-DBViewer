# file_utils.py
import os
from typing import Optional


def is_valid_sqlite_file(file_path: str) -> bool:
    """
    检查文件是否为有效的SQLite文件
    """
    if not os.path.isfile(file_path):
        return False
    
    # 检查文件扩展名
    valid_extensions = ['.db', '.sqlite', '.sqlite3']
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in valid_extensions:
        return False
    
    # 尝试读取文件头（SQLite文件头为 "SQLite format 3"）
    try:
        with open(file_path, 'rb') as f:
            header = f.read(16)
            return header.startswith(b'SQLite format 3')
    except:
        return False


def get_file_size_mb(file_path: str) -> Optional[float]:
    """
    获取文件大小（MB）
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    except:
        return None
