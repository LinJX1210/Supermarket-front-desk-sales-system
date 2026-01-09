# -*- coding: utf-8 -*-
"""
商品管理逻辑 - 组员2负责
"""

from datetime import datetime
from db.db_conn import DBConnection


class GoodsManageLogic:
    """商品管理业务逻辑"""
    
    STATUS_MAP = {
        "在售": "on_shelf",
        "下架": "off_shelf",
        "待质检": "pending_inspect",
    }
    
    STATUS_DISPLAY = {v: k for k, v in STATUS_MAP.items()}
    
    def add_goods(self, goods_data):
        """
        新增商品
        :param goods_data: {
            "barcode": 商品条码,
            "goods_name": 商品名称,
            "category_id": 分类ID,
            "unit": 单位（默认"个"）,
            "is_weighted": 是否散装（0/1）,
            "cost_price": 成本价,
            "sale_price": 销售价,
            "stock_warning": 库存预警值（默认10）
        }
        :return: {"success": bool, "data": goods_id, "message": str}
        """
        required_fields = ['barcode', 'goods_name', 'category_id', 'sale_price']
        for field in required_fields:
            if not goods_data.get(field):
                return {"success": False, "data": None, "message": f"缺少必填字段: {field}"}
        
        db = DBConnection()
        try:
            db.connect()
            
            # 检查条码是否已存在
            db.execute("SELECT goods_id FROM goods WHERE barcode = %s", (goods_data['barcode'],))
            if db.fetchone():
                return {"success": False, "data": None, "message": "该条码已存在"}
            
            # 检查分类是否存在
            db.execute("SELECT category_id FROM goods_category WHERE category_id = %s", 
                      (goods_data['category_id'],))
            if not db.fetchone():
                return {"success": False, "data": None, "message": "所选分类不存在"}
            
            # 插入商品
            sql = """
                INSERT INTO goods (barcode, goods_name, category_id, unit, is_weighted,
                                   cost_price, price, shelf_status, create_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'off_shelf', NOW())
            """
            db.execute(sql, (
                goods_data['barcode'], 
                goods_data['goods_name'], 
                goods_data['category_id'],
                goods_data.get('unit', '个'), 
                goods_data.get('is_weighted', 0),
                goods_data.get('cost_price', 0),
                goods_data['sale_price']
            ))
            
            goods_id = db.cursor.lastrowid
            
            # 初始化库存记录
            stock_warning = goods_data.get('stock_warning', 10)
            shelf_warning = max(stock_warning // 2, 5)  # 在架预警值为库存预警的一半，最小5
            
            inv_sql = """
                INSERT INTO inventory (goods_id, stock_num, on_shelf_num, stock_warning, 
                                      shelf_warning, stock_status)
                VALUES (%s, 0, 0, %s, %s, 'stock_shortage')
            """
            db.execute(inv_sql, (goods_id, stock_warning, shelf_warning))
            db.commit()
            
            return {"success": True, "data": goods_id, "message": "商品添加成功"}
        except Exception as e:
            db.rollback()
            return {"success": False, "data": None, "message": f"添加失败: {str(e)}"}
        finally:
            db.close()

    def on_shelf(self, goods_id, shelf_code=None, price=None):
        """
        上架商品
        :param goods_id: 商品ID
        :param shelf_code: 货架编码（可选）
        :param price: 新售价（可选）
        :return: {"success": bool, "data": None, "message": str}
        """
        db = DBConnection()
        try:
            db.connect()
            
            db.execute("SELECT goods_id, shelf_status FROM goods WHERE goods_id = %s", (goods_id,))
            goods = db.fetchone()
            
            if not goods:
                return {"success": False, "data": None, "message": "商品不存在"}
            
            if goods['shelf_status'] == 'on_shelf':
                return {"success": False, "data": None, "message": "商品已在售"}
            
            # 检查库存（仓库库存或货架库存有一个大于0即可）
            db.execute("SELECT stock_num, on_shelf_num FROM inventory WHERE goods_id = %s", (goods_id,))
            inv = db.fetchone()
            if not inv:
                return {"success": False, "data": None, "message": "库存记录不存在"}
            
            # 如果货架没货但仓库有货，自动从仓库移一部分到货架
            if inv['on_shelf_num'] <= 0:
                if inv['stock_num'] <= 0:
                    return {"success": False, "data": None, "message": "库存不足，无法上架（仓库和货架均无库存）"}
                # 自动从仓库移10个或全部到货架
                move_num = min(inv['stock_num'], 10)
                db.execute("""
                    UPDATE inventory 
                    SET stock_num = stock_num - %s, on_shelf_num = on_shelf_num + %s 
                    WHERE goods_id = %s
                """, (move_num, move_num, goods_id))
            
            update_fields = ["shelf_status = 'on_shelf'", "update_time = NOW()"]
            params = []
            
            if shelf_code:
                update_fields.append("shelf_id = %s")
                params.append(shelf_code)
            
            if price:
                update_fields.append("price = %s")
                params.append(price)
            
            params.append(goods_id)
            sql = f"UPDATE goods SET {', '.join(update_fields)} WHERE goods_id = %s"
            db.execute(sql, params)
            db.commit()
            
            return {"success": True, "data": None, "message": "商品上架成功"}
        except Exception as e:
            db.rollback()
            return {"success": False, "data": None, "message": f"上架失败: {str(e)}"}
        finally:
            db.close()
    
    def off_shelf(self, goods_id, reason=None):
        """
        下架商品
        :param goods_id: 商品ID
        :param reason: 下架原因
        :return: {"success": bool, "data": None, "message": str}
        """
        db = DBConnection()
        try:
            db.connect()
            
            db.execute("SELECT goods_id, shelf_status FROM goods WHERE goods_id = %s", (goods_id,))
            goods = db.fetchone()
            
            if not goods:
                return {"success": False, "data": None, "message": "商品不存在"}
            
            if goods['shelf_status'] == 'off_shelf':
                return {"success": False, "data": None, "message": "商品已下架"}
            
            sql = "UPDATE goods SET shelf_status = 'off_shelf', update_time = NOW() WHERE goods_id = %s"
            db.execute(sql, (goods_id,))
            db.commit()
            
            return {"success": True, "data": None, "message": "商品下架成功"}
        except Exception as e:
            db.rollback()
            return {"success": False, "data": None, "message": f"下架失败: {str(e)}"}
        finally:
            db.close()
    
    def update_price(self, goods_id, new_price):
        """
        修改定价
        :param goods_id: 商品ID
        :param new_price: 新售价
        :return: {"success": bool, "data": None, "message": str}
        """
        if new_price <= 0:
            return {"success": False, "data": None, "message": "价格必须大于0"}
        
        with DBConnection() as db:
            try:
                db.execute("SELECT goods_id, price FROM goods WHERE goods_id = %s", (goods_id,))
                goods = db.fetchone()
                
                if not goods:
                    return {"success": False, "data": None, "message": "商品不存在"}
                
                old_price = goods['price']
                
                sql = "UPDATE goods SET price = %s, update_time = NOW() WHERE goods_id = %s"
                db.execute(sql, (new_price, goods_id))
                db.commit()
                
                return {"success": True, "data": {"old_price": old_price, "new_price": new_price}, 
                        "message": f"价格已从 ¥{old_price} 修改为 ¥{new_price}"}
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"修改失败: {str(e)}"}
    
    def set_discount(self, goods_id, discount, start_time, end_time):
        """
        设置临时折扣
        :param goods_id: 商品ID
        :param discount: 折扣比例 (0.8 = 8折)
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: {"success": bool, "data": None, "message": str}
        """
        if discount <= 0 or discount > 1:
            return {"success": False, "data": None, "message": "折扣比例应在0-1之间"}
        
        with DBConnection() as db:
            try:
                db.execute("SELECT goods_id FROM goods WHERE goods_id = %s", (goods_id,))
                if not db.fetchone():
                    return {"success": False, "data": None, "message": "商品不存在"}
                
                sql = """
                    UPDATE goods 
                    SET discount = %s, discount_start = %s, discount_end = %s, update_time = NOW()
                    WHERE goods_id = %s
                """
                db.execute(sql, (discount, start_time, end_time, goods_id))
                db.commit()
                
                return {"success": True, "data": None, "message": f"已设置{int(discount*100)}折优惠"}
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"设置失败: {str(e)}"}
    
    def get_goods_list(self, filters=None):
        """
        获取商品列表
        :param filters: {"category_id", "status", "keyword"}
        :return: {"success": bool, "data": list, "message": str}
        """
        filters = filters or {}
        
        with DBConnection() as db:
            try:
                sql = """
                    SELECT g.goods_id, g.barcode, g.goods_name, g.category_id, g.unit,
                           g.cost_price, g.price as sale_price, g.discount, g.shelf_status,
                           gc.category_name, i.stock_num
                    FROM goods g
                    LEFT JOIN goods_category gc ON g.category_id = gc.category_id
                    LEFT JOIN inventory i ON g.goods_id = i.goods_id
                    WHERE 1=1
                """
                params = []
                
                if filters.get('category_id'):
                    # 获取该分类及其所有子分类的ID
                    category_ids = self._get_category_and_children(db, filters['category_id'])
                    if category_ids:
                        placeholders = ','.join(['%s'] * len(category_ids))
                        sql += f" AND g.category_id IN ({placeholders})"
                        params.extend(category_ids)
                
                if filters.get('status'):
                    status_code = self.STATUS_MAP.get(filters['status'], filters['status'])
                    sql += " AND g.shelf_status = %s"
                    params.append(status_code)
                
                if filters.get('keyword'):
                    sql += " AND (g.barcode LIKE %s OR g.goods_name LIKE %s)"
                    keyword = f"%{filters['keyword']}%"
                    params.extend([keyword, keyword])
                
                sql += " ORDER BY g.goods_id"
                db.execute(sql, params)
                goods_list = db.fetchall()
                
                for goods in goods_list:
                    goods['status_display'] = self.STATUS_DISPLAY.get(goods['shelf_status'], goods['shelf_status'])
                    goods['sale_price_str'] = f"¥{goods['sale_price']:.2f}"
                
                return {"success": True, "data": goods_list, "message": "获取成功"}
            except Exception as e:
                return {"success": False, "data": [], "message": f"查询失败: {str(e)}"}
    
    def _get_category_and_children(self, db, category_id):
        """获取分类及其所有子分类ID"""
        result = [category_id]
        
        # 获取直接子分类
        db.execute("SELECT category_id FROM goods_category WHERE parent_id = %s", (category_id,))
        children = db.fetchall()
        
        for child in children:
            result.extend(self._get_category_and_children(db, child['category_id']))
        
        return result
    
    def get_goods_by_barcode(self, barcode):
        """根据条码获取商品"""
        with DBConnection() as db:
            sql = """
                SELECT g.*, g.price as sale_price, gc.category_name, i.stock_num
                FROM goods g
                LEFT JOIN goods_category gc ON g.category_id = gc.category_id
                LEFT JOIN inventory i ON g.goods_id = i.goods_id
                WHERE g.barcode = %s
            """
            db.execute(sql, (barcode,))
            goods = db.fetchone()
            
            if goods:
                goods['status_display'] = self.STATUS_DISPLAY.get(goods['shelf_status'], goods['shelf_status'])
                return {"success": True, "data": goods, "message": "获取成功"}
            return {"success": False, "data": None, "message": "商品不存在"}
