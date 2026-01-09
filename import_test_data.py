# -*- coding: utf-8 -*-
"""导入测试数据脚本"""

import pymysql
from config import DB_CONFIG

def import_test_data():
    conn = pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    with open('db/test_data.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 禁用外键检查
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    # 分割SQL语句并执行
    statements = sql_content.split(';')
    for stmt in statements:
        stmt = stmt.strip()
        if stmt and not stmt.startswith('--') and not stmt.startswith('/*'):
            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"跳过: {str(e)[:60]}")
                continue
    
    # 重新启用外键检查
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    
    cursor.close()
    conn.close()
    print("测试数据导入完成！")

if __name__ == "__main__":
    import_test_data()
