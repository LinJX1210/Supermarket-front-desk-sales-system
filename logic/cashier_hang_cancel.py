# -*- coding: utf-8 -*-
"""
挂单/调单/撤单逻辑 - 组员1负责
"""

from datetime import datetime
from decimal import Decimal
from db.db_conn import DBConnection
from logic.cashier_logic import generate_order_no, calculate_order_total


def hang_order(cashier_id, member_id, items):
    """
    挂单：保存当前未结算订单
    :param cashier_id: 收银员ID
    :param member_id: 会员ID (可为None)
    :param items: 商品列表
    :return: {"success": bool, "data": dict, "message": str}
    """
    if not items:
        return {"success": False, "data": None, "message": "没有商品可挂单"}
    
    db = None
    try:
        db = DBConnection()
        db.connect()
        
        order_no = generate_order_no()
        amounts = calculate_order_total(items)
        
        # 写入订单表，状态为hanged
        sql_order = """
            INSERT INTO order_info 
            (order_no, member_id, cashier_id, total_amount, discount_amount, 
             actual_amount, order_status, create_time)
            VALUES (%s, %s, %s, %s, %s, %s, 'hanged', NOW())
        """
        db.execute(sql_order, (
            order_no, member_id, cashier_id,
            amounts["total_amount"], 0, amounts["total_amount"]
        ))
        order_id = db.cursor.lastrowid
        
        # 写入订单明细表
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
        
        db.commit()
        
        return {
            "success": True,
            "data": {
                "order_id": order_id,
                "order_no": order_no
            },
            "message": "挂单成功"
        }
        
    except Exception as e:
        if db:
            db.rollback()
        return {"success": False, "data": None, "message": f"挂单失败: {str(e)}"}
    finally:
        if db:
            db.close()


def get_hanged_orders(cashier_id=None):
    """
    获取挂单订单列表
    :param cashier_id: 收银员ID (可选，为空则查询所有)
    :return: {"success": bool, "data": list, "message": str}
    """
    try:
        with DBConnection() as db:
            if cashier_id:
                sql = """
                    SELECT o.order_id, o.order_no, o.total_amount, o.create_time,
                           m.card_no AS member_card, m.name AS member_name,
                           u.real_name AS cashier_name
                    FROM order_info o
                    LEFT JOIN member m ON o.member_id = m.member_id
                    LEFT JOIN sys_user u ON o.cashier_id = u.user_id
                    WHERE o.order_status = 'hanged' AND o.cashier_id = %s
                    ORDER BY o.create_time DESC
                """
                db.execute(sql, (cashier_id,))
            else:
                sql = """
                    SELECT o.order_id, o.order_no, o.total_amount, o.create_time,
                           m.card_no AS member_card, m.name AS member_name,
                           u.real_name AS cashier_name
                    FROM order_info o
                    LEFT JOIN member m ON o.member_id = m.member_id
                    LEFT JOIN sys_user u ON o.cashier_id = u.user_id
                    WHERE o.order_status = 'hanged'
                    ORDER BY o.create_time DESC
                """
                db.execute(sql)
            
            orders = db.fetchall()
            
            # 格式化时间
            for order in orders:
                if order["create_time"]:
                    order["create_time"] = order["create_time"].strftime("%Y-%m-%d %H:%M:%S")
                order["total_amount"] = float(order["total_amount"])
            
            return {
                "success": True,
                "data": orders,
                "message": f"查询到 {len(orders)} 个挂单"
            }
            
    except Exception as e:
        return {"success": False, "data": [], "message": f"查询失败: {str(e)}"}


def load_order(order_id):
    """
    调单：加载挂单订单详情
    :param order_id: 订单ID
    :return: {"success": bool, "data": dict, "message": str}
    """
    try:
        with DBConnection() as db:
            # 查询订单信息
            sql_order = """
                SELECT o.order_id, o.order_no, o.member_id, o.cashier_id,
                       o.total_amount, o.create_time, o.order_status,
                       m.card_no, m.name AS member_name
                FROM order_info o
                LEFT JOIN member m ON o.member_id = m.member_id
                WHERE o.order_id = %s
            """
            db.execute(sql_order, (order_id,))
            order = db.fetchone()
            
            if not order:
                return {"success": False, "data": None, "message": "订单不存在"}
            
            if order["order_status"] != "hanged":
                return {"success": False, "data": None, "message": "该订单不是挂单状态"}
            
            # 查询订单明细
            sql_detail = """
                SELECT detail_id, goods_id, goods_name, barcode, 
                       unit_price, quantity, discount, subtotal
                FROM order_detail
                WHERE order_id = %s
            """
            db.execute(sql_detail, (order_id,))
            details = db.fetchall()
            
            # 格式化数据
            items = []
            for d in details:
                items.append({
                    "detail_id": d["detail_id"],
                    "goods_id": d["goods_id"],
                    "goods_name": d["goods_name"],
                    "barcode": d["barcode"],
                    "unit_price": float(d["unit_price"]),
                    "quantity": float(d["quantity"]),
                    "discount": float(d["discount"]),
                    "subtotal": float(d["subtotal"])
                })
            
            return {
                "success": True,
                "data": {
                    "order_id": order["order_id"],
                    "order_no": order["order_no"],
                    "member_id": order["member_id"],
                    "member_card": order["card_no"],
                    "member_name": order["member_name"],
                    "total_amount": float(order["total_amount"]),
                    "items": items
                },
                "message": "调单成功"
            }
            
    except Exception as e:
        return {"success": False, "data": None, "message": f"调单失败: {str(e)}"}


def cancel_order(order_id, is_completed=False):
    """
    撤单
    :param order_id: 订单ID
    :param is_completed: 是否已结账订单
    :return: {"success": bool, "data": None, "message": str}
    """
    db = None
    try:
        db = DBConnection()
        db.connect()
        
        # 查询订单状态
        sql_check = "SELECT order_status FROM order_info WHERE order_id = %s"
        db.execute(sql_check, (order_id,))
        order = db.fetchone()
        
        if not order:
            return {"success": False, "data": None, "message": "订单不存在"}
        
        status = order["order_status"]
        
        if status == "cancelled":
            return {"success": False, "data": None, "message": "订单已撤销"}
        
        if status == "completed" and is_completed:
            # 已结账订单需要走退货流程
            try:
                from logic.return_full_logic import process_full_return
                # 这里应该跳转到退货流程
                return {"success": False, "data": None, "message": "已结账订单请走退货流程"}
            except ImportError:
                return {"success": False, "data": None, "message": "已结账订单请走退货流程"}
        
        if status not in ("hanged", "pending_pay"):
            return {"success": False, "data": None, "message": f"订单状态({status})不允许撤单"}
        
        # 更新订单状态为已撤销
        sql_cancel = "UPDATE order_info SET order_status = 'cancelled' WHERE order_id = %s"
        db.execute(sql_cancel, (order_id,))
        db.commit()
        
        return {"success": True, "data": None, "message": "撤单成功"}
        
    except Exception as e:
        if db:
            db.rollback()
        return {"success": False, "data": None, "message": f"撤单失败: {str(e)}"}
    finally:
        if db:
            db.close()


def resume_order(order_id, cashier_id, pay_method):
    """
    继续结算挂单订单
    :param order_id: 订单ID
    :param cashier_id: 收银员ID
    :param pay_method: 支付方式
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
        # 先加载订单
        load_result = load_order(order_id)
        if not load_result["success"]:
            return load_result
        
        order_data = load_result["data"]
        member_id = order_data["member_id"]
        items = order_data["items"]
        
        # 检查库存
        from logic.cashier_logic import check_stock
        stock_check = check_stock(items)
        if not stock_check["success"]:
            return stock_check
        
        # 获取会员折扣
        discount_rate = 1.0
        if member_id:
            try:
                from logic.member_rule_logic import get_member_discount
                discount_result = get_member_discount(member_id)
                if discount_result["success"]:
                    discount_rate = discount_result["data"]["discount_rate"]
            except ImportError:
                pass
        
        # 计算金额
        amounts = calculate_order_total(items, discount_rate)
        points_earned = int(amounts["actual_amount"]) if member_id else 0
        
        db = DBConnection()
        db.connect()
        
        try:
            # 更新订单状态和金额
            sql_update = """
                UPDATE order_info SET 
                    order_status = 'completed',
                    cashier_id = %s,
                    discount_amount = %s,
                    actual_amount = %s,
                    points_earned = %s,
                    complete_time = NOW()
                WHERE order_id = %s
            """
            db.execute(sql_update, (
                cashier_id, amounts["discount_amount"],
                amounts["actual_amount"], points_earned, order_id
            ))
            
            # 写入支付记录
            sql_payment = """
                INSERT INTO payment_record 
                (order_id, payment_type, amount, transaction_type, payment_time)
                VALUES (%s, %s, %s, 'pay', NOW())
            """
            db.execute(sql_payment, (order_id, payment_type, amounts["actual_amount"]))
            
            # 扣减库存
            try:
                from logic.inventory_logic import InventoryLogic
                inv_logic = InventoryLogic()
                for item in items:
                    inv_logic.reduce_stock(item["goods_id"], item["quantity"])
            except (ImportError, Exception):
                sql_stock = """
                    UPDATE inventory SET on_shelf_num = on_shelf_num - %s 
                    WHERE goods_id = %s
                """
                for item in items:
                    db.execute(sql_stock, (item["quantity"], item["goods_id"]))
            
            # 累加会员积分
            if member_id and points_earned > 0:
                try:
                    from logic.member_rule_logic import add_member_points
                    add_member_points(member_id, amounts["actual_amount"])
                except ImportError:
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
                    "order_no": order_data["order_no"],
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
