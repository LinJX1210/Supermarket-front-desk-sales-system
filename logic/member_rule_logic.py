# -*- coding: utf-8 -*-
"""
会员规则逻辑 - 组员3负责
"""

from db.db_conn import DBConnection


class MemberRuleLogic:
    """会员规则业务逻辑"""
    
    LEVEL_ORDER = ['normal', 'silver', 'gold']
    
    LEVEL_DISPLAY = {
        "normal": "普通会员",
        "silver": "银卡会员",
        "gold": "金卡会员",
    }
    
    def get_all_rules(self):
        """获取所有会员等级规则"""
        with DBConnection() as db:
            try:
                sql = """
                    SELECT rule_id, level_name, level_code, min_consume, min_points, 
                           discount_rate, points_rate, create_time, update_time
                    FROM member_level_rule
                    ORDER BY min_consume ASC
                """
                db.execute(sql)
                rules = db.fetchall()
                return {"success": True, "data": rules, "message": "获取成功"}
            except Exception as e:
                return {"success": False, "data": [], "message": f"获取失败: {str(e)}"}
    
    def get_member_discount(self, member_id):
        """获取会员折扣（收银调用）"""
        with DBConnection() as db:
            try:
                sql = """
                    SELECT m.level_code, mlr.discount_rate, mlr.points_rate, mlr.level_name
                    FROM member m
                    JOIN member_level_rule mlr ON m.level_code = mlr.level_code
                    WHERE m.member_id = %s AND m.status = 'active'
                """
                db.execute(sql, (member_id,))
                result = db.fetchone()
                
                if not result:
                    return {"success": False, "data": None, "message": "会员不存在或已禁用"}
                
                return {
                    "success": True, 
                    "data": {
                        "discount_rate": float(result['discount_rate']),
                        "points_rate": result['points_rate'],
                        "level_code": result['level_code'],
                        "level_name": result['level_name']
                    }, 
                    "message": "获取成功"
                }
            except Exception as e:
                return {"success": False, "data": None, "message": f"获取失败: {str(e)}"}

    def add_member_points(self, member_id, amount):
        """
        累加积分（消费后调用）
        :param member_id: 会员ID
        :param amount: 消费金额
        :return: {"success": bool, "data": {"points_earned", "new_total"}, "message": str}
        """
        with DBConnection() as db:
            try:
                sql = """
                    SELECT m.total_points, m.total_consume, m.level_code, mlr.points_rate
                    FROM member m
                    JOIN member_level_rule mlr ON m.level_code = mlr.level_code
                    WHERE m.member_id = %s AND m.status = 'active'
                """
                db.execute(sql, (member_id,))
                member = db.fetchone()
                
                if not member:
                    return {"success": False, "data": None, "message": "会员不存在或已禁用"}
                
                points_earned = int(float(amount) * member['points_rate'])
                new_points = member['total_points'] + points_earned
                new_consume = float(member['total_consume']) + float(amount)
                
                sql = "UPDATE member SET total_points = %s, total_consume = %s WHERE member_id = %s"
                db.execute(sql, (new_points, new_consume, member_id))
                db.commit()
                
                return {
                    "success": True, 
                    "data": {"points_earned": points_earned, "new_total": new_points}, 
                    "message": f"获得{points_earned}积分"
                }
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"积分累加失败: {str(e)}"}

    def save_all_rules(self, rules_data):
        """
        批量保存所有等级规则
        :param rules_data: {"normal": {...}, "silver": {...}, "gold": {...}}
        :return: {"success": bool, "data": None, "message": str}
        """
        with DBConnection() as db:
            try:
                for level_code, rule in rules_data.items():
                    sql = """
                        UPDATE member_level_rule 
                        SET min_consume=%s, min_points=%s, discount_rate=%s, points_rate=%s
                        WHERE level_code=%s
                    """
                    db.execute(sql, (
                        rule.get('min_consume', 0),
                        rule.get('min_points', 0),
                        rule.get('discount_rate', 1.00),
                        rule.get('points_rate', 1),
                        level_code
                    ))
                db.commit()
                return {"success": True, "data": None, "message": "所有规则保存成功"}
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"保存失败: {str(e)}"}
