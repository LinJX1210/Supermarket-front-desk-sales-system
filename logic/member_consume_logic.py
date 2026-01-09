# -*- coding: utf-8 -*-
"""
会员消费管理逻辑 - 组员3负责
"""

from db.db_conn import DBConnection


class MemberConsumeLogic:
    """会员消费管理业务逻辑"""
    
    LEVEL_ORDER = ['normal', 'silver', 'gold']
    
    LEVEL_DISPLAY = {
        "normal": "普通会员",
        "silver": "银卡会员",
        "gold": "金卡会员",
    }
    
    def get_consume_records(self, member_id, limit=50):
        """获取会员消费记录"""
        with DBConnection() as db:
            try:
                sql = """
                    SELECT o.order_id, o.order_no, o.total_amount, o.discount_amount,
                           o.actual_amount, o.points_earned, o.points_used,
                           o.order_status, o.create_time, o.complete_time
                    FROM order_info o
                    WHERE o.member_id = %s AND o.order_status IN ('completed', 'part_returned')
                    ORDER BY o.create_time DESC
                    LIMIT %s
                """
                db.execute(sql, (member_id, limit))
                records = db.fetchall()
                
                for record in records:
                    if record['create_time']:
                        record['create_time_str'] = record['create_time'].strftime('%Y-%m-%d %H:%M')
                    record['total_amount_str'] = f"¥{record['total_amount']:.2f}"
                    record['actual_amount_str'] = f"¥{record['actual_amount']:.2f}"
                
                return {"success": True, "data": records, "message": f"查询到{len(records)}条记录"}
            except Exception as e:
                return {"success": False, "data": [], "message": f"查询失败: {str(e)}"}
    
    def reduce_member_points(self, member_id, points, reason="退货扣减积分"):
        """扣减积分（退货调用）"""
        if points <= 0:
            return {"success": False, "data": None, "message": "扣减积分数必须大于0"}
        
        with DBConnection() as db:
            try:
                db.execute("SELECT total_points FROM member WHERE member_id = %s", (member_id,))
                member = db.fetchone()
                
                if not member:
                    return {"success": False, "data": None, "message": "会员不存在"}
                
                new_points = max(0, member['total_points'] - points)
                actual_reduced = member['total_points'] - new_points
                
                db.execute("UPDATE member SET total_points = %s WHERE member_id = %s", 
                          (new_points, member_id))
                db.commit()
                
                return {
                    "success": True, 
                    "data": {"points_reduced": actual_reduced, "new_total": new_points},
                    "message": f"已扣减{actual_reduced}积分"
                }
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"扣减失败: {str(e)}"}
