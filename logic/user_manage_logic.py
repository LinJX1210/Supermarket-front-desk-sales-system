# -*- coding: utf-8 -*-
"""
用户管理逻辑 - 组员3负责
"""

import hashlib
from db.db_conn import DBConnection


class UserManageLogic:
    """用户管理业务逻辑"""
    
    ROLE_MAP = {
        "管理员": "admin",
        "收银员": "cashier",
        "商品管理员": "goods_manager",
        "售后": "after_sale",
    }
    
    ROLE_DISPLAY = {v: k for k, v in ROLE_MAP.items()}
    
    STATUS_DISPLAY = {
        "active": "正常",
        "disabled": "禁用",
    }
    
    def _md5(self, password):
        """MD5加密密码"""
        return hashlib.md5(password.encode()).hexdigest()
    
    def add_user(self, username, password, real_name, phone, role):
        """新增用户"""
        if not username or not password:
            return {"success": False, "data": None, "message": "用户名和密码不能为空"}
        
        if len(password) < 6:
            return {"success": False, "data": None, "message": "密码长度不能少于6位"}
        
        with DBConnection() as db:
            try:
                db.execute("SELECT user_id FROM sys_user WHERE username = %s", (username,))
                if db.fetchone():
                    return {"success": False, "data": None, "message": "用户名已存在"}
                
                role_code = self.ROLE_MAP.get(role, role)
                
                sql = """
                    INSERT INTO sys_user (username, password, real_name, phone, role, status)
                    VALUES (%s, %s, %s, %s, %s, 'active')
                """
                db.execute(sql, (username, self._md5(password), real_name or '', phone or '', role_code))
                db.commit()
                
                user_id = db.cursor.lastrowid
                return {"success": True, "data": user_id, "message": "用户添加成功"}
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"添加失败: {str(e)}"}
    
    def update_user(self, user_id, data):
        """修改用户"""
        with DBConnection() as db:
            try:
                db.execute("SELECT user_id FROM sys_user WHERE user_id = %s", (user_id,))
                if not db.fetchone():
                    return {"success": False, "data": None, "message": "用户不存在"}
                
                if data.get('username'):
                    db.execute("SELECT user_id FROM sys_user WHERE username = %s AND user_id != %s",
                              (data['username'], user_id))
                    if db.fetchone():
                        return {"success": False, "data": None, "message": "用户名已被占用"}
                
                role_code = self.ROLE_MAP.get(data.get('role'), data.get('role'))
                
                if data.get('password'):
                    sql = """
                        UPDATE sys_user 
                        SET username=%s, password=%s, real_name=%s, phone=%s, role=%s
                        WHERE user_id=%s
                    """
                    db.execute(sql, (
                        data.get('username'), self._md5(data['password']),
                        data.get('real_name', ''), data.get('phone', ''),
                        role_code, user_id
                    ))
                else:
                    sql = """
                        UPDATE sys_user 
                        SET username=%s, real_name=%s, phone=%s, role=%s
                        WHERE user_id=%s
                    """
                    db.execute(sql, (
                        data.get('username'), data.get('real_name', ''),
                        data.get('phone', ''), role_code, user_id
                    ))
                
                db.commit()
                return {"success": True, "data": None, "message": "用户修改成功"}
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"修改失败: {str(e)}"}

    def disable_user(self, user_id):
        """禁用/启用用户"""
        with DBConnection() as db:
            try:
                db.execute("SELECT status FROM sys_user WHERE user_id = %s", (user_id,))
                user = db.fetchone()
                if not user:
                    return {"success": False, "data": None, "message": "用户不存在"}
                
                new_status = 'disabled' if user['status'] == 'active' else 'active'
                db.execute("UPDATE sys_user SET status = %s WHERE user_id = %s", (new_status, user_id))
                db.commit()
                
                status_text = "禁用" if new_status == 'disabled' else "启用"
                return {"success": True, "data": new_status, "message": f"用户已{status_text}"}
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"操作失败: {str(e)}"}
    
    def get_user_list(self, filters=None):
        """获取用户列表"""
        filters = filters or {}
        
        with DBConnection() as db:
            try:
                sql = """
                    SELECT user_id, username, real_name, phone, role, status, create_time
                    FROM sys_user WHERE 1=1
                """
                params = []
                
                if filters.get('role'):
                    role_code = self.ROLE_MAP.get(filters['role'], filters['role'])
                    sql += " AND role = %s"
                    params.append(role_code)
                
                if filters.get('status'):
                    status_code = 'active' if filters['status'] == '正常' else 'disabled'
                    sql += " AND status = %s"
                    params.append(status_code)
                
                if filters.get('keyword'):
                    sql += " AND (username LIKE %s OR real_name LIKE %s)"
                    keyword = f"%{filters['keyword']}%"
                    params.extend([keyword, keyword])
                
                sql += " ORDER BY create_time DESC"
                db.execute(sql, params)
                users = db.fetchall()
                
                for user in users:
                    user['role_display'] = self.ROLE_DISPLAY.get(user['role'], user['role'])
                    user['status_display'] = self.STATUS_DISPLAY.get(user['status'], user['status'])
                    if user['create_time']:
                        user['create_time_str'] = user['create_time'].strftime('%Y-%m-%d %H:%M')
                
                return {"success": True, "data": users, "message": "获取成功"}
            except Exception as e:
                return {"success": False, "data": [], "message": f"查询失败: {str(e)}"}
    
    def get_user_by_id(self, user_id):
        """根据ID获取用户"""
        with DBConnection() as db:
            db.execute("SELECT * FROM sys_user WHERE user_id = %s", (user_id,))
            user = db.fetchone()
            if user:
                user['role_display'] = self.ROLE_DISPLAY.get(user['role'], user['role'])
                return {"success": True, "data": user, "message": "获取成功"}
            return {"success": False, "data": None, "message": "用户不存在"}
