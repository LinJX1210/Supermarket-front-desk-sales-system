# -*- coding: utf-8 -*-
"""
系统主界面 - 组员1负责
统一UI风格参考模板（浅色主题）
"""

import customtkinter as ctk
from logic.notification_logic import NotificationLogic

# ==================== 统一UI风格配置（其他组员请参考） ====================
COLORS = {
    "primary": "#4A90D9",       # 主色调-蓝色
    "primary_hover": "#357ABD",
    "sidebar_bg": "#2C3E50",    # 侧边栏-深蓝灰
    "sidebar_hover": "#34495E",
    "content_bg": "#F5F7FA",    # 内容区-浅灰白
    "card_bg": "#FFFFFF",       # 卡片背景-白色
    "text_dark": "#2C3E50",     # 深色文字
    "text_light": "#FFFFFF",    # 浅色文字
    "success": "#27AE60",       # 成功-绿色
    "warning": "#F39C12",       # 警告-橙色
    "danger": "#E74C3C",        # 危险-红色
    "info": "#3498DB",          # 信息-蓝色
    "gray": "#95A5A6",          # 灰色
}

FONTS = {
    "title": ("微软雅黑", 16, "bold"),
    "body": ("微软雅黑", 13),
    "button": ("微软雅黑", 13),
}


class MainApp(ctk.CTk):
    """主应用程序窗口"""
    
    def __init__(self, user_info=None):
        super().__init__()
        
        self.title("超市前台销售系统")
        self.geometry("1200x800")
        
        # 使用浅色主题
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # 接收登录用户信息
        self.current_user = user_info or {"username": "admin", "role": "admin", "role_display": "管理员", "permissions": ["cashier", "goods", "member", "return", "statistics", "user_manage"]}
        self.current_frame = None
        
        self._create_layout()
        self._show_cashier()
    
    def _create_layout(self):
        """创建布局"""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 左侧导航栏（深色）
        sidebar = ctk.CTkFrame(self, width=180, fg_color=COLORS["sidebar_bg"], corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Logo
        ctk.CTkLabel(
            sidebar, text="🛒 超市系统", 
            font=("微软雅黑", 18, "bold"),
            text_color=COLORS["text_light"]
        ).pack(pady=30)
        
        # 导航按钮（根据权限显示）
        permissions = self.current_user.get('permissions', [])
        
        nav_items = [
            ("💰 收银台", self._show_cashier, "cashier"),
            ("📦 商品管理", self._show_goods, "goods"),
            ("📊 库存监控", self._show_inventory, "goods"),
            ("👥 会员管理", self._show_member, "member"),
            ("⭐ 会员规则", self._show_member_rule, "member"),
            ("↩️ 退货处理", self._show_return, "return"),
            ("📋 退货查询", self._show_return_query, "return"),
            ("📈 统计报表", self._show_statistics, "statistics"),
            ("👤 用户管理", self._show_user_manage, "user_manage"),
        ]
        for text, cmd, perm in nav_items:
            # 管理员显示所有，其他角色按权限显示
            if self.current_user.get('role') == 'admin' or perm in permissions:
                ctk.CTkButton(
                    sidebar, text=text, font=FONTS["button"],
                    fg_color="transparent", 
                    hover_color=COLORS["sidebar_hover"],
                    text_color=COLORS["text_light"],
                    anchor="w", height=45, command=cmd
                ).pack(fill="x", padx=10, pady=3)
        
        # 底部用户信息
        user_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        user_frame.pack(side="bottom", fill="x", padx=10, pady=20)
        
        # 通知按钮容器（用于显示小红点）
        self.notification_logic = NotificationLogic()
        
        notification_container = ctk.CTkFrame(user_frame, fg_color="transparent")
        notification_container.pack(fill="x", pady=(0, 10))
        
        self.notification_btn = ctk.CTkButton(
            notification_container, text="🔔 通知", font=("微软雅黑", 11),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color=COLORS["text_light"], height=32,
            command=self._show_notifications
        )
        self.notification_btn.pack(fill="x")
        
        # 小红点标签（放在按钮右上角内侧）
        self.badge_label = ctk.CTkLabel(
            notification_container, text="", font=("微软雅黑", 9, "bold"),
            fg_color=COLORS["danger"], text_color=COLORS["text_light"],
            corner_radius=10, width=20, height=20
        )
        # 初始隐藏小红点
        self.badge_label.place_forget()
        
        # 定时刷新未读数量
        self._refresh_notification_count()
        
        ctk.CTkLabel(
            user_frame, text=f"👤 {self.current_user.get('real_name') or self.current_user.get('username')}",
            font=("微软雅黑", 11), text_color=COLORS["text_light"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            user_frame, text=f"角色: {self.current_user.get('role_display', '管理员')}",
            font=("微软雅黑", 10), text_color=COLORS["gray"]
        ).pack(anchor="w")
        
        # 右侧内容区（浅色）
        self.content = ctk.CTkFrame(self, fg_color=COLORS["content_bg"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
    
    def _switch_frame(self, frame_class, **kwargs):
        """切换内容区"""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.content, **kwargs)
        self.current_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    
    def _show_cashier(self):
        from ui.cashier_ui import CashierUI
        self._switch_frame(CashierUI, user_info=self.current_user)
    
    def _show_goods(self):
        from ui.goods_manage_ui import GoodsManageUI
        self._switch_frame(GoodsManageUI)
    
    def _show_member(self):
        from ui.member_manage_ui import MemberManageUI
        self._switch_frame(MemberManageUI)
    
    def _show_return(self):
        from ui.return_handle_ui import ReturnHandleUI
        self._switch_frame(ReturnHandleUI)
    
    def _show_statistics(self):
        from ui.statistics_ui import StatisticsUI
        self._switch_frame(StatisticsUI)

    def _show_user_manage(self):
        from ui.user_manage_ui import UserManageUI
        self._switch_frame(UserManageUI)
    
    def _show_member_rule(self):
        from ui.member_rule_ui import MemberRuleUI
        self._switch_frame(MemberRuleUI)
    
    def _show_return_query(self):
        from ui.return_query_ui import ReturnQueryUI
        self._switch_frame(ReturnQueryUI)
    
    def _show_category(self):
        from ui.goods_category_ui import GoodsCategoryUI
        self._switch_frame(GoodsCategoryUI)
    
    def _show_inventory(self):
        from ui.inventory_monitor_ui import InventoryMonitorUI
        self._switch_frame(InventoryMonitorUI)
    
    def _show_query(self):
        from ui.query_comprehensive_ui import QueryComprehensiveUI
        self._switch_frame(QueryComprehensiveUI)
    
    def _refresh_notification_count(self):
        """刷新未读通知数量"""
        try:
            user_id = self.current_user.get('user_id')
            role = self.current_user.get('role')
            result = self.notification_logic.get_unread_count(user_id, role)
            count = result.get('data', 0) if result.get('success') else 0
            
            if count > 0:
                # 显示小红点（调整位置到按钮内部右上角）
                self.badge_label.configure(text=str(count) if count < 100 else "99+")
                self.badge_label.place(relx=1.0, rely=0, x=-30, y=2)
                self.notification_btn.configure(fg_color=COLORS["warning"])
            else:
                # 隐藏小红点
                self.badge_label.place_forget()
                self.notification_btn.configure(fg_color=COLORS["primary"])
        except:
            pass
        
        # 每30秒刷新一次
        self.after(30000, self._refresh_notification_count)
    
    def _show_notifications(self):
        """显示通知弹窗"""
        NotificationDialog(self, self.current_user, self.notification_logic, self._refresh_notification_count)


class NotificationDialog(ctk.CTkToplevel):
    """通知弹窗"""
    
    def __init__(self, parent, user_info, notification_logic, refresh_callback):
        super().__init__(parent)
        
        self.title("系统通知")
        self.geometry("500x450")
        self.resizable(False, False)
        
        self.user_info = user_info
        self.notification_logic = notification_logic
        self.refresh_callback = refresh_callback
        
        # 居中显示
        self.transient(parent)
        self.grab_set()
        
        self._create_ui()
        self._load_notifications()
    
    def _create_ui(self):
        """创建UI"""
        # 标题栏
        header = ctk.CTkFrame(self, fg_color=COLORS["primary"], corner_radius=0, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="🔔 系统通知", font=("微软雅黑", 14, "bold"),
                     text_color=COLORS["text_light"]).pack(side="left", padx=15, pady=10)
        
        ctk.CTkButton(header, text="全部已读", font=("微软雅黑", 11), width=80, height=28,
                      fg_color=COLORS["text_light"], text_color=COLORS["primary"],
                      hover_color="#E0E0E0", command=self._mark_all_read).pack(side="right", padx=15, pady=10)
        
        # 通知列表区域
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS["content_bg"])
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 空状态提示
        self.empty_label = ctk.CTkLabel(self.list_frame, text="暂无通知", 
                                         font=("微软雅黑", 13), text_color=COLORS["gray"])
    
    def _load_notifications(self):
        """加载通知列表"""
        # 清空现有内容
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        user_id = self.user_info.get('user_id')
        role = self.user_info.get('role')
        result = self.notification_logic.get_notifications(user_id, role)
        
        if not result.get('success') or not result.get('data'):
            self.empty_label = ctk.CTkLabel(self.list_frame, text="暂无通知", 
                                             font=("微软雅黑", 13), text_color=COLORS["gray"])
            self.empty_label.pack(pady=50)
            return
        
        for notification in result['data']:
            self._create_notification_card(notification)
    
    def _create_notification_card(self, notification):
        """创建单条通知卡片"""
        is_read = notification.get('is_read', 0)
        bg_color = COLORS["card_bg"] if is_read else "#E8F4FD"
        
        card = ctk.CTkFrame(self.list_frame, fg_color=bg_color, corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)
        
        # 内容区
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=12, pady=10)
        
        # 标题行
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.pack(fill="x")
        
        type_display = notification.get('type_display', '通知')
        ctk.CTkLabel(title_frame, text=f"[{type_display}]", font=("微软雅黑", 11),
                     text_color=COLORS["primary"]).pack(side="left")
        
        ctk.CTkLabel(title_frame, text=notification.get('title', ''), font=("微软雅黑", 12, "bold"),
                     text_color=COLORS["text_dark"]).pack(side="left", padx=(5, 0))
        
        if not is_read:
            ctk.CTkLabel(title_frame, text="●", font=("微软雅黑", 10),
                         text_color=COLORS["danger"]).pack(side="right")
        
        # 内容
        ctk.CTkLabel(content_frame, text=notification.get('content', ''), font=("微软雅黑", 11),
                     text_color=COLORS["gray"], wraplength=420, anchor="w", justify="left").pack(fill="x", pady=(5, 0))
        
        # 时间
        ctk.CTkLabel(content_frame, text=notification.get('create_time_str', ''), font=("微软雅黑", 10),
                     text_color=COLORS["gray"]).pack(anchor="e", pady=(5, 0))
        
        # 点击标记已读
        if not is_read:
            notification_id = notification.get('notification_id')
            card.bind("<Button-1>", lambda e, nid=notification_id: self._mark_read(nid))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, nid=notification_id: self._mark_read(nid))
    
    def _mark_read(self, notification_id):
        """标记单条已读"""
        self.notification_logic.mark_as_read(notification_id)
        self._load_notifications()
        self.refresh_callback()
    
    def _mark_all_read(self):
        """标记全部已读"""
        user_id = self.user_info.get('user_id')
        role = self.user_info.get('role')
        self.notification_logic.mark_all_as_read(user_id, role)
        self._load_notifications()
        self.refresh_callback()


# 单独运行测试
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
