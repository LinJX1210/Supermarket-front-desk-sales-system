# -*- coding: utf-8 -*-
"""
部分退货逻辑 - 组员4负责
"""

from datetime import datetime
from decimal import Decimal
from db.db_conn import DBConnection
from config import SYSTEM_CONFIG


class ReturnPartLogic:
    """部分退货业务逻辑"""
    
    def process_part_return(self, order_id, return_items, reason, operator_id, 
                            reason_detail=None, quality_photo=None):
        """
        处理部分退货
        :param order_id: 原订单ID
        :param return_items: 退货商品列表 [{detail_id, goods_id, quantity, refund_amount}, ...]
        :param reason: 退货原因
        :param operator_id: 操作员ID
        :return: {"success": bool, "data": dict, "message": str}
        """
        if not order_id or not return_items or not reason or not operator_id:
            return {"success": False, "data": None, "message": "缺少必要参数"}
        
        if not isinstance(return_items, list) or len(return_items) == 0:
            return {"success": False, "data": None, "message": "退货商品列表不能为空"}
        
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

            # 3. 校验退货商品并计算退款金额
            total_refund = Decimal('0')
            validated_items = []
            
            for item in return_items:
                detail_id = item.get('detail_id')
                return_qty = Decimal(str(item.get('quantity', 0)))
                
                if not detail_id or return_qty <= 0:
                    continue
                
                detail_sql = """
                    SELECT detail_id, goods_id, goods_name, barcode, unit_price,
                           quantity, discount, subtotal, is_returned, returned_quantity
                    FROM order_detail WHERE detail_id = %s AND order_id = %s
                """
                db.execute(detail_sql, (detail_id, order_id))
                detail = db.fetchone()
                
                if not detail:
                    continue
                
                returnable_qty = Decimal(str(detail['quantity'])) - Decimal(str(detail['returned_quantity']))
                if return_qty > returnable_qty:
                    return_qty = returnable_qty
                
                if return_qty <= 0:
                    continue
                
                unit_price = Decimal(str(detail['unit_price']))
                discount = Decimal(str(detail['discount']))
                item_refund = unit_price * return_qty * discount
                
                validated_items.append({
                    'detail_id': detail_id,
                    'goods_id': detail['goods_id'],
                    'goods_name': detail['goods_name'],
                    'barcode': detail['barcode'],
                    'return_quantity': float(return_qty),
                    'refund_amount': float(item_refund),
                    'original_quantity': float(detail['quantity'])
                })
                
                total_refund += item_refund
            
            if not validated_items:
                return {"success": False, "data": None, "message": "没有有效的退货商品"}
            
            # 4. 按比例计算扣减积分
            original_amount = Decimal(str(order['actual_amount']))
            original_points = order['points_earned'] or 0
            
            if original_amount > 0 and original_points > 0:
                points_ratio = total_refund / original_amount
                points_to_deduct = int(float(points_ratio) * original_points)
            else:
                points_to_deduct = 0
            
            # 5. 生成退货单号
            return_no = self._generate_return_no(db)
            
            # 6. 写入退货记录表
            return_sql = """
                INSERT INTO return_record 
                (return_no, order_id, return_type, refund_amount, points_deducted,
                 return_reason, reason_detail, quality_photo, operator_id, return_status, create_time)
                VALUES (%s, %s, 'part', %s, %s, %s, %s, %s, %s, 'completed', NOW())
            """
            db.execute(return_sql, (return_no, order_id, float(total_refund), points_to_deduct,
                                    reason, reason_detail, quality_photo, operator_id))
            return_id = db.cursor.lastrowid
            
            # 7. 写入退货明细表 & 更新订单明细 & 恢复库存
            for item in validated_items:
                goods_status = 'pending_inspect' if reason == 'quality_issue' else 'to_stock'
                
                return_detail_sql = """
                    INSERT INTO return_detail
                    (return_id, order_detail_id, goods_id, return_quantity, refund_amount, return_reason, goods_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                db.execute(return_detail_sql, (return_id, item['detail_id'], item['goods_id'],
                                               item['return_quantity'], item['refund_amount'], 
                                               reason, goods_status))
                
                new_returned_qty = item['return_quantity']
                update_detail_sql = """
                    UPDATE order_detail
                    SET returned_quantity = returned_quantity + %s,
                        is_returned = CASE WHEN returned_quantity + %s >= quantity THEN 1 ELSE is_returned END
                    WHERE detail_id = %s
                """
                db.execute(update_detail_sql, (new_returned_qty, new_returned_qty, item['detail_id']))
                
                self._restore_stock(db, item['goods_id'], int(item['return_quantity']))
            
            # 8. 更新订单状态为部分退货
            db.execute("UPDATE order_info SET order_status = 'part_returned' WHERE order_id = %s", (order_id,))
            
            # 9. 扣减会员积分
            if order['member_id'] and points_to_deduct > 0:
                self._reduce_member_points(db, order['member_id'], points_to_deduct)
            
            db.commit()
            
            return {
                "success": True,
                "data": {
                    "return_id": return_id,
                    "return_no": return_no,
                    "refund_amount": float(total_refund),
                    "points_deducted": points_to_deduct,
                    "return_type": "part",
                    "return_items": validated_items
                },
                "message": "部分退货成功"
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "data": None, "message": f"部分退货失败: {str(e)}"}
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
