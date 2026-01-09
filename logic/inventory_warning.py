# -*- coding: utf-8 -*-
"""库存警戒逻辑"""

from db.db_conn import DBConnection
from logic.notification_logic import NotificationLogic


class InventoryWarning:
    """库存警戒业务逻辑"""
    
    def get_stock_warning_list(self):
        """获取库存预警列表"""
        with DBConnection() as db:
            sql = """
                SELECT i.*, g.goods_name, g.barcode
                FROM inventory i
                JOIN goods g ON i.goods_id = g.goods_id
                WHERE i.stock_num <= i.stock_warning
                ORDER BY i.stock_num ASC
            """
            db.execute(sql)
            return db.fetchall()
    
    def get_shelf_warning_list(self):
        """获取货架预警列表"""
        with DBConnection() as db:
            sql = """
                SELECT i.*, g.goods_name, g.barcode
                FROM inventory i
                JOIN goods g ON i.goods_id = g.goods_id
                WHERE i.on_shelf_num <= i.shelf_warning
                ORDER BY i.on_shelf_num ASC
            """
            db.execute(sql)
            return db.fetchall()
    
    def check_all_inventory(self):
        """检查所有库存状态并更新"""
        # 直接创建库存预警通知，不更新状态字段（避免ENUM值不匹配）
        try:
            self._create_warning_notifications()
            return True, "库存检查完成"
        except Exception as e:
            return False, str(e)
    
    def _create_warning_notifications(self):
        """创建库存预警通知"""
        notification_logic = NotificationLogic()
        
        # 获取缺货商品
        shortage_list = self.get_shortage_goods()
        if shortage_list:
            goods_names = [item['goods_name'] for item in shortage_list[:5]]
            content = f"The following items are out of stock: {', '.join(goods_names)}"
            if len(shortage_list) > 5:
                content += f" and {len(shortage_list) - 5} more"
            notification_logic.create_notification(
                target_user_id=None, target_role="admin",
                notification_type="stock_warning",
                title="Stock Out Warning",
                content=content
            )
        
        # 获取库存预警商品
        stock_warning_list = self.get_stock_warning_list()
        if stock_warning_list:
            warning_only = [item for item in stock_warning_list if item['stock_num'] > 0]
            if warning_only:
                goods_names = [item['goods_name'] for item in warning_only[:5]]
                content = f"Low stock items: {', '.join(goods_names)}"
                if len(warning_only) > 5:
                    content += f" and {len(warning_only) - 5} more"
                notification_logic.create_notification(
                    target_user_id=None, target_role="admin",
                    notification_type="stock_warning",
                    title="Low Stock Warning",
                    content=content
                )
    
    def get_shortage_goods(self):
        """获取缺货商品列表"""
        with DBConnection() as db:
            sql = """
                SELECT i.*, g.goods_name, g.barcode
                FROM inventory i
                JOIN goods g ON i.goods_id = g.goods_id
                WHERE i.stock_num <= 0
                ORDER BY g.goods_name
            """
            db.execute(sql)
            return db.fetchall()
    
    def get_warning_summary(self):
        """获取预警汇总"""
        with DBConnection() as db:
            sql = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN stock_num <= 0 THEN 1 ELSE 0 END) as shortage_count,
                    SUM(CASE WHEN stock_num > 0 AND stock_num <= stock_warning THEN 1 ELSE 0 END) as stock_warning_count,
                    SUM(CASE WHEN on_shelf_num <= shelf_warning THEN 1 ELSE 0 END) as shelf_warning_count
                FROM inventory
            """
            db.execute(sql)
            return db.fetchone()
