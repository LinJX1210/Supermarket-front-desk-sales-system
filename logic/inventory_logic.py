# -*- coding: utf-8 -*-
"""
库存管理逻辑 - 组员2负责
"""

from datetime import datetime
from db.db_conn import DBConnection


class InventoryLogic:
    """库存管理业务逻辑"""
    
    STATUS_MAP = {
        "充足": "sufficient",
        "预警": "warning",
        "缺货": "shortage",
    }
    
    STATUS_DISPLAY = {v: k for k, v in STATUS_MAP.items()}
    
    def get_stock(self, goods_id):
        """
        查询库存
        :param goods_id: 商品ID
        :return: {"success": bool, "data": dict, "message": str}
        """
        with DBConnection() as db:
            sql = """
                SELECT i.*, g.goods_name, g.barcode
                FROM inventory i
                JOIN goods g ON i.goods_id = g.goods_id
                WHERE i.goods_id = %s
            """
            db.execute(sql, (goods_id,))
            inv = db.fetchone()
            
            if inv:
                inv['status_display'] = self.STATUS_DISPLAY.get(inv['stock_status'], inv['stock_status'])
                return {"success": True, "data": inv, "message": "获取成功"}
            return {"success": False, "data": None, "message": "库存记录不存在"}
    
    def reduce_stock(self, goods_id, num):
        """
        扣减库存（销售时调用）
        :param goods_id: 商品ID
        :param num: 扣减数量
        :return: {"success": bool, "data": dict, "message": str}
        """
        if num <= 0:
            return {"success": False, "data": None, "message": "扣减数量必须大于0"}
        
        with DBConnection() as db:
            try:
                db.execute("SELECT stock_num, stock_warning FROM inventory WHERE goods_id = %s FOR UPDATE", 
                          (goods_id,))
                inv = db.fetchone()
                
                if not inv:
                    return {"success": False, "data": None, "message": "库存记录不存在"}
                
                if inv['stock_num'] < num:
                    return {"success": False, "data": None, "message": f"库存不足，当前库存: {inv['stock_num']}"}
                
                new_stock = inv['stock_num'] - num
                
                # 更新库存状态
                if new_stock <= 0:
                    new_status = 'shortage'
                elif new_stock <= inv['stock_warning']:
                    new_status = 'warning'
                else:
                    new_status = 'sufficient'
                
                sql = """
                    UPDATE inventory 
                    SET stock_num = %s, stock_status = %s, update_time = NOW()
                    WHERE goods_id = %s
                """
                db.execute(sql, (new_stock, new_status, goods_id))
                db.commit()
                
                return {
                    "success": True, 
                    "data": {"old_stock": inv['stock_num'], "new_stock": new_stock, "status": new_status},
                    "message": f"库存已扣减，剩余: {new_stock}"
                }
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"扣减失败: {str(e)}"}

    def restore_stock(self, goods_id, num):
        """
        恢复库存（退货时调用）
        :param goods_id: 商品ID
        :param num: 恢复数量
        :return: {"success": bool, "data": dict, "message": str}
        """
        if num <= 0:
            return {"success": False, "data": None, "message": "恢复数量必须大于0"}
        
        with DBConnection() as db:
            try:
                db.execute("SELECT stock_num, stock_warning FROM inventory WHERE goods_id = %s", (goods_id,))
                inv = db.fetchone()
                
                if not inv:
                    return {"success": False, "data": None, "message": "库存记录不存在"}
                
                new_stock = inv['stock_num'] + num
                
                # 更新库存状态
                if new_stock <= 0:
                    new_status = 'shortage'
                elif new_stock <= inv['stock_warning']:
                    new_status = 'warning'
                else:
                    new_status = 'sufficient'
                
                sql = """
                    UPDATE inventory 
                    SET stock_num = %s, stock_status = %s, update_time = NOW()
                    WHERE goods_id = %s
                """
                db.execute(sql, (new_stock, new_status, goods_id))
                db.commit()
                
                return {
                    "success": True, 
                    "data": {"old_stock": inv['stock_num'], "new_stock": new_stock, "status": new_status},
                    "message": f"库存已恢复，当前: {new_stock}"
                }
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"恢复失败: {str(e)}"}
    
    def set_warning_value(self, goods_id, stock_warning, shelf_warning=None):
        """
        设置警戒值
        :param goods_id: 商品ID
        :param stock_warning: 库存预警值
        :param shelf_warning: 货架预警值
        :return: {"success": bool, "data": None, "message": str}
        """
        with DBConnection() as db:
            try:
                db.execute("SELECT inventory_id FROM inventory WHERE goods_id = %s", (goods_id,))
                if not db.fetchone():
                    return {"success": False, "data": None, "message": "库存记录不存在"}
                
                if shelf_warning:
                    sql = """
                        UPDATE inventory 
                        SET stock_warning = %s, shelf_warning = %s, update_time = NOW()
                        WHERE goods_id = %s
                    """
                    db.execute(sql, (stock_warning, shelf_warning, goods_id))
                else:
                    sql = """
                        UPDATE inventory 
                        SET stock_warning = %s, update_time = NOW()
                        WHERE goods_id = %s
                    """
                    db.execute(sql, (stock_warning, goods_id))
                
                db.commit()
                return {"success": True, "data": None, "message": "预警值设置成功"}
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"设置失败: {str(e)}"}
    
    def check_stock_status(self, goods_id):
        """
        检查库存状态
        :param goods_id: 商品ID
        :return: {"success": bool, "data": dict, "message": str}
        """
        with DBConnection() as db:
            sql = """
                SELECT i.stock_num, i.stock_warning, i.shelf_warning, i.stock_status,
                       g.goods_name, g.barcode
                FROM inventory i
                JOIN goods g ON i.goods_id = g.goods_id
                WHERE i.goods_id = %s
            """
            db.execute(sql, (goods_id,))
            inv = db.fetchone()
            
            if not inv:
                return {"success": False, "data": None, "message": "库存记录不存在"}
            
            status_info = {
                "goods_name": inv['goods_name'],
                "barcode": inv['barcode'],
                "stock_num": inv['stock_num'],
                "stock_warning": inv['stock_warning'],
                "stock_status": inv['stock_status'],
                "status_display": self.STATUS_DISPLAY.get(inv['stock_status'], inv['stock_status']),
                "is_warning": inv['stock_num'] <= inv['stock_warning'],
                "is_shortage": inv['stock_num'] <= 0
            }
            
            return {"success": True, "data": status_info, "message": "获取成功"}
    
    def get_warning_list(self):
        """
        获取库存预警列表
        :return: {"success": bool, "data": list, "message": str}
        """
        with DBConnection() as db:
            try:
                sql = """
                    SELECT i.goods_id, i.stock_num, i.stock_warning, i.stock_status,
                           g.goods_name, g.barcode, gc.category_name
                    FROM inventory i
                    JOIN goods g ON i.goods_id = g.goods_id
                    LEFT JOIN goods_category gc ON g.category_id = gc.category_id
                    WHERE i.stock_status IN ('warning', 'shortage')
                    ORDER BY i.stock_num ASC
                """
                db.execute(sql)
                items = db.fetchall()
                
                for item in items:
                    item['status_display'] = self.STATUS_DISPLAY.get(item['stock_status'], item['stock_status'])
                
                return {"success": True, "data": items, "message": f"共{len(items)}条预警记录"}
            except Exception as e:
                return {"success": False, "data": [], "message": f"查询失败: {str(e)}"}
    
    def add_stock(self, goods_id, num, batch_no=None):
        """
        入库（进货时调用）
        :param goods_id: 商品ID
        :param num: 入库数量
        :param batch_no: 批次号
        :return: {"success": bool, "data": dict, "message": str}
        """
        if num <= 0:
            return {"success": False, "data": None, "message": "入库数量必须大于0"}
        
        with DBConnection() as db:
            try:
                db.execute("SELECT stock_num, stock_warning FROM inventory WHERE goods_id = %s", (goods_id,))
                inv = db.fetchone()
                
                if not inv:
                    return {"success": False, "data": None, "message": "库存记录不存在"}
                
                new_stock = inv['stock_num'] + num
                
                # 更新库存状态
                if new_stock <= 0:
                    new_status = 'shortage'
                elif new_stock <= inv['stock_warning']:
                    new_status = 'warning'
                else:
                    new_status = 'sufficient'
                
                sql = """
                    UPDATE inventory 
                    SET stock_num = %s, stock_status = %s, update_time = NOW()
                    WHERE goods_id = %s
                """
                db.execute(sql, (new_stock, new_status, goods_id))
                db.commit()
                
                return {
                    "success": True, 
                    "data": {"old_stock": inv['stock_num'], "new_stock": new_stock},
                    "message": f"入库成功，当前库存: {new_stock}"
                }
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"入库失败: {str(e)}"}
    
    def get_all_inventory(self):
        """获取所有库存"""
        with DBConnection() as db:
            sql = """
                SELECT i.*, g.goods_name, g.barcode
                FROM inventory i
                JOIN goods g ON i.goods_id = g.goods_id
                ORDER BY i.goods_id
            """
            db.execute(sql)
            return db.fetchall()
    
    def search_inventory(self, keyword):
        """搜索库存"""
        with DBConnection() as db:
            sql = """
                SELECT i.*, g.goods_name, g.barcode
                FROM inventory i
                JOIN goods g ON i.goods_id = g.goods_id
                WHERE g.goods_name LIKE %s OR g.barcode LIKE %s
                ORDER BY i.goods_id
            """
            db.execute(sql, (f"%{keyword}%", f"%{keyword}%"))
            return db.fetchall()
    
    def move_to_shelf(self, goods_id, num):
        """从仓库移到货架"""
        if num <= 0:
            return False, "数量必须大于0"
        
        with DBConnection() as db:
            try:
                db.execute("SELECT stock_num, on_shelf_num FROM inventory WHERE goods_id = %s", (goods_id,))
                inv = db.fetchone()
                
                if not inv:
                    return False, "库存记录不存在"
                
                if inv['stock_num'] < num:
                    return False, f"仓库库存不足，当前: {inv['stock_num']}"
                
                sql = """
                    UPDATE inventory 
                    SET stock_num = stock_num - %s, on_shelf_num = on_shelf_num + %s, update_time = NOW()
                    WHERE goods_id = %s
                """
                db.execute(sql, (num, num, goods_id))
                db.commit()
                return True, "上架成功"
            except Exception as e:
                db.rollback()
                return False, f"上架失败: {str(e)}"
    
    def set_stock_warning(self, goods_id, warning_num):
        """设置库存预警线"""
        with DBConnection() as db:
            try:
                sql = "UPDATE inventory SET stock_warning = %s, update_time = NOW() WHERE goods_id = %s"
                db.execute(sql, (warning_num, goods_id))
                db.commit()
                return True, "设置成功"
            except Exception as e:
                db.rollback()
                return False, f"设置失败: {str(e)}"
    
    def set_shelf_warning(self, goods_id, warning_num):
        """设置货架预警线"""
        with DBConnection() as db:
            try:
                sql = "UPDATE inventory SET shelf_warning = %s, update_time = NOW() WHERE goods_id = %s"
                db.execute(sql, (warning_num, goods_id))
                db.commit()
                return True, "设置成功"
            except Exception as e:
                db.rollback()
                return False, f"设置失败: {str(e)}"
