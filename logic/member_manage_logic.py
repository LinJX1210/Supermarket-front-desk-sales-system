# -*- coding: utf-8 -*-
"""
会员管理逻辑 - 组员3负责
"""

import random
from datetime import datetime
from db.db_conn import DBConnection


class MemberManageLogic:
    """会员管理业务逻辑"""
    
    LEVEL_MAP = {
        "普通会员": "normal",
        "银卡会员": "silver",
        "金卡会员": "gold",
    }
    
    LEVEL_DISPLAY = {v: k for k, v in LEVEL_MAP.items()}
    
    STATUS_DISPLAY = {
        "active": "正常",
        "disabled": "禁用",
    }
    
    def _generate_card_no(self):
        """生成会员卡号: VIP + 8位数字"""
        random_num = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return f"VIP{random_num}"
    
    def register_member(self, name, phone, address=None):
        """
        注册会员
        :return: {"success": bool, "data": {"member_id", "card_no"}, "message": str}
        """
        if not name:
            return {"success": False, "data": None, "message": "会员姓名不能为空"}
        
        with DBConnection() as db:
            try:
                # 检查手机号是否已注册
                if phone:
                    db.execute("SELECT member_id FROM member WHERE phone = %s", (phone,))
                    if db.fetchone():
                        return {"success": False, "data": None, "message": "该手机号已注册会员"}
                
                # 生成唯一卡号
                card_no = self._generate_card_no()
                db.execute("SELECT member_id FROM member WHERE card_no = %s", (card_no,))
                while db.fetchone():
                    card_no = self._generate_card_no()
                    db.execute("SELECT member_id FROM member WHERE card_no = %s", (card_no,))
                
                sql = """
                    INSERT INTO member (card_no, name, phone, address, level_code, status)
                    VALUES (%s, %s, %s, %s, 'normal', 'active')
                """
                db.execute(sql, (card_no, name, phone or '', address or ''))
                db.commit()
                
                member_id = db.cursor.lastrowid
                return {
                    "success": True, 
                    "data": {"member_id": member_id, "card_no": card_no}, 
                    "message": f"会员注册成功，卡号: {card_no}"
                }
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"注册失败: {str(e)}"}
    
    def update_member(self, member_id, data):
        """
        修改会员信息
        :param data: {"name", "phone", "address", "level", "status"}
        :return: {"success": bool, "data": None, "message": str}
        """
        with DBConnection() as db:
            try:
                db.execute("SELECT member_id FROM member WHERE member_id = %s", (member_id,))
                if not db.fetchone():
                    return {"success": False, "data": None, "message": "会员不存在"}
                
                if data.get('phone'):
                    db.execute("SELECT member_id FROM member WHERE phone = %s AND member_id != %s",
                              (data['phone'], member_id))
                    if db.fetchone():
                        return {"success": False, "data": None, "message": "该手机号已被其他会员使用"}
                
                level_code = self.LEVEL_MAP.get(data.get('level'), data.get('level_code', 'normal'))
                status = 'active' if data.get('status') in ['正常', 'active'] else 'disabled'
                
                sql = """
                    UPDATE member 
                    SET name=%s, phone=%s, address=%s, level_code=%s, status=%s
                    WHERE member_id=%s
                """
                db.execute(sql, (
                    data.get('name', ''), data.get('phone', ''), data.get('address', ''),
                    level_code, status, member_id
                ))
                db.commit()
                return {"success": True, "data": None, "message": "会员信息修改成功"}
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"修改失败: {str(e)}"}

    def query_member(self, keyword):
        """按卡号/手机号查询会员"""
        if not keyword:
            return {"success": False, "data": [], "message": "请输入查询关键字"}
        
        with DBConnection() as db:
            try:
                sql = """
                    SELECT member_id, card_no, name, phone, address, level_code, 
                           total_consume, total_points, status, create_time
                    FROM member
                    WHERE card_no LIKE %s OR phone LIKE %s
                    ORDER BY create_time DESC
                """
                like_keyword = f"%{keyword}%"
                db.execute(sql, (like_keyword, like_keyword))
                members = db.fetchall()
                
                for member in members:
                    member['level_display'] = self.LEVEL_DISPLAY.get(member['level_code'], member['level_code'])
                    member['status_display'] = self.STATUS_DISPLAY.get(member['status'], member['status'])
                    member['total_consume_str'] = f"¥{member['total_consume']:.2f}"
                
                return {"success": True, "data": members, "message": f"查询到{len(members)}条记录"}
            except Exception as e:
                return {"success": False, "data": [], "message": f"查询失败: {str(e)}"}
    
    def get_member_list(self, filters=None):
        """获取会员列表"""
        filters = filters or {}
        
        with DBConnection() as db:
            try:
                sql = """
                    SELECT member_id, card_no, name, phone, address, level_code, 
                           total_consume, total_points, status, create_time
                    FROM member WHERE 1=1
                """
                params = []
                
                if filters.get('level'):
                    level_code = self.LEVEL_MAP.get(filters['level'], filters['level'])
                    sql += " AND level_code = %s"
                    params.append(level_code)
                
                if filters.get('status'):
                    status_code = 'active' if filters['status'] == '正常' else 'disabled'
                    sql += " AND status = %s"
                    params.append(status_code)
                
                if filters.get('keyword'):
                    sql += " AND (card_no LIKE %s OR name LIKE %s OR phone LIKE %s)"
                    keyword = f"%{filters['keyword']}%"
                    params.extend([keyword, keyword, keyword])
                
                sql += " ORDER BY create_time DESC"
                db.execute(sql, params)
                members = db.fetchall()
                
                for member in members:
                    member['level_display'] = self.LEVEL_DISPLAY.get(member['level_code'], member['level_code'])
                    member['status_display'] = self.STATUS_DISPLAY.get(member['status'], member['status'])
                    member['total_consume_str'] = f"¥{member['total_consume']:.2f}"
                    if member['create_time']:
                        member['create_time_str'] = member['create_time'].strftime('%Y-%m-%d')
                
                return {"success": True, "data": members, "message": "获取成功"}
            except Exception as e:
                return {"success": False, "data": [], "message": f"查询失败: {str(e)}"}
    
    def get_member_by_id(self, member_id):
        """根据ID获取会员"""
        with DBConnection() as db:
            db.execute("SELECT * FROM member WHERE member_id = %s", (member_id,))
            member = db.fetchone()
            if member:
                member['level_display'] = self.LEVEL_DISPLAY.get(member['level_code'], member['level_code'])
                member['status_display'] = self.STATUS_DISPLAY.get(member['status'], member['status'])
                return {"success": True, "data": member, "message": "获取成功"}
            return {"success": False, "data": None, "message": "会员不存在"}
    
    def get_member_by_card(self, card_no):
        """根据卡号获取会员（收银台调用）"""
        with DBConnection() as db:
            sql = """
                SELECT m.*, mlr.discount_rate, mlr.points_rate
                FROM member m
                JOIN member_level_rule mlr ON m.level_code = mlr.level_code
                WHERE m.card_no = %s
            """
            db.execute(sql, (card_no,))
            member = db.fetchone()
            
            if not member:
                return {"success": False, "data": None, "message": "会员不存在"}
            
            if member['status'] == 'disabled':
                return {"success": False, "data": None, "message": "该会员已被禁用"}
            
            member['level_display'] = self.LEVEL_DISPLAY.get(member['level_code'], member['level_code'])
            return {"success": True, "data": member, "message": "查询成功"}
