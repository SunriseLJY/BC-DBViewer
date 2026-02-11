# config.py
import os


class Config:
    # 应用程序设置
    APP_NAME = "SQLite3 Database Viewer"
    APP_VERSION = "1.0.0"
    
    # 默认设置
    DEFAULT_WINDOW_WIDTH = 1000
    DEFAULT_WINDOW_HEIGHT = 700
    
    # 文件过滤器
    SQLITE_FILE_FILTER = "SQLite数据库文件 (*.db *.sqlite *.sqlite3)"
    
    # 最大显示行数（防止大表导致界面卡顿）
    MAX_DISPLAY_ROWS = 10000
