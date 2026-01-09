# -*- coding: utf-8 -*-
"""
退货查询逻辑 - 组员4负责
"""

from datetime import datetime, timedelta
from db.db_conn import DBConnection
from config import SYSTEM_CONFIG


class ReturnQueryLogic:
    """退货查询业务逻辑"""
    
    def query_order_for_return(self, keyword):
        """按小票号/卡号/手机号查询可退货订单"""
        if not keyword or not keyword.strip():
            return {"success": False, "data": [], "message": "请输入查询条件"}
        
        keyword = keyword.strip()
        return_limit_days = SYSTEM_CONFIG.get('return_limit_days', 7)
        limit_date = datetime.now() - timedelta(days=return_limit_days)
        
        try:
            with DBConnection() as db:
                sql = """
                    SELECT o.order_id, o.order_no, o.member_id, o.total_amount,
                           o.discount_amount, o.actual_amount, o.points_earned,
                           o.order_status, o.create_time, o.complete_time,
                           m.card_no, m.name AS member_name, m.phone
                    FROM order_info o
                    LEFT JOIN member m ON o.member_id = m.member_id
                    WHERE o.order_status = 'completed'
                      AND o.complete_time >= %s
                      AND (o.order_no = %s OR m.card_no = %s OR m.phone = %s)
                    ORDER BY o.complete_time DESC
                """
                db.execute(sql, (limit_date, keyword, keyword, keyword))
                orders = db.fetchall()
                
                if not orders:
                    return {"success": True, "data": [], "message": "未找到符合条件的可退货订单"}
                
                return {"success": True, "data": orders, "message": f"找到 {len(orders)} 条可退货订单"}
        except Exception as e:
            return {"success": False, "data": [], "message": f"查询失败: {str(e)}"}
    
    def get_order_detail(self, order_id):
        """获取订单明细"""
        if not order_id:
            return {"success": False, "data": None, "message": "订单ID不能为空"}
        
        try:
            with DBConnection() as db:
                order_sql = """
                    SELECT o.order_id, o.order_no, o.member_id, o.cashier_id,
                           o.total_amount, o.discount_amount, o.actual_amount,
                           o.points_earned, o.points_used, o.order_status,
                           o.create_time, o.complete_time,
                           m.card_no, m.name AS member_name, m.phone,
                           u.real_name AS cashier_name
                    FROM order_info o
                    LEFT JOIN member m ON o.member_id = m.member_id
                    LEFT JOIN sys_user u ON o.cashier_id = u.user_id
                    WHERE o.order_id = %s
                """
                db.execute(order_sql, (order_id,))
                order = db.fetchone()
                
                if not order:
                    return {"success": False, "data": None, "message": "订单不存在"}
                
                detail_sql = """
                    SELECT d.detail_id, d.order_id, d.goods_id, d.goods_name,
                           d.barcode, d.unit_price, d.quantity, d.discount,
                           d.subtotal, d.is_returned, d.returned_quantity,
                           (d.quantity - d.returned_quantity) AS returnable_quantity
                    FROM order_detail d WHERE d.order_id = %s ORDER BY d.detail_id
                """
                db.execute(detail_sql, (order_id,))
                details = db.fetchall()
                
                order['details'] = details
                return {"success": True, "data": order, "message": "获取成功"}
        except Exception as e:
            return {"success": False, "data": None, "message": f"获取订单明细失败: {str(e)}"}

    def check_return_valid(self, order_id):
        """
        校验是否在7天退货期内
        :param order_id: 订单ID
        :return: {"success": bool, "data": dict, "message": str}
        """
        if not order_id:
            return {"success": False, "data": None, "message": "订单ID不能为空"}
        
        return_limit_days = SYSTEM_CONFIG.get('return_limit_days', 7)
        
        try:
            with DBConnection() as db:
                sql = """
                    SELECT order_id, order_no, order_status, complete_time,
                           DATEDIFF(NOW(), complete_time) AS days_passed
                    FROM order_info WHERE order_id = %s
                """
                db.execute(sql, (order_id,))
                order = db.fetchone()
                
                if not order:
                    return {"success": False, "data": None, "message": "订单不存在"}
                
                if order['order_status'] not in ('completed', 'part_returned'):
                    return {
                        "success": False, 
                        "data": {"is_valid": False, "reason": "order_status"},
                        "message": f"订单状态为 {order['order_status']}，不可退货"
                    }
                
                days_passed = order['days_passed'] or 0
                if days_passed > return_limit_days:
                    return {
                        "success": False,
                        "data": {"is_valid": False, "reason": "expired", "days_passed": days_passed},
                        "message": f"订单已超过{return_limit_days}天退货期限（已过{days_passed}天）"
                    }
                
                remaining_days = return_limit_days - days_passed
                return {
                    "success": True,
                    "data": {"is_valid": True, "days_passed": days_passed, "remaining_days": remaining_days},
                    "message": f"订单在退货期内，剩余{remaining_days}天"
                }
        except Exception as e:
            return {"success": False, "data": None, "message": f"校验失败: {str(e)}"}

    def query_return_records(self, keyword=""):
        """
        查询退货记录
        :param keyword: 订单号（可选，为空则查询全部）
        :return: {"success": bool, "data": list, "message": str}
        """
        try:
            with DBConnection() as db:
                if keyword:
                    sql = """
                        SELECT r.return_id, r.return_no, r.order_id, r.return_type,
                               r.refund_amount, r.points_deducted, r.return_reason,
                               r.reason_detail, r.return_status, r.create_time,
                               o.order_no
                        FROM return_record r
                        JOIN order_info o ON r.order_id = o.order_id
                        WHERE o.order_no LIKE %s OR r.return_no LIKE %s
                        ORDER BY r.create_time DESC
                        LIMIT 100
                    """
                    db.execute(sql, (f"%{keyword}%", f"%{keyword}%"))
                else:
                    sql = """
                        SELECT r.return_id, r.return_no, r.order_id, r.return_type,
                               r.refund_amount, r.points_deducted, r.return_reason,
                               r.reason_detail, r.return_status, r.create_time,
                               o.order_no
                        FROM return_record r
                        JOIN order_info o ON r.order_id = o.order_id
                        ORDER BY r.create_time DESC
                        LIMIT 100
                    """
                    db.execute(sql)
                
                records = db.fetchall()
                return {"success": True, "data": records, "message": f"查询到 {len(records)} 条记录"}
        except Exception as e:
            return {"success": False, "data": [], "message": f"查询失败: {str(e)}"}
