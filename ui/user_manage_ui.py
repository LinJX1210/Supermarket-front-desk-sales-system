# -*- coding: utf-8 -*-
"""
用户管理界面 - 组员3负责
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from logic.user_manage_logic import UserManageLogic

COLORS = {
    "primary": "#4A90D9",
    "primary_hover": "#357ABD",
    "card_bg": "#FFFFFF",
    "text_dark": "#2C3E50",
    "success": "#27AE60",
    "danger": "#E74C3C",
    "info": "#3498DB",
    "gray": "#95A5A6",
    "border": "#E0E0E0",
}

FONTS = {
    "title": ("微软雅黑", 16, "bold"),
    "subtitle": ("微软雅黑", 14, "bold"),
    "body": ("微软雅黑", 13),
}


class UserManageUI(ctk.CTkFrame):
    """用户管理界面"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.logic = UserManageLogic()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_toolbar()
        self._create_user_list()
        self._load_user_list()
    
    def _create_toolbar(self):
        """顶部工具栏"""
        toolbar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        ctk.CTkLabel(
            toolbar, text="用户管理", 
            font=FONTS["title"], 
            text_color=COLORS["text_dark"]
        ).pack(side="left", padx=20, pady=15)
        
        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(side="right", padx=20, pady=15)
        
        ctk.CTkButton(
            btn_frame, text="+ 新增用户", width=100, height=36,
            font=FONTS["body"], fg_color=COLORS["success"],
            hover_color="#219A52", command=self._add_user
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame, text="修改", width=80, height=36,
            font=FONTS["body"], fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"], command=self._edit_user
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame, text="禁用/启用", width=90, height=36,
            font=FONTS["body"], fg_color=COLORS["danger"],
            hover_color="#C0392B", command=self._disable_user
        ).pack(side="left")

    def _create_user_list(self):
        """用户列表区域"""
        list_card = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        list_card.grid(row=1, column=0, sticky="nsew")
        list_card.grid_rowconfigure(0, weight=1)
        list_card.grid_columnconfigure(0, weight=1)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=COLORS["text_dark"], 
                       rowheight=40, fieldbackground="white", font=("微软雅黑", 12))
        style.configure("Treeview.Heading", font=("微软雅黑", 12, "bold"), 
                       background="#F0F0F0", foreground=COLORS["text_dark"])
        style.map("Treeview", background=[("selected", COLORS["primary"])])
        
        columns = ("user_id", "username", "real_name", "role", "status", "create_time")
        self.tree = ttk.Treeview(list_card, columns=columns, show="headings", height=15)
        
        self.tree.heading("user_id", text="ID")
        self.tree.heading("username", text="账号")
        self.tree.heading("real_name", text="姓名")
        self.tree.heading("role", text="角色")
        self.tree.heading("status", text="状态")
        self.tree.heading("create_time", text="创建时间")
        
        self.tree.column("user_id", width=50, anchor="center")
        self.tree.column("username", width=120, anchor="center")
        self.tree.column("real_name", width=100, anchor="center")
        self.tree.column("role", width=120, anchor="center")
        self.tree.column("status", width=80, anchor="center")
        self.tree.column("create_time", width=160, anchor="center")
        
        self.tree.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=20, padx=(0, 10))
        self.tree.configure(yscrollcommand=scrollbar.set)
    
    def _load_user_list(self):
        """加载用户列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        result = self.logic.get_user_list()
        if result['success']:
            for user in result['data']:
                self.tree.insert("", "end", values=(
                    user['user_id'],
                    user['username'],
                    user['real_name'] or '',
                    user['role_display'],
                    user['status_display'],
                    user.get('create_time_str', '')
                ))
    
    def _get_selected_user(self):
        """获取选中的用户"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个用户")
            return None
        values = self.tree.item(selected[0])['values']
        return {'user_id': values[0], 'username': values[1], 'real_name': values[2], 
                'role': values[3], 'status': values[4]}
    
    def _add_user(self):
        """新增用户"""
        dialog = UserEditDialog(self, "新增用户")
        self.wait_window(dialog)
        if hasattr(dialog, 'result') and dialog.result:
            result = self.logic.add_user(**dialog.result)
            if result['success']:
                messagebox.showinfo("成功", result['message'])
                self._load_user_list()
            else:
                messagebox.showerror("失败", result['message'])
    
    def _edit_user(self):
        """修改用户"""
        user = self._get_selected_user()
        if not user:
            return
        
        result = self.logic.get_user_by_id(user['user_id'])
        if not result['success']:
            messagebox.showerror("错误", result['message'])
            return
        
        dialog = UserEditDialog(self, "修改用户", result['data'])
        self.wait_window(dialog)
        if hasattr(dialog, 'result') and dialog.result:
            result = self.logic.update_user(user['user_id'], dialog.result)
            if result['success']:
                messagebox.showinfo("成功", result['message'])
                self._load_user_list()
            else:
                messagebox.showerror("失败", result['message'])
    
    def _disable_user(self):
        """禁用/启用用户"""
        user = self._get_selected_user()
        if not user:
            return
        
        action = "启用" if user['status'] == "禁用" else "禁用"
        if not messagebox.askyesno("确认", f"确定要{action}用户 {user['username']} 吗？"):
            return
        
        result = self.logic.disable_user(user['user_id'])
        if result['success']:
            messagebox.showinfo("成功", result['message'])
            self._load_user_list()
        else:
            messagebox.showerror("失败", result['message'])


class UserEditDialog(ctk.CTkToplevel):
    """用户编辑弹窗"""
    
    def __init__(self, parent, title="新增用户", user_data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x520")
        self.resizable(False, False)
        
        self.user_data = user_data
        self.result = None
        
        self.transient(parent)
        self.grab_set()
        
        self._create_form()
        if user_data:
            self._fill_form(user_data)
    
    def _create_form(self):
        """创建表单"""
        form = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        form.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(form, text="账号 *", font=FONTS["body"], text_color=COLORS["text_dark"]).pack(anchor="w", padx=20, pady=(20, 5))
        self.username_entry = ctk.CTkEntry(form, height=38, font=FONTS["body"])
        self.username_entry.pack(fill="x", padx=20)
        
        pwd_label = "密码 *" if not self.user_data else "密码 (留空不修改)"
        ctk.CTkLabel(form, text=pwd_label, font=FONTS["body"], text_color=COLORS["text_dark"]).pack(anchor="w", padx=20, pady=(15, 5))
        self.password_entry = ctk.CTkEntry(form, height=38, font=FONTS["body"], show="*")
        self.password_entry.pack(fill="x", padx=20)
        
        ctk.CTkLabel(form, text="姓名", font=FONTS["body"], text_color=COLORS["text_dark"]).pack(anchor="w", padx=20, pady=(15, 5))
        self.realname_entry = ctk.CTkEntry(form, height=38, font=FONTS["body"])
        self.realname_entry.pack(fill="x", padx=20)
        
        ctk.CTkLabel(form, text="角色 *", font=FONTS["body"], text_color=COLORS["text_dark"]).pack(anchor="w", padx=20, pady=(15, 5))
        self.role_combo = ctk.CTkOptionMenu(form, height=38, font=FONTS["body"],
            values=["管理员", "收银员", "商品管理员", "售后"])
        self.role_combo.pack(fill="x", padx=20)
        
        btn_frame = ctk.CTkFrame(form, fg_color="transparent", height=50)
        btn_frame.pack(fill="x", padx=20, pady=25)
        btn_frame.pack_propagate(False)
        
        ctk.CTkButton(btn_frame, text="取消", width=140, height=40,
            font=FONTS["body"], fg_color=COLORS["gray"],
            command=self.destroy).pack(side="left", expand=True, padx=(0, 10), pady=5)
        
        ctk.CTkButton(btn_frame, text="保存", width=140, height=40,
            font=FONTS["body"], fg_color=COLORS["primary"],
            command=self._save).pack(side="left", expand=True, pady=5)
    
    def _fill_form(self, data):
        """填充表单数据"""
        self.username_entry.insert(0, data.get('username', ''))
        self.realname_entry.insert(0, data.get('real_name', '') or '')
        role_display = data.get('role_display', '收银员')
        self.role_combo.set(role_display)
    
    def _save(self):
        """保存用户"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        real_name = self.realname_entry.get().strip()
        role = self.role_combo.get()
        
        if not username:
            messagebox.showwarning("提示", "请输入账号")
            return
        
        if not self.user_data and not password:
            messagebox.showwarning("提示", "请输入密码")
            return
        
        if not self.user_data and len(password) < 6:
            messagebox.showwarning("提示", "密码长度不能少于6位")
            return
        
        self.result = {
            'username': username,
            'password': password if password else None,
            'real_name': real_name,
            'phone': '',
            'role': role
        }
        self.destroy()
