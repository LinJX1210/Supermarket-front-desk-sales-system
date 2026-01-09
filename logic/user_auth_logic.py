# -*- coding: utf-8 -*-
"""
用户认证逻辑 - 组员3负责
"""

import hashlib
from db.db_conn import DBConnection


class UserAuthLogic:
    """用户认证业务逻辑"""
    
    ROLE_PERMISSIONS = {
        "admin": ["cashier", "goods", "member", "return", "statistics", "user_manage", "member_rule"],
        "cashier": ["cashier", "member"],
        "goods_manager": ["goods", "inventory"],
        "after_sale": ["return", "member"],
    }
    
    ROLE_DISPLAY = {
        "admin": "管理员",
        "cashier": "收银员",
        "goods_manager": "商品管理员",
        "after_sale": "售后",
    }
    
    def _md5(self, password):
        """MD5加密密码"""
        return hashlib.md5(password.encode()).hexdigest()
    
    def login_auth(self, username, password):
        """登录验证"""
        if not username or not password:
            return {"success": False, "data": None, "message": "用户名和密码不能为空"}
        
        with DBConnection() as db:
            sql = """
                SELECT user_id, username, real_name, phone, role, status
                FROM sys_user
                WHERE username = %s AND password = %s
            """
            db.execute(sql, (username, self._md5(password)))
            user = db.fetchone()
            
            if not user:
                return {"success": False, "data": None, "message": "用户名或密码错误"}
            
            if user['status'] == 'disabled':
                return {"success": False, "data": None, "message": "账号已被禁用，请联系管理员"}
            
            self._log_operation(db, user['user_id'], '用户登录')
            
            user['role_display'] = self.ROLE_DISPLAY.get(user['role'], user['role'])
            user['permissions'] = self.ROLE_PERMISSIONS.get(user['role'], [])
            
            return {"success": True, "data": user, "message": "登录成功"}
    
    def get_role_permission(self, role):
        """获取角色权限列表"""
        permissions = self.ROLE_PERMISSIONS.get(role, [])
        return {"success": True, "data": permissions, "message": "获取成功"}
    
    def check_permission(self, user_id, module):
        """检查用户是否有某模块权限"""
        with DBConnection() as db:
            db.execute("SELECT role FROM sys_user WHERE user_id = %s", (user_id,))
            user = db.fetchone()
            
            if not user:
                return {"success": False, "data": False, "message": "用户不存在"}
            
            permissions = self.ROLE_PERMISSIONS.get(user['role'], [])
            has_permission = module in permissions
            
            return {"success": True, "data": has_permission, "message": "有权限" if has_permission else "无权限"}
    
    def change_password(self, user_id, old_password, new_password):
        """修改密码"""
        if not new_password or len(new_password) < 6:
            return {"success": False, "data": None, "message": "新密码长度不能少于6位"}
        
        with DBConnection() as db:
            try:
                sql = "SELECT user_id FROM sys_user WHERE user_id = %s AND password = %s"
                db.execute(sql, (user_id, self._md5(old_password)))
                if not db.fetchone():
                    return {"success": False, "data": None, "message": "原密码错误"}
                
                db.execute("UPDATE sys_user SET password = %s WHERE user_id = %s", 
                          (self._md5(new_password), user_id))
                db.commit()
                return {"success": True, "data": None, "message": "密码修改成功"}
            except Exception as e:
                db.rollback()
                return {"success": False, "data": None, "message": f"修改失败: {str(e)}"}
    
    def _log_operation(self, db, user_id, operation):
        """记录操作日志"""
        try:
            sql = "INSERT INTO sys_user_log (user_id, operation) VALUES (%s, %s)"
            db.execute(sql, (user_id, operation))
            db.commit()
        except Exception:
            pass
