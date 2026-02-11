# main_window.py
import sqlite3
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QFileDialog, QMessageBox, QComboBox, QLabel, 
                             QSplitter, QHeaderView, QAbstractItemView, QApplication,
                             QMenuBar, QMenu, QAction, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from db_manager import DatabaseManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = None
        self.current_table = None
        self.primary_key_column = None
        self.load_stylesheet()
        self.init_ui()
    
    def load_stylesheet(self):
        """加载样式表"""
        import sys
        # 获取正确的资源文件路径
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        style_file = os.path.join(base_path, 'style.qss')
        if os.path.exists(style_file):
            with open(style_file, 'r', encoding='utf-8') as f:
                style = f.read()
                QApplication.instance().setStyleSheet(style)
    
    def init_ui(self):
        # 设置窗口图标
        import sys
        # 获取正确的资源文件路径
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setWindowTitle("SQLite3 Database Viewer")
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建工具栏
        toolbar_layout = QHBoxLayout()
        
        # 数据库连接按钮
        self.connect_btn = QPushButton("连接数据库")
        self.connect_btn.clicked.connect(self.connect_database)
        
        # 表选择下拉框
        self.table_combo = QComboBox()
        self.table_combo.currentTextChanged.connect(self.load_table_data)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_tables)
        
        # 编辑按钮
        self.edit_btn = QPushButton("编辑模式")
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        self.edit_btn.setStyleSheet("QPushButton { background-color: #27ae60; }")
        
        # 保存按钮
        self.save_btn = QPushButton("保存更改")
        self.save_btn.clicked.connect(self.save_changes)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("QPushButton { background-color: #2980b9; }")
        
        # 添加到工具栏
        toolbar_layout.addWidget(QLabel("数据库:"))
        toolbar_layout.addWidget(self.connect_btn)
        toolbar_layout.addWidget(QLabel("表:"))
        toolbar_layout.addWidget(self.table_combo)
        toolbar_layout.addWidget(self.refresh_btn)
        toolbar_layout.addWidget(self.edit_btn)
        toolbar_layout.addWidget(self.save_btn)
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)
        
        # 创建表格显示区域
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 默认不可编辑
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 连接表格的单元格更改事件
        self.table_widget.cellChanged.connect(self.on_cell_changed)
        
        main_layout.addWidget(self.table_widget)
        
        # 初始化状态栏
        self.statusBar().showMessage("就绪")
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        open_action = QAction('打开数据库', self)
        open_action.triggered.connect(self.connect_database)
        file_menu.addAction(open_action)
        
        refresh_action = QAction('刷新', self)
        refresh_action.triggered.connect(self.refresh_tables)
        file_menu.addAction(refresh_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')
        
        edit_action = QAction('切换编辑模式', self)
        edit_action.triggered.connect(self.toggle_edit_mode)
        edit_menu.addAction(edit_action)
        
        save_action = QAction('保存更改', self)
        save_action.triggered.connect(self.save_changes)
        edit_menu.addAction(save_action)
        
        # 添加分隔符
        edit_menu.addSeparator()
        
        add_row_action = QAction('添加行', self)
        add_row_action.triggered.connect(self.add_row)
        edit_menu.addAction(add_row_action)
        
        delete_row_action = QAction('删除行', self)
        delete_row_action.triggered.connect(self.delete_row)
        edit_menu.addAction(delete_row_action)
    
    def toggle_edit_mode(self):
        """切换编辑模式"""
        if self.table_widget.editTriggers() == QAbstractItemView.NoEditTriggers:
            # 启用编辑模式
            self.table_widget.setEditTriggers(QAbstractItemView.DoubleClicked | 
                                              QAbstractItemView.EditKeyPressed)
            self.edit_btn.setText("只读模式")
            self.edit_btn.setStyleSheet("QPushButton { background-color: #e74c3c; }")
            self.statusBar().showMessage("已切换到编辑模式")
        else:
            # 禁用编辑模式
            self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.edit_btn.setText("编辑模式")
            self.edit_btn.setStyleSheet("QPushButton { background-color: #27ae60; }")
            self.statusBar().showMessage("已切换到只读模式")
    
    def on_cell_changed(self, row, column):
        """处理单元格更改"""
        if self.db_manager and self.current_table and self.primary_key_column:
            # 启用保存按钮
            self.save_btn.setEnabled(True)
            
            # 获取更改的值和主键值
            new_value = self.table_widget.item(row, column).text()
            column_name = self.table_widget.horizontalHeaderItem(column).text()
            
            # 获取主键值（假设主键在第一列）
            primary_key_value = self.table_widget.item(row, 0).text()
            
            # 保存到临时字典中，稍后统一提交
            if not hasattr(self, 'pending_changes'):
                self.pending_changes = []
            
            self.pending_changes.append({
                'row': row,
                'column': column,
                'column_name': column_name,
                'new_value': new_value,
                'primary_key_value': primary_key_value
            })
    
    def save_changes(self):
        """保存更改到数据库"""
        if not self.db_manager or not self.current_table or not self.primary_key_column:
            QMessageBox.warning(self, "警告", "请先连接数据库并选择表")
            return
        
        if not hasattr(self, 'pending_changes') or not self.pending_changes:
            QMessageBox.information(self, "提示", "没有待保存的更改")
            return
        
        try:
            # 提交所有更改
            for change in self.pending_changes:
                self.db_manager.update_cell(
                    self.current_table,
                    change['column_name'],
                    self.primary_key_column,
                    change['primary_key_value'],
                    change['new_value']
                )
            
            # 清空待处理更改
            self.pending_changes = []
            self.save_btn.setEnabled(False)
            
            # 刷新表格数据
            self.load_table_data(self.current_table)
            
            QMessageBox.information(self, "成功", "更改已保存到数据库")
            self.statusBar().showMessage("更改已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存更改失败: {str(e)}")
    
    def add_row(self):
        """添加新行"""
        if not self.db_manager or not self.current_table:
            QMessageBox.warning(self, "警告", "请先连接数据库并选择表")
            return
        
        try:
            # 获取表结构
            columns_info = self.db_manager.get_table_info(self.current_table)
            column_names = [info[1] for info in columns_info]
            
            # 创建输入对话框
            dialog_result = {}
            for col_name in column_names:
                if col_name != self.primary_key_column:  # 跳过主键列（如果是自增的）
                    value, ok = QInputDialog.getText(self, "添加行", f"输入 {col_name} 的值:")
                    if ok:
                        dialog_result[col_name] = value
                    else:
                        return  # 用户取消操作
            
            # 插入新行
            self.db_manager.insert_row(self.current_table, dialog_result)
            
            # 刷新表格数据
            self.load_table_data(self.current_table)
            
            QMessageBox.information(self, "成功", "新行已添加")
            self.statusBar().showMessage("新行已添加")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加行失败: {str(e)}")
    
    def delete_row(self):
        """删除选中的行"""
        if not self.db_manager or not self.current_table or not self.primary_key_column:
            QMessageBox.warning(self, "警告", "请先连接数据库并选择表")
            return
        
        # 获取选中的行
        selected_rows = set()
        for item in self.table_widget.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要删除的行")
            return
        
        # 确认删除
        reply = QMessageBox.question(self, "确认", f"确定要删除 {len(selected_rows)} 行数据吗？", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        
        try:
            # 删除选中的行
            for row in selected_rows:
                primary_key_value = self.table_widget.item(row, 0).text()  # 假设主键在第一列
                self.db_manager.delete_row(self.current_table, self.primary_key_column, primary_key_value)
            
            # 刷新表格数据
            self.load_table_data(self.current_table)
            
            QMessageBox.information(self, "成功", "行已删除")
            self.statusBar().showMessage("行已删除")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除行失败: {str(e)}")
    
    def connect_database(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择SQLite数据库文件", "", "SQLite数据库文件 (*.db *.sqlite *.sqlite3)"
        )
        
        if file_path:
            try:
                self.db_manager = DatabaseManager(file_path)
                self.refresh_tables()
                self.statusBar().showMessage(f"已连接到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法连接到数据库: {str(e)}")
    
    def refresh_tables(self):
        if self.db_manager:
            try:
                tables = self.db_manager.get_table_names()
                self.table_combo.clear()
                self.table_combo.addItems(tables)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法获取表列表: {str(e)}")
    
    def load_table_data(self, table_name):
        if self.db_manager and table_name:
            try:
                # 获取表数据
                data, columns = self.db_manager.get_table_data(table_name)
                
                # 获取主键列
                self.primary_key_column = self.db_manager.get_primary_key_column(table_name)
                
                # 保存当前表名
                self.current_table = table_name
                
                # 清空待处理更改
                if hasattr(self, 'pending_changes'):
                    delattr(self, 'pending_changes')
                self.save_btn.setEnabled(False)
                
                self.display_table_data(data, columns)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法加载表数据: {str(e)}")
    
    def display_table_data(self, data, columns):
        if not data or not columns:
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            return
        
        # 设置表格行列数
        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(columns))
        
        # 设置列标题
        self.table_widget.setHorizontalHeaderLabels(columns)
        
        # 填充数据
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data) if cell_data is not None else "")
                self.table_widget.setItem(row_idx, col_idx, item)