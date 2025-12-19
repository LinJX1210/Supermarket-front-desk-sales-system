# -*- coding: utf-8 -*-
"""
数据库连接与基础CRUD操作
"""

import pymysql
from config import DB_CONFIG


class DBConnection:
    """数据库连接类"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """建立数据库连接"""
        self.conn = pymysql.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        return self
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def execute(self, sql, params=None):
        """执行SQL语句"""
        self.cursor.execute(sql, params)
        return self.cursor
    
    def commit(self):
        """提交事务"""
        self.conn.commit()
    
    def rollback(self):
        """回滚事务"""
        self.conn.rollback()
    
    def fetchone(self):
        """获取单条记录"""
        return self.cursor.fetchone()
    
    def fetchall(self):
        """获取所有记录"""
        return self.cursor.fetchall()
    
    def __enter__(self):
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
