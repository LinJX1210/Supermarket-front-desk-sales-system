# -*- coding: utf-8 -*-
"""
系统配置文件
"""

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '121024',
    'database': 'supermarket_db',
    'charset': 'utf8mb4'
}

# 系统配置
SYSTEM_CONFIG = {
    'app_name': '超市前台销售系统',
    'version': '1.0.0',
    'return_limit_days': 7,  # 退货期限（天）
    'points_rate': 1,  # 积分比例：1元=1积分
}
