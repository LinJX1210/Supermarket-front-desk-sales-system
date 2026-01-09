# -*- coding: utf-8 -*-
"""
收银结算逻辑 - 组员1负责
"""

import random
from datetime import datetime
from decimal import Decimal
from db.db_conn import DBConnection


def get_goods_by_barcode(barcode):
    """
    根据条码查询商品信息
    :param barcode: 商品条码
    :return: {"success": bool, "data": dict, "message": str}
    """
    try:
        with DBConnection() as db:
            sql = """
                SELECT g.goods_id, g.barcode, g.goods_name, g.price, g.discount,
                       g.unit, g.is_weighted, g.shelf_status, i.on_shelf_num
                FROM goods g
                LEFT JOIN inventory i ON g.goods_id = i.goods_id
                WHERE g.barcode = %s
            """
            db.execute(sql, (barcode,))
            goods = db.fetchone()
            
            if not goods:
                return {"success": False, "data": None, "message": "商品不存在"}
            
            if goods["shelf_status"] != "on_shelf":
                return {"success": False, "data": None, "message": "商品未上架"}
            
            if not goods["on_shelf_num"] or goods["on_shelf_num"] <= 0:
                return {"success": False, "data": None, "message": "商品库存不足"}
            
            return {
                "success": True,
                "data": {
                    "goods_id": goods["goods_id"],
                    "barcode": goods["barcode"],
                    "goods_name": goods["goods_name"],
                    "price": float(goods["price"]),
                    "discount": float(goods["discount"]) if goods["discount"] else 1.0,
                    "unit": goods["unit"],
                    "is_weighted": goods["is_weighted"],
                    "stock": goods["on_shelf_num"]
                },
                "message": "查询成功"
            }
    except Exception as e:
        return {"success": False, "data": None, "message": f"查询失败: {str(e)}"}


def calculate_bulk_price(barcode, weight):
    """
    计算散装商品价格
    :param barcode: 商品条码
    :param weight: 重量(kg)
    :return: {"success": bool, "data": dict, "message": str}
    """
    try:
        weight = Decimal(str(weight))
        if weight <= 0:
            return {"success": False, "data": None, "message": "重量必须大于0"}
        
        result = get_goods_by_barcode(barcode)
        if not result["success"]:
            return result
        
        goods = result["data"]
        if not goods["is_weighted"]:
            return {"success": False, "data": None, "message": "该商品不是散装商品"}
        
        price = Decimal(str(goods["price"]))
        discount = Decimal(str(goods["discount"]))
        subtotal = weight * price * discount
        
        return {
            "success": True,
            "data": {
                "goods_id": goods["goods_id"],
                "barcode": goods["barcode"],
                "goods_name": goods["goods_name"],
                "unit_price": float(price),
                "quantity": float(weight),
                "discount": float(discount),
                "subtotal": float(subtotal.quantize(Decimal("0.01")))
            },
            "message": "计算成功"
        }
    except Exception as e:
        return {"success": False, "data": None, "message": f"计算失败: {str(e)}"}


def generate_order_no():
    """生成订单号: ORD + 年月日时分秒 + 4位随机数"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = str(random.randint(1000, 9999))
    return f"ORD{timestamp}{random_num}"


def calculate_order_total(items, discount_rate=1.0):
    """
    计算订单金额
    :param items: 商品列表
    :param discount_rate: 会员折扣率
    :return: {"total_amount", "discount_amount", "actual_amount"}
    """
    total_amount = sum(Decimal(str(item["subtotal"])) for item in items)
    discount_rate = Decimal(str(discount_rate))
    discount_amount = total_amount * (1 - discount_rate)
    actual_amount = total_amount - discount_amount
    
    return {
        "total_amount": float(total_amount.quantize(Decimal("0.01"))),
        "discount_amount": float(discount_amount.quantize(Decimal("0.01"))),
        "actual_amount": float(actual_amount.quantize(Decimal("0.01")))
    }


def check_stock(items):
    """
    检查库存是否充足
    :param items: 商品列表
    :return: {"success": bool, "message": str}
    """
    try:
        with DBConnection() as db:
            for item in items:
                sql = "SELECT on_shelf_num, stock_num FROM inventory WHERE goods_id = %s"
                db.execute(sql, (item["goods_id"],))
                result = db.fetchone()
                
                if not result:
                    # 库存记录不存在，跳过检查（允许结账）
                    continue
                
                on_shelf = result["on_shelf_num"] or 0
                if on_shelf < item["quantity"]:
                    return {
                        "success": False,
                        "message": f"商品 {item['goods_name']} 库存不足（当前库存: {on_shelf}）"
                    }
            return {"success": True, "message": "库存充足"}
    except Exception as e:
        return {"success": False, "message": f"库存检查失败: {str(e)}"}


def create_order(cashier_id, member_id, items, pay_method):
    """
    创建订单并完成结算
    :param cashier_id: 收银员ID
    :param member_id: 会员ID (可为None)
    :param items: 商品列表 [{goods_id, goods_name, barcode, unit_price, quantity, discount, subtotal}, ...]
    :param pay_method: 支付方式 (cash/bank_card/wechat/alipay)
    :return: {"success": bool, "data": dict, "message": str}
    """
    # 支付方式映射
    pay_method_map = {
        "现金": "cash",
        "银行卡": "bank_card",
        "微信": "bank_card",
        "支付宝": "bank_card"
    }
    payment_type = pay_method_map.get(pay_method, "cash")
    
    db = None
    try:
        # 检查库存
        stock_check = check_stock(items)
        if not stock_check["success"]:
            return stock_check
        
        # 获取会员折扣
        discount_rate = 1.0
        points_earned = 0
        
        if member_id:
            try:
                with DBConnection() as db_temp:
                    sql = """
                        SELECT mlr.discount_rate
                        FROM member m
                        JOIN member_level_rule mlr ON m.level_code = mlr.level_code
                        WHERE m.member_id = %s AND m.status = 'active'
                    """
                    db_temp.execute(sql, (member_id,))
                    result = db_temp.fetchone()
                    if result:
                        discount_rate = float(result['discount_rate'])
            except Exception:
                pass  # 获取折扣失败时使用默认值1.0
        
        # 计算金额
        amounts = calculate_order_total(items, discount_rate)
        order_no = generate_order_no()
        
        # 计算积分
        if member_id:
            points_earned = int(amounts["actual_amount"])
        
        db = DBConnection()
        db.connect()
        
        try:
            # 1. 写入订单表
            sql_order = """
                INSERT INTO order_info 
                (order_no, member_id, cashier_id, total_amount, discount_amount, 
                 actual_amount, points_earned, order_status, create_time, complete_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'completed', NOW(), NOW())
            """
            db.execute(sql_order, (
                order_no, member_id, cashier_id,
                amounts["total_amount"], amounts["discount_amount"],
                amounts["actual_amount"], points_earned
            ))
            order_id = db.cursor.lastrowid
            
            # 2. 写入订单明细表
            sql_detail = """
                INSERT INTO order_detail 
                (order_id, goods_id, goods_name, barcode, unit_price, quantity, discount, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            for item in items:
                db.execute(sql_detail, (
                    order_id, item["goods_id"], item["goods_name"], item["barcode"],
                    item["unit_price"], item["quantity"], item["discount"], item["subtotal"]
                ))
            
            # 3. 写入支付记录表
            sql_payment = """
                INSERT INTO payment_record 
                (order_id, payment_type, amount, transaction_type, payment_time)
                VALUES (%s, %s, %s, 'pay', NOW())
            """
            db.execute(sql_payment, (order_id, payment_type, amounts["actual_amount"]))
            
            # 4. 扣减库存
            try:
                from logic.inventory_logic import InventoryLogic
                inv_logic = InventoryLogic()
                for item in items:
                    inv_logic.reduce_stock(item["goods_id"], item["quantity"])
            except (ImportError, Exception):
                # 组员2的模块未完成时，直接更新库存
                sql_stock = """
                    UPDATE inventory SET on_shelf_num = on_shelf_num - %s 
                    WHERE goods_id = %s AND on_shelf_num >= %s
                """
                for item in items:
                    db.execute(sql_stock, (item["quantity"], item["goods_id"], item["quantity"]))
            
            # 5. 累加会员积分（直接在当前事务中更新，避免嵌套事务死锁）
            if member_id and points_earned > 0:
                sql_points = """
                    UPDATE member SET total_points = total_points + %s,
                    total_consume = total_consume + %s WHERE member_id = %s
                """
                db.execute(sql_points, (points_earned, amounts["actual_amount"], member_id))
            
            db.commit()
            
            return {
                "success": True,
                "data": {
                    "order_id": order_id,
                    "order_no": order_no,
                    "total_amount": amounts["total_amount"],
                    "discount_amount": amounts["discount_amount"],
                    "actual_amount": amounts["actual_amount"],
                    "points_earned": points_earned,
                    "pay_method": pay_method,
                    "items": items
                },
                "message": "结算成功"
            }
            
        except Exception as e:
            db.rollback()
            raise e
            
    except Exception as e:
        return {"success": False, "data": None, "message": f"结算失败: {str(e)}"}
    finally:
        if db:
            db.close()
