# -*- coding: utf-8 -*-
"""
收银界面 - 组员1负责
UI参考模板（浅色主题）
"""

import customtkinter as ctk
from tkinter import ttk

# 统一风格配置
COLORS = {
    "primary": "#4A90D9",
    "card_bg": "#FFFFFF",
    "text_dark": "#2C3E50",
    "success": "#27AE60",
    "danger": "#E74C3C",
    "info": "#3498DB",
    "gray": "#95A5A6",
    "border": "#E0E0E0",
}

FONTS = {
    "title": ("Microsoft YaHei UI", 16, "bold"),
    "subtitle": ("Microsoft YaHei UI", 14, "bold"),
    "body": ("Microsoft YaHei UI", 13),
    "price": ("Microsoft YaHei UI", 24, "bold"),
}


class CashierUI(ctk.CTkFrame):
    """收银界面"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_left_panel()
        self._create_right_panel()
    
    def _create_left_panel(self):
        """左侧面板：条码输入 + 商品列表"""
        left = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)
        
        # 条码输入区
        input_frame = ctk.CTkFrame(left, fg_color="transparent")
        input_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        ctk.CTkLabel(input_frame, text="商品条码", font=FONTS["subtitle"], text_color=COLORS["text_dark"]).pack(anchor="w")
        
        entry_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        entry_row.pack(fill="x", pady=(8, 0))
        
        self.barcode_entry = ctk.CTkEntry(
            entry_row, height=40, 
            placeholder_text="扫码枪扫描或手动输入条码",
            font=FONTS["body"]
        )
        self.barcode_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            entry_row, text="添加商品", width=100, height=40,
            font=FONTS["body"], fg_color=COLORS["primary"],
            command=self._add_goods
        ).pack(side="left")
        
        # 分割线
        ctk.CTkFrame(left, height=1, fg_color=COLORS["border"]).grid(row=0, column=0, sticky="sew", padx=20)
        
        # 商品列表
        list_frame = ctk.CTkFrame(left, fg_color="transparent")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=15)
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(list_frame, text="购物清单", font=FONTS["subtitle"], text_color=COLORS["text_dark"]).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Treeview样式
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=COLORS["text_dark"], rowheight=35, fieldbackground="white", font=("Microsoft YaHei UI", 12))
        style.configure("Treeview.Heading", font=("Microsoft YaHei UI", 12, "bold"), background="#F0F0F0", foreground=COLORS["text_dark"])
        style.map("Treeview", background=[("selected", COLORS["primary"])])
        
        columns = ("name", "price", "qty", "subtotal")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        self.tree.heading("name", text="商品名称")
        self.tree.heading("price", text="单价")
        self.tree.heading("qty", text="数量")
        self.tree.heading("subtotal", text="小计")
        self.tree.column("name", width=180)
        self.tree.column("price", width=100, anchor="center")
        self.tree.column("qty", width=80, anchor="center")
        self.tree.column("subtotal", width=100, anchor="center")
        self.tree.grid(row=1, column=0, sticky="nsew")
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
    
    def _create_right_panel(self):
        """右侧面板：会员 + 结算"""
        right = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew")
        
        # 会员区域
        member_frame = ctk.CTkFrame(right, fg_color="transparent")
        member_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(member_frame, text="会员信息", font=FONTS["subtitle"], text_color=COLORS["text_dark"]).pack(anchor="w")
        
        self.member_entry = ctk.CTkEntry(
            member_frame, height=38,
            placeholder_text="输入会员卡号或手机号",
            font=FONTS["body"]
        )
        self.member_entry.pack(fill="x", pady=(10, 8))
        
        ctk.CTkButton(
            member_frame, text="查询会员", height=36,
            font=FONTS["body"], fg_color=COLORS["info"],
            command=self._query_member
        ).pack(fill="x")
        
        # 分割线
        ctk.CTkFrame(right, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=20)
        
        # 金额区域
        amount_frame = ctk.CTkFrame(right, fg_color="transparent")
        amount_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(amount_frame, text="结算信息", font=FONTS["subtitle"], text_color=COLORS["text_dark"]).pack(anchor="w", pady=(0, 15))
        
        # 金额明细
        for label, value in [("商品总额", "¥0.00"), ("会员折扣", "无"), ("优惠金额", "¥0.00")]:
            row = ctk.CTkFrame(amount_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=label, font=FONTS["body"], text_color=COLORS["gray"]).pack(side="left")
            ctk.CTkLabel(row, text=value, font=FONTS["body"], text_color=COLORS["text_dark"]).pack(side="right")
        
        # 实付金额
        ctk.CTkLabel(
            amount_frame, text="¥ 0.00", 
            font=FONTS["price"], text_color=COLORS["success"]
        ).pack(pady=15)
        
        # 支付方式
        ctk.CTkLabel(amount_frame, text="支付方式", font=FONTS["body"], text_color=COLORS["text_dark"]).pack(anchor="w", pady=(0, 5))
        self.pay_method = ctk.CTkOptionMenu(
            amount_frame, values=["现金", "银行卡", "微信支付", "支付宝"],
            font=FONTS["body"], height=36
        )
        self.pay_method.pack(fill="x")
        
        # 分割线
        ctk.CTkFrame(right, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=20, pady=10)
        
        # 操作按钮
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        btn_row = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(btn_row, text="挂单", width=85, height=36, font=FONTS["body"], fg_color=COLORS["gray"], command=self._hang_order).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="调单", width=85, height=36, font=FONTS["body"], fg_color=COLORS["info"], command=self._load_order).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="撤单", width=85, height=36, font=FONTS["body"], fg_color=COLORS["danger"], command=self._cancel_order).pack(side="left")
        
        # 结账按钮
        ctk.CTkButton(
            btn_frame, text="结 账", height=50,
            font=FONTS["title"], fg_color=COLORS["success"],
            hover_color="#219A52",
            command=self._checkout
        ).pack(fill="x", pady=(5, 0))
    
    # ========== 事件处理函数（占位） ==========
    def _add_goods(self):
        print("添加商品:", self.barcode_entry.get())
    
    def _query_member(self):
        print("查询会员:", self.member_entry.get())
    
    def _hang_order(self):
        print("挂单")
    
    def _load_order(self):
        print("调单")
    
    def _cancel_order(self):
        print("撤单")
    
    def _checkout(self):
        print("结账")
