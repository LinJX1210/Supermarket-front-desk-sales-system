# -*- coding: utf-8 -*-
"""
系统通知逻辑 - 组员1负责
"""

from db.db_conn import DBConnection


class NotificationLogic:
    """系统通知业务逻辑"""
    
    NOTIFICATION_TYPES = {
        "stock_warning": "库存预警",
        "quality_feedback": "质量反馈",
        "member_upgrade": "会员升级",
        "member_downgrade": "会员降级",
        "system": "系统通知",
    }
    
    def create_notification(self, target_user_id, target_role, notification_type, title, content, related_id=None):
        """
        创建通知
        :param target_user_id: 目标用户ID（为空则按角色广播）
        :param target_role: 目标角色
        :param notification_type: 通知类型
        :param title: 通知标题
        :param content: 通知内容
        :param related_id: 关联业务ID
        """
        try:
            with DBConnection() as db:
                sql = """
                    INSERT INTO sys_notification 
                    (target_user_id, target_role, notification_type, title, content, related_id, is_read, create_time)
                    VALUES (%s, %s, %s, %s, %s, %s, 0, NOW())
                """
                db.execute(sql, (target_user_id, target_role, notification_type, title, content, related_id))
                db.commit()
                return {"success": True, "data": None, "message": "通知创建成功"}
        except Exception as e:
            return {"success": False, "data": None, "message": f"创建通知失败: {str(e)}"}
    
    def get_unread_count(self, user_id, role):
        """
        获取未读通知数量
        :param user_id: 用户ID
        :param role: 用户角色
        """
        try:
            with DBConnection() as db:
                # 简化查询：获取所有未读通知（target_role匹配或为空，target_user_id匹配或为空）
                sql = """
                    SELECT COUNT(*) as count FROM sys_notification 
                    WHERE is_read = 0 
                    AND (target_role = %s OR target_role IS NULL OR target_role = '')
                    AND (target_user_id = %s OR target_user_id IS NULL)
                """
                db.execute(sql, (role, user_id))
                result = db.fetchone()
                return {"success": True, "data": result["count"] if result else 0, "message": "获取成功"}
        except Exception as e:
            return {"success": False, "data": 0, "message": f"获取失败: {str(e)}"}
    
    def get_notifications(self, user_id, role, limit=20):
        """
        获取通知列表
        :param user_id: 用户ID
        :param role: 用户角色
        :param limit: 返回数量限制
        """
        try:
            with DBConnection() as db:
                sql = """
                    SELECT notification_id, notification_type, title, content, 
                           is_read, create_time, read_time
                    FROM sys_notification 
                    WHERE (target_role = %s OR target_role IS NULL OR target_role = '')
                    AND (target_user_id = %s OR target_user_id IS NULL)
                    ORDER BY create_time DESC
                    LIMIT %s
                """
                db.execute(sql, (role, user_id, limit))
                notifications = db.fetchall()
                
                for n in notifications:
                    n["type_display"] = self.NOTIFICATION_TYPES.get(n["notification_type"], n["notification_type"])
                    if n["create_time"]:
                        n["create_time_str"] = n["create_time"].strftime("%Y-%m-%d %H:%M")
                
                return {"success": True, "data": notifications, "message": "获取成功"}
        except Exception as e:
            return {"success": False, "data": [], "message": f"获取失败: {str(e)}"}
    
    def mark_as_read(self, notification_id):
        """标记通知为已读"""
        try:
            with DBConnection() as db:
                sql = "UPDATE sys_notification SET is_read = 1, read_time = NOW() WHERE notification_id = %s"
                db.execute(sql, (notification_id,))
                db.commit()
                return {"success": True, "data": None, "message": "标记成功"}
        except Exception as e:
            return {"success": False, "data": None, "message": f"标记失败: {str(e)}"}
    
    def mark_all_as_read(self, user_id, role):
        """标记所有通知为已读"""
        try:
            with DBConnection() as db:
                sql = """
                    UPDATE sys_notification SET is_read = 1, read_time = NOW() 
                    WHERE is_read = 0 
                    AND (target_role = %s OR target_role IS NULL OR target_role = '')
                    AND (target_user_id = %s OR target_user_id IS NULL)
                """
                db.execute(sql, (role, user_id))
                db.commit()
                return {"success": True, "data": None, "message": "全部标记成功"}
        except Exception as e:
            return {"success": False, "data": None, "message": f"标记失败: {str(e)}"}
