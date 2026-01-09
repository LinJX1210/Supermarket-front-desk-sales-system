# -*- coding: utf-8 -*-
"""
整单退货逻辑 - 组员4负责
"""

from datetime import datetime
from db.db_conn import DBConnection
from config import SYSTEM_CONFIG


class ReturnFullLogic:
    """整单退货业务逻辑"""
    
    def process_full_return(self, order_id, reason, reason_detail, operator_id, quality_photo=None):
        """
        处理整单退货
        :param order_id: 原订单ID
        :param reason: 退货原因 (quality_issue/no_reason_7day/spec_mismatch/damaged/other)
        :param reason_detail: 原因详情/质量问题描述
        :param operator_id: 操作员ID
        :param quality_photo: 质量问题照片路径（可选）
        :return: {"success": bool, "data": dict, "message": str}
        """
        if not order_id or not reason or not operator_id:
            return {"success": False, "data": None, "message": "缺少必要参数"}
        
        db = DBConnection()
        try:
            db.connect()
            
            # 1. 获取原订单信息
            order_sql = """
                SELECT order_id, order_no, member_id, total_amount, discount_amount,
                       actual_amount, points_earned, order_status, complete_time
                FROM order_info WHERE order_id = %s
            """
            db.execute(order_sql, (order_id,))
            order = db.fetchone()
            
            if not order:
                return {"success": False, "data": None, "message": "订单不存在"}
            
            if order['order_status'] not in ('completed', 'part_returned'):
                return {"success": False, "data": None, "message": f"订单状态为 {order['order_status']}，不可退货"}
            
            # 2. 检查退货期限
            return_limit_days = SYSTEM_CONFIG.get('return_limit_days', 7)
            if order['complete_time']:
                days_passed = (datetime.now() - order['complete_time']).days
                if days_passed > return_limit_days:
                    return {"success": False, "data": None, "message": f"订单已超过{return_limit_days}天退货期限"}
            
            # 3. 获取订单明细
            detail_sql = """
                SELECT detail_id, goods_id, goods_name, barcode, unit_price,
                       quantity, discount, subtotal, is_returned, returned_quantity
                FROM order_detail WHERE order_id = %s
            """
            db.execute(detail_sql, (order_id,))
            details = db.fetchall()
            
            if not details:
                return {"success": False, "data": None, "message": "订单明细为空"}

            # 4. 计算退款金额（全额退款）
            refund_amount = order['actual_amount']
            points_to_deduct = order['points_earned']
            
            # 5. 生成退货单号
            return_no = self._generate_return_no(db)
            
            # 6. 写入退货记录表
            return_sql = """
                INSERT INTO return_record 
                (return_no, order_id, return_type, refund_amount, points_deducted,
                 return_reason, reason_detail, quality_photo, operator_id, return_status, create_time)
                VALUES (%s, %s, 'full', %s, %s, %s, %s, %s, %s, 'completed', NOW())
            """
            db.execute(return_sql, (return_no, order_id, refund_amount, points_to_deduct,
                                    reason, reason_detail, quality_photo, operator_id))
            return_id = db.cursor.lastrowid
            
            # 7. 写入退货明细表 & 恢复库存
            for detail in details:
                returnable_qty = float(detail['quantity']) - float(detail['returned_quantity'])
                if returnable_qty <= 0:
                    continue
                
                item_refund = float(detail['unit_price']) * returnable_qty * float(detail['discount'])
                goods_status = 'pending_inspect' if reason == 'quality_issue' else 'to_stock'
                
                return_detail_sql = """
                    INSERT INTO return_detail
                    (return_id, order_detail_id, goods_id, return_quantity, refund_amount, return_reason, goods_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                db.execute(return_detail_sql, (return_id, detail['detail_id'], detail['goods_id'],
                                               returnable_qty, item_refund, reason, goods_status))
                
                update_detail_sql = """
                    UPDATE order_detail SET is_returned = 1, returned_quantity = quantity WHERE detail_id = %s
                """
                db.execute(update_detail_sql, (detail['detail_id'],))
                
                self._restore_stock(db, detail['goods_id'], int(returnable_qty))
            
            # 8. 更新订单状态为整单退货
            db.execute("UPDATE order_info SET order_status = 'full_returned' WHERE order_id = %s", (order_id,))
            
            # 9. 扣减会员积分
            if order['member_id'] and points_to_deduct > 0:
                self._reduce_member_points(db, order['member_id'], points_to_deduct)
            
            db.commit()
            
            return {
                "success": True,
                "data": {
                    "return_id": return_id,
                    "return_no": return_no,
                    "refund_amount": float(refund_amount),
                    "points_deducted": points_to_deduct,
                    "return_type": "full"
                },
                "message": "整单退货成功"
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "data": None, "message": f"整单退货失败: {str(e)}"}
        finally:
            db.close()

    def _generate_return_no(self, db):
        """生成退货单号"""
        today = datetime.now().strftime('%Y%m%d')
        prefix = f"RT{today}"
        
        sql = "SELECT return_no FROM return_record WHERE return_no LIKE %s ORDER BY return_no DESC LIMIT 1"
        db.execute(sql, (f"{prefix}%",))
        result = db.fetchone()
        
        if result:
            last_no = int(result['return_no'][-4:])
            new_no = f"{prefix}{last_no + 1:04d}"
        else:
            new_no = f"{prefix}0001"
        
        return new_no
    
    def _restore_stock(self, db, goods_id, num):
        """恢复库存"""
        sql = """
            UPDATE inventory 
            SET stock_num = stock_num + %s,
                stock_status = CASE WHEN stock_num + %s >= stock_warning THEN 'sufficient' ELSE stock_status END,
                update_time = NOW()
            WHERE goods_id = %s
        """
        db.execute(sql, (num, num, goods_id))
    
    def _reduce_member_points(self, db, member_id, points):
        """扣减会员积分"""
        sql = "SELECT total_points FROM member WHERE member_id = %s"
        db.execute(sql, (member_id,))
        member = db.fetchone()
        
        if not member:
            return
        
        old_points = member['total_points']
        new_points = max(0, old_points - points)
        
        db.execute("UPDATE member SET total_points = %s, update_time = NOW() WHERE member_id = %s", 
                  (new_points, member_id))
