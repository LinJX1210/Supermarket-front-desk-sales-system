# -*- coding: utf-8 -*-
"""
登录界面 - 组员3负责
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import messagebox
from logic.user_auth_logic import UserAuthLogic

# 统一风格配置
COLORS = {
    "primary": "#4A90D9",
    "primary_hover": "#357ABD",
    "card_bg": "#FFFFFF",
    "text_dark": "#2C3E50",
    "text_gray": "#7F8C8D",
    "bg": "#F5F7FA",
}

FONTS = {
    "title": ("微软雅黑", 24, "bold"),
    "subtitle": ("微软雅黑", 14),
    "body": ("微软雅黑", 13),
}


class LoginUI(ctk.CTk):
    """登录界面"""
    
    def __init__(self):
        super().__init__()
        
        self.title("超市前台销售系统 - 登录")
        self.geometry("400x500")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.logic = UserAuthLogic()
        self.current_user = None
        
        self._center_window()
        self._create_ui()
    
    def _center_window(self):
        """窗口居中"""
        self.update_idletasks()
        width = 400
        height = 500
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_ui(self):
        """创建界面"""
        self.configure(fg_color=COLORS["bg"])
        
        # 主卡片
        card = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=15)
        card.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Logo区域
        logo_frame = ctk.CTkFrame(card, fg_color="transparent")
        logo_frame.pack(pady=(40, 20))
        
        ctk.CTkLabel(logo_frame, text="🛒", font=("微软雅黑", 48)).pack()
        
        ctk.CTkLabel(
            logo_frame, text="超市前台销售系统",
            font=FONTS["title"], text_color=COLORS["text_dark"]
        ).pack(pady=(10, 0))
        
        ctk.CTkLabel(
            logo_frame, text="Supermarket Front-end Sales System",
            font=("微软雅黑", 10), text_color=COLORS["text_gray"]
        ).pack()
        
        # 表单区域
        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(fill="x", padx=40, pady=30)
        
        # 用户名
        ctk.CTkLabel(
            form_frame, text="用户名", 
            font=FONTS["body"], text_color=COLORS["text_dark"]
        ).pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            form_frame, height=42, font=FONTS["body"],
            placeholder_text="请输入用户名"
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        
        # 密码
        ctk.CTkLabel(
            form_frame, text="密码", 
            font=FONTS["body"], text_color=COLORS["text_dark"]
        ).pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_frame, height=42, font=FONTS["body"],
            placeholder_text="请输入密码", show="●"
        )
        self.password_entry.pack(fill="x", pady=(0, 25))
        self.password_entry.bind("<Return>", lambda e: self._login())
        
        # 登录按钮
        self.login_btn = ctk.CTkButton(
            form_frame, text="登 录", height=45,
            font=("微软雅黑", 15, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._login
        )
        self.login_btn.pack(fill="x")
        
        # 提示信息
        ctk.CTkLabel(
            card, text="默认管理员账号: admin / 123456",
            font=("微软雅黑", 10), text_color=COLORS["text_gray"]
        ).pack(pady=(0, 20))
        
        self.username_entry.focus()
    
    def _login(self):
        """登录验证"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username:
            messagebox.showwarning("提示", "请输入用户名")
            self.username_entry.focus()
            return
        
        if not password:
            messagebox.showwarning("提示", "请输入密码")
            self.password_entry.focus()
            return
        
        self.login_btn.configure(state="disabled", text="登录中...")
        self.update()
        
        result = self.logic.login_auth(username, password)
        
        if result['success']:
            self.current_user = result['data']
            self.destroy()
            self._open_main_window()
        else:
            self.login_btn.configure(state="normal", text="登 录")
            messagebox.showerror("登录失败", result['message'])
            self.password_entry.delete(0, "end")
            self.password_entry.focus()
    
    def _open_main_window(self):
        """打开主窗口"""
        from ui.main_ui import MainApp
        app = MainApp(self.current_user)
        app.mainloop()


if __name__ == "__main__":
    app = LoginUI()
    app.mainloop()
