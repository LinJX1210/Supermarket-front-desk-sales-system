# -*- coding: utf-8 -*-
"""
系统主界面 - 组员1负责
统一UI风格参考模板（浅色主题）
"""

import customtkinter as ctk

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
    "title": ("Microsoft YaHei UI", 16, "bold"),
    "body": ("Microsoft YaHei UI", 13),
    "button": ("Microsoft YaHei UI", 13),
}


class MainApp(ctk.CTk):
    """主应用程序窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.title("超市前台销售系统")
        self.geometry("1200x700")
        
        # 使用浅色主题
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.current_user = {"username": "admin", "role": "管理员"}
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
            font=("Microsoft YaHei UI", 18, "bold"),
            text_color=COLORS["text_light"]
        ).pack(pady=30)
        
        # 导航按钮
        nav_items = [
            ("💰 收银台", self._show_cashier),
            ("📦 商品管理", self._show_goods),
            ("👥 会员管理", self._show_member),
            ("↩️ 退货处理", self._show_return),
            ("📊 统计报表", self._show_statistics),
        ]
        for text, cmd in nav_items:
            ctk.CTkButton(
                sidebar, text=text, font=FONTS["button"],
                fg_color="transparent", 
                hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["text_light"],
                anchor="w", height=45, command=cmd
            ).pack(fill="x", padx=10, pady=3)
        
        # 右侧内容区（浅色）
        self.content = ctk.CTkFrame(self, fg_color=COLORS["content_bg"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
    
    def _switch_frame(self, frame_class):
        """切换内容区"""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.content)
        self.current_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    
    def _show_cashier(self):
        from ui.cashier_ui import CashierUI
        self._switch_frame(CashierUI)
    
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
