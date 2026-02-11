# db_manager.py
import sqlite3
from typing import List, Tuple, Any


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self.connect()
    
    def connect(self):
        """连接到数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)
        except Exception as e:
            raise Exception(f"无法连接到数据库: {str(e)}")
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_table_names(self) -> List[str]:
        """获取所有表名"""
        if not self.connection:
            raise Exception("数据库未连接")
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        return [table[0] for table in tables]
    
    def get_table_info(self, table_name: str) -> List[Tuple]:
        """获取表结构信息"""
        if not self.connection:
            raise Exception("数据库未连接")
        
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        return cursor.fetchall()
    
    def get_table_data(self, table_name: str) -> Tuple[List[Tuple], List[str]]:
        """获取表的所有数据"""
        if not self.connection:
            raise Exception("数据库未连接")
        
        # 获取列名
        columns_info = self.get_table_info(table_name)
        columns = [info[1] for info in columns_info]  # 列名在第二个位置
        
        # 获取数据
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name};")
        data = cursor.fetchall()
        
        return data, columns
    
    def execute_query(self, query: str) -> Tuple[List[Tuple], List[str]]:
        """执行自定义查询"""
        if not self.connection:
            raise Exception("数据库未连接")
        
        cursor = self.connection.cursor()
        cursor.execute(query)
        
        # 获取列名
        columns = [description[0] for description in cursor.description] if cursor.description else []
        
        # 获取数据
        data = cursor.fetchall()
        
        return data, columns
    
    def update_cell(self, table_name: str, column_name: str, primary_key_column: str, primary_key_value: Any, new_value: Any):
        """更新单元格值"""
        if not self.connection:
            raise Exception("数据库未连接")
        
        try:
            cursor = self.connection.cursor()
            # 构建更新语句
            query = f"UPDATE {table_name} SET {column_name} = ? WHERE {primary_key_column} = ?"
            cursor.execute(query, (new_value, primary_key_value))
            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"更新失败: {str(e)}")
    
    def insert_row(self, table_name: str, column_values: dict):
        """插入新行"""
        if not self.connection:
            raise Exception("数据库未连接")
        
        try:
            cursor = self.connection.cursor()
            # 构建插入语句
            columns = ', '.join(column_values.keys())
            placeholders = ', '.join(['?' for _ in column_values])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(column_values.values()))
            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"插入失败: {str(e)}")
    
    def delete_row(self, table_name: str, primary_key_column: str, primary_key_value: Any):
        """删除行"""
        if not self.connection:
            raise Exception("数据库未连接")
        
        try:
            cursor = self.connection.cursor()
            # 构建删除语句
            query = f"DELETE FROM {table_name} WHERE {primary_key_column} = ?"
            cursor.execute(query, (primary_key_value,))
            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"删除失败: {str(e)}")
    
    def get_primary_key_column(self, table_name: str) -> str:
        """获取表的主键列名"""
        if not self.connection:
            raise Exception("数据库未连接")
        
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()
        
        # 寻找主键列
        for col_info in columns_info:
            if col_info[5] == 1:  # 主键标志
                return col_info[1]  # 列名在索引1位置
        
        # 如果没有显式主键，返回第一列
        if columns_info:
            return columns_info[0][1]
        
        return None