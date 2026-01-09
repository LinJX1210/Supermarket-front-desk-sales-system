# -*- coding: utf-8 -*-
"""
会员管理界面 - 组员3负责
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from logic.member_manage_logic import MemberManageLogic

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


class MemberManageUI(ctk.CTkFrame):
    """会员管理界面"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.logic = MemberManageLogic()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._create_toolbar()
        self._create_member_list()
        self._load_member_list()
    
    def _create_toolbar(self):
        """顶部工具栏"""
        toolbar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        ctk.CTkLabel(toolbar, text="会员管理", font=FONTS["title"], 
                    text_color=COLORS["text_dark"]).pack(side="left", padx=20, pady=15)
        
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="left", padx=30)
        
        self.search_entry = ctk.CTkEntry(search_frame, width=220, height=36,
            placeholder_text="输入卡号或手机号查询", font=FONTS["body"])
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._search_member())
        
        ctk.CTkButton(search_frame, text="查询", width=80, height=36,
            font=FONTS["body"], fg_color=COLORS["info"],
            command=self._search_member).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(search_frame, text="刷新", width=60, height=36,
            font=FONTS["body"], fg_color=COLORS["gray"],
            command=self._load_member_list).pack(side="left")
        
        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(side="right", padx=20, pady=15)
        
        ctk.CTkButton(btn_frame, text="+ 新增会员", width=100, height=36,
            font=FONTS["body"], fg_color=COLORS["success"],
            command=self._add_member).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(btn_frame, text="修改", width=80, height=36,
            font=FONTS["body"], fg_color=COLORS["primary"],
            command=self._edit_member).pack(side="left")

    def _create_member_list(self):
        """会员列表区域"""
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
        
        columns = ("member_id", "card_no", "name", "phone", "level", "total_consume", "total_points", "status")
        self.tree = ttk.Treeview(list_card, columns=columns, show="headings", height=15)
        
        self.tree.heading("member_id", text="ID")
        self.tree.heading("card_no", text="卡号")
        self.tree.heading("name", text="姓名")
        self.tree.heading("phone", text="手机号")
        self.tree.heading("level", text="级别")
        self.tree.heading("total_consume", text="累计消费")
        self.tree.heading("total_points", text="积分")
        self.tree.heading("status", text="状态")
        
        self.tree.column("member_id", width=50, anchor="center")
        self.tree.column("card_no", width=130, anchor="center")
        self.tree.column("name", width=80, anchor="center")
        self.tree.column("phone", width=120, anchor="center")
        self.tree.column("level", width=80, anchor="center")
        self.tree.column("total_consume", width=100, anchor="center")
        self.tree.column("total_points", width=70, anchor="center")
        self.tree.column("status", width=60, anchor="center")
        
        self.tree.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=20, padx=(0, 10))
        self.tree.configure(yscrollcommand=scrollbar.set)
    
    def _load_member_list(self):
        """加载会员列表"""
        self.search_entry.delete(0, "end")
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        result = self.logic.get_member_list()
        if result['success']:
            self._fill_tree(result['data'])
    
    def _fill_tree(self, members):
        """填充列表数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for member in members:
            self.tree.insert("", "end", values=(
                member['member_id'], member['card_no'], member['name'],
                member['phone'] or '', member['level_display'],
                member['total_consume_str'], member['total_points'], member['status_display']
            ))
    
    def _get_selected_member(self):
        """获取选中的会员"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个会员")
            return None
        values = self.tree.item(selected[0])['values']
        return {'member_id': values[0], 'card_no': values[1], 'name': values[2]}
    
    def _search_member(self):
        """查询会员"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            self._load_member_list()
            return
        result = self.logic.query_member(keyword)
        if result['success']:
            self._fill_tree(result['data'])
            if not result['data']:
                messagebox.showinfo("提示", "未找到匹配的会员")
        else:
            messagebox.showerror("错误", result['message'])
    
    def _add_member(self):
        """新增会员"""
        dialog = MemberEditDialog(self, "新增会员")
        self.wait_window(dialog)
        if hasattr(dialog, 'result') and dialog.result:
            result = self.logic.register_member(
                name=dialog.result['name'],
                phone=dialog.result['phone'],
                address=dialog.result['address']
            )
            if result['success']:
                messagebox.showinfo("成功", result['message'])
                self._load_member_list()
            else:
                messagebox.showerror("失败", result['message'])
    
    def _edit_member(self):
        """修改会员"""
        member = self._get_selected_member()
        if not member:
            return
        result = self.logic.get_member_by_id(member['member_id'])
        if not result['success']:
            messagebox.showerror("错误", result['message'])
            return
        dialog = MemberEditDialog(self, "修改会员", result['data'])
        self.wait_window(dialog)
        if hasattr(dialog, 'result') and dialog.result:
            result = self.logic.update_member(member['member_id'], dialog.result)
            if result['success']:
                messagebox.showinfo("成功", result['message'])
                self._load_member_list()
            else:
                messagebox.showerror("失败", result['message'])


class MemberEditDialog(ctk.CTkToplevel):
    """会员编辑弹窗"""
    
    def __init__(self, parent, title="新增会员", member_data=None):
        super().__init__(parent)
        self.title(title)
        self.member_data = member_data
        self.result = None
        
        # 根据是否有会员数据调整窗口高度
        height = 500 if member_data else 350
        self.geometry(f"400x{height}")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self._create_form()
        if member_data:
            self._fill_form(member_data)
    
    def _create_form(self):
        """创建表单"""
        form = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        form.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(form, text="姓名 *", font=FONTS["body"], 
                    text_color=COLORS["text_dark"]).pack(anchor="w", padx=20, pady=(20, 5))
        self.name_entry = ctk.CTkEntry(form, height=38, font=FONTS["body"])
        self.name_entry.pack(fill="x", padx=20)
        
        ctk.CTkLabel(form, text="手机号", font=FONTS["body"], 
                    text_color=COLORS["text_dark"]).pack(anchor="w", padx=20, pady=(15, 5))
        self.phone_entry = ctk.CTkEntry(form, height=38, font=FONTS["body"])
        self.phone_entry.pack(fill="x", padx=20)
        
        if self.member_data:
            ctk.CTkLabel(form, text="会员级别", font=FONTS["body"], 
                        text_color=COLORS["text_dark"]).pack(anchor="w", padx=20, pady=(15, 5))
            self.level_combo = ctk.CTkOptionMenu(form, height=38, font=FONTS["body"],
                values=["普通会员", "银卡会员", "金卡会员"])
            self.level_combo.pack(fill="x", padx=20)
            
            ctk.CTkLabel(form, text="状态", font=FONTS["body"], 
                        text_color=COLORS["text_dark"]).pack(anchor="w", padx=20, pady=(15, 5))
            self.status_combo = ctk.CTkOptionMenu(form, height=38, font=FONTS["body"],
                values=["正常", "禁用"])
            self.status_combo.pack(fill="x", padx=20)
        
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
        self.name_entry.insert(0, data.get('name', ''))
        self.phone_entry.insert(0, data.get('phone', '') or '')
        if hasattr(self, 'level_combo'):
            self.level_combo.set(data.get('level_display', '普通会员'))
        if hasattr(self, 'status_combo'):
            self.status_combo.set(data.get('status_display', '正常'))
    
    def _save(self):
        """保存会员"""
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not name:
            messagebox.showwarning("提示", "请输入会员姓名")
            return
        
        self.result = {'name': name, 'phone': phone, 'address': ''}
        
        if self.member_data:
            self.result['level'] = self.level_combo.get()
            self.result['status'] = self.status_combo.get()
        
        self.destroy()
