# -*- coding: utf-8 -*-
"""
退货异常处理逻辑 - 组员4负责
"""

from datetime import datetime
from db.db_conn import DBConnection
from config import SYSTEM_CONFIG


class ReturnExceptionLogic:
    """退货异常处理业务逻辑"""
    
    NON_RETURNABLE_CATEGORIES = ['生鲜食品', '熟食', '冷冻食品']
    
    def validate_return(self, order_id, goods_list):
        """校验退货条件，返回校验结果"""
        if not order_id:
            return {"success": False, "data": None, "message": "订单ID不能为空"}
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "goods_validation": []
        }
        
        try:
            period_check = self.check_return_period(order_id)
            if not period_check['success']:
                validation_result['is_valid'] = False
                validation_result['errors'].append(period_check['message'])
                return {"success": False, "data": validation_result, "message": period_check['message']}
            
            if not period_check['data']['is_valid']:
                validation_result['is_valid'] = False
                validation_result['errors'].append(period_check['message'])
            else:
                remaining = period_check['data'].get('remaining_days', 0)
                if remaining <= 2:
                    validation_result['warnings'].append(f"退货期限即将到期，剩余{remaining}天")
            
            if goods_list:
                for item in goods_list:
                    goods_id = item.get('goods_id')
                    quantity = item.get('quantity', 0)
                    
                    goods_check = self.check_goods_returnable(goods_id)
                    
                    goods_validation = {
                        "goods_id": goods_id,
                        "quantity": quantity,
                        "is_returnable": goods_check['data']['is_returnable'] if goods_check['success'] else False,
                        "reason": goods_check['message']
                    }
                    
                    if not goods_validation['is_returnable']:
                        validation_result['is_valid'] = False
                        validation_result['errors'].append(f"商品ID {goods_id}: {goods_check['message']}")
                    
                    validation_result['goods_validation'].append(goods_validation)
            
            message = "校验通过" if validation_result['is_valid'] else "校验未通过，请查看错误信息"
            return {"success": True, "data": validation_result, "message": message}
            
        except Exception as e:
            return {"success": False, "data": None, "message": f"校验失败: {str(e)}"}

    def check_return_period(self, order_id):
        """
        检查是否超出退货期限（7天）
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
                           TIMESTAMPDIFF(DAY, complete_time, NOW()) AS days_passed
                    FROM order_info
                    WHERE order_id = %s
                """
                db.execute(sql, (order_id,))
                order = db.fetchone()
                
                if not order:
                    return {"success": False, "data": None, "message": "订单不存在"}
                
                valid_statuses = ('completed', 'part_returned')
                if order['order_status'] not in valid_statuses:
                    return {
                        "success": True,
                        "data": {"is_valid": False, "reason": "invalid_status", "order_status": order['order_status']},
                        "message": f"订单状态为 {order['order_status']}，不可退货"
                    }
                
                if not order['complete_time']:
                    return {
                        "success": True,
                        "data": {"is_valid": False, "reason": "no_complete_time"},
                        "message": "订单未完成，无法退货"
                    }
                
                days_passed = order['days_passed'] or 0
                
                if days_passed > return_limit_days:
                    return {
                        "success": True,
                        "data": {"is_valid": False, "reason": "expired", "days_passed": days_passed, "limit_days": return_limit_days},
                        "message": f"订单已超过{return_limit_days}天退货期限（已过{days_passed}天）"
                    }
                
                remaining_days = return_limit_days - days_passed
                return {
                    "success": True,
                    "data": {"is_valid": True, "days_passed": days_passed, "remaining_days": remaining_days, "limit_days": return_limit_days},
                    "message": f"在退货期内，剩余{remaining_days}天"
                }
                
        except Exception as e:
            return {"success": False, "data": None, "message": f"检查失败: {str(e)}"}

    def check_goods_returnable(self, goods_id):
        """
        检查商品是否可退（如食品拆封不可退）
        :param goods_id: 商品ID
        :return: {"success": bool, "data": dict, "message": str}
        """
        if not goods_id:
            return {"success": False, "data": None, "message": "商品ID不能为空"}
        
        try:
            with DBConnection() as db:
                sql = """
                    SELECT g.goods_id, g.goods_name, g.barcode, g.shelf_status,
                           gc.category_name, gc.category_id
                    FROM goods g
                    JOIN goods_category gc ON g.category_id = gc.category_id
                    WHERE g.goods_id = %s
                """
                db.execute(sql, (goods_id,))
                goods = db.fetchone()
                
                if not goods:
                    return {
                        "success": True,
                        "data": {"is_returnable": False, "reason": "not_found"},
                        "message": "商品不存在"
                    }
                
                category_name = goods['category_name']
                if category_name in self.NON_RETURNABLE_CATEGORIES:
                    return {
                        "success": True,
                        "data": {"is_returnable": False, "reason": "category_restricted", "category": category_name, "goods_name": goods['goods_name']},
                        "message": f"商品 {goods['goods_name']} 属于 {category_name} 分类，不支持退货"
                    }
                
                return {
                    "success": True,
                    "data": {"is_returnable": True, "goods_id": goods_id, "goods_name": goods['goods_name'], "category": category_name},
                    "message": "商品可退货"
                }
                
        except Exception as e:
            return {"success": False, "data": None, "message": f"检查失败: {str(e)}"}
    
    def handle_points_downgrade(self, member_id):
        """
        积分扣减后检查是否触发降级
        :param member_id: 会员ID
        :return: {"success": bool, "data": dict, "message": str}
        """
        if not member_id:
            return {"success": False, "data": None, "message": "会员ID不能为空"}
        
        try:
            with DBConnection() as db:
                member_sql = """
                    SELECT m.member_id, m.card_no, m.name, m.level_code, m.total_consume, m.total_points
                    FROM member m WHERE m.member_id = %s
                """
                db.execute(member_sql, (member_id,))
                member = db.fetchone()
                
                if not member:
                    return {"success": False, "data": None, "message": "会员不存在"}
                
                current_level = member['level_code']
                total_consume = float(member['total_consume'])
                total_points = member['total_points']
                
                rule_sql = "SELECT level_code, level_name, min_consume, min_points FROM member_level_rule ORDER BY min_consume ASC"
                db.execute(rule_sql)
                rules = db.fetchall()
                
                target_level = 'normal'
                target_level_name = '普通会员'
                
                for rule in rules:
                    if total_consume >= float(rule['min_consume']) and total_points >= rule['min_points']:
                        target_level = rule['level_code']
                        target_level_name = rule['level_name']
                
                level_order = {'normal': 0, 'silver': 1, 'gold': 2}
                current_order = level_order.get(current_level, 0)
                target_order = level_order.get(target_level, 0)
                
                if target_order < current_order:
                    db.execute("UPDATE member SET level_code = %s, update_time = NOW() WHERE member_id = %s", (target_level, member_id))
                    db.commit()
                    
                    return {
                        "success": True,
                        "data": {"need_downgrade": True, "old_level": current_level, "new_level": target_level, "new_level_name": target_level_name},
                        "message": f"会员已从 {current_level} 降级为 {target_level_name}"
                    }
                else:
                    return {
                        "success": True,
                        "data": {"need_downgrade": False, "current_level": current_level, "member_name": member['name']},
                        "message": "会员等级无需变更"
                    }
                    
        except Exception as e:
            return {"success": False, "data": None, "message": f"检查降级失败: {str(e)}"}
