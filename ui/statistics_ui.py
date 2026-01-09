# -*- coding: utf-8 -*-
"""统计报表界面"""

import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, timedelta
from logic.statistics_logic import StatisticsLogic

COLORS = {
    "primary": "#4A90D9",
    "card_bg": "#FFFFFF",
    "text_dark": "#2C3E50",
    "success": "#27AE60",
    "danger": "#E74C3C",
    "info": "#3498DB",
    "gray": "#95A5A6",
}

FONTS = {
    "title": ("微软雅黑", 16, "bold"),
    "subtitle": ("微软雅黑", 14, "bold"),
    "body": ("微软雅黑", 12),
    "big": ("微软雅黑", 24, "bold"),
}


class StatisticsUI(ctk.CTkFrame):
    """统计报表界面"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.logic = StatisticsLogic()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_header()
        self._create_summary_cards()
        self._create_detail_area()
        self._load_data()
    
    def _create_header(self):
        """标题栏"""
        header = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        ctk.CTkLabel(header, text="📊 统计报表", font=FONTS["title"], 
                    text_color=COLORS["text_dark"]).pack(side="left", padx=20, pady=15)
        
        # 日期选择
        date_frame = ctk.CTkFrame(header, fg_color="transparent")
        date_frame.pack(side="left", padx=30)
        
        ctk.CTkLabel(date_frame, text="日期范围:", font=FONTS["body"]).pack(side="left", padx=5)
        
        self.start_date = ctk.CTkEntry(date_frame, width=100, height=32, font=FONTS["body"])
        self.start_date.pack(side="left", padx=5)
        self.start_date.insert(0, (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
        
        ctk.CTkLabel(date_frame, text="至", font=FONTS["body"]).pack(side="left", padx=5)
        
        self.end_date = ctk.CTkEntry(date_frame, width=100, height=32, font=FONTS["body"])
        self.end_date.pack(side="left", padx=5)
        self.end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ctk.CTkButton(header, text="查询", width=80, height=32,
            font=FONTS["body"], fg_color=COLORS["info"],
            command=self._load_data).pack(side="left", padx=10)
        
        ctk.CTkButton(header, text="刷新", width=80, height=32,
            font=FONTS["body"], fg_color=COLORS["gray"],
            command=self._load_data).pack(side="right", padx=20, pady=15)
    
    def _create_summary_cards(self):
        """汇总卡片"""
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        
        # 今日销售额
        card1 = ctk.CTkFrame(cards_frame, fg_color=COLORS["card_bg"], corner_radius=10)
        card1.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(card1, text="销售总额", font=FONTS["subtitle"], 
                    text_color=COLORS["gray"]).pack(anchor="w", padx=20, pady=(15, 5))
        self.total_sales_label = ctk.CTkLabel(card1, text="¥ 0.00", font=FONTS["big"], 
                    text_color=COLORS["success"])
        self.total_sales_label.pack(anchor="w", padx=20, pady=(0, 15))
        
        # 订单数
        card2 = ctk.CTkFrame(cards_frame, fg_color=COLORS["card_bg"], corner_radius=10)
        card2.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(card2, text="订单总数", font=FONTS["subtitle"], 
                    text_color=COLORS["gray"]).pack(anchor="w", padx=20, pady=(15, 5))
        self.total_orders_label = ctk.CTkLabel(card2, text="0 单", font=FONTS["big"], 
                    text_color=COLORS["primary"])
        self.total_orders_label.pack(anchor="w", padx=20, pady=(0, 15))
        
        # 退货金额
        card3 = ctk.CTkFrame(cards_frame, fg_color=COLORS["card_bg"], corner_radius=10)
        card3.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(card3, text="退货金额", font=FONTS["subtitle"], 
                    text_color=COLORS["gray"]).pack(anchor="w", padx=20, pady=(15, 5))
        self.total_return_label = ctk.CTkLabel(card3, text="¥ 0.00", font=FONTS["big"], 
                    text_color=COLORS["danger"])
        self.total_return_label.pack(anchor="w", padx=20, pady=(0, 15))
        
        # 会员消费占比
        card4 = ctk.CTkFrame(cards_frame, fg_color=COLORS["card_bg"], corner_radius=10)
        card4.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(card4, text="会员消费占比", font=FONTS["subtitle"], 
                    text_color=COLORS["gray"]).pack(anchor="w", padx=20, pady=(15, 5))
        self.member_ratio_label = ctk.CTkLabel(card4, text="0%", font=FONTS["big"], 
                    text_color=COLORS["info"])
        self.member_ratio_label.pack(anchor="w", padx=20, pady=(0, 15))
    
    def _create_detail_area(self):
        """详情区域"""
        detail_frame = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        detail_frame.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        detail_frame.grid_rowconfigure(1, weight=1)
        detail_frame.grid_columnconfigure(0, weight=1)
        
        # 标签页
        tab_frame = ctk.CTkFrame(detail_frame, fg_color="transparent")
        tab_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        self.current_tab = "daily"
        
        self.tab_daily = ctk.CTkButton(tab_frame, text="每日销售", width=100, height=32,
            font=FONTS["body"], fg_color=COLORS["primary"],
            command=lambda: self._switch_tab("daily"))
        self.tab_daily.pack(side="left", padx=(0, 5))
        
        self.tab_goods = ctk.CTkButton(tab_frame, text="商品销量", width=100, height=32,
            font=FONTS["body"], fg_color=COLORS["gray"],
            command=lambda: self._switch_tab("goods"))
        self.tab_goods.pack(side="left", padx=(0, 5))
        
        self.tab_member = ctk.CTkButton(tab_frame, text="会员排行", width=100, height=32,
            font=FONTS["body"], fg_color=COLORS["gray"],
            command=lambda: self._switch_tab("member"))
        self.tab_member.pack(side="left", padx=(0, 5))
        
        self.tab_orders = ctk.CTkButton(tab_frame, text="订单查询", width=100, height=32,
            font=FONTS["body"], fg_color=COLORS["gray"],
            command=lambda: self._switch_tab("orders"))
        self.tab_orders.pack(side="left")
        
        # 数据表格
        table_frame = ctk.CTkFrame(detail_frame, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(table_frame, show="headings", height=15)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
    
    def _switch_tab(self, tab):
        """切换标签页"""
        self.current_tab = tab
        
        # 更新按钮样式
        self.tab_daily.configure(fg_color=COLORS["primary"] if tab == "daily" else COLORS["gray"])
        self.tab_goods.configure(fg_color=COLORS["primary"] if tab == "goods" else COLORS["gray"])
        self.tab_member.configure(fg_color=COLORS["primary"] if tab == "member" else COLORS["gray"])
        self.tab_orders.configure(fg_color=COLORS["primary"] if tab == "orders" else COLORS["gray"])
        
        self._load_detail_data()
    
    def _load_data(self):
        """加载数据"""
        start = self.start_date.get().strip()
        end = self.end_date.get().strip()
        
        # 加载汇总数据
        summary = self.logic.get_summary(start, end)
        
        self.total_sales_label.configure(text=f"¥ {summary['total_sales']:,.2f}")
        self.total_orders_label.configure(text=f"{summary['total_orders']} 单")
        self.total_return_label.configure(text=f"¥ {summary['total_return']:,.2f}")
        self.member_ratio_label.configure(text=f"{summary['member_ratio']:.1f}%")
        
        self._load_detail_data()
    
    def _load_detail_data(self):
        """加载详情数据"""
        start = self.start_date.get().strip()
        end = self.end_date.get().strip()
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.current_tab == "daily":
            self._setup_daily_columns()
            data = self.logic.get_daily_sales(start, end)
            for row in data:
                self.tree.insert("", "end", values=(
                    row['date'], row['order_count'], 
                    f"¥{row['sales']:,.2f}", f"¥{row['profit']:,.2f}"
                ))
        
        elif self.current_tab == "goods":
            self._setup_goods_columns()
            data = self.logic.get_goods_ranking(start, end)
            for i, row in enumerate(data, 1):
                self.tree.insert("", "end", values=(
                    i, row['goods_name'], row['total_qty'], f"¥{row['total_amount']:,.2f}"
                ))
        
        elif self.current_tab == "member":
            self._setup_member_columns()
            data = self.logic.get_member_ranking(start, end)
            for i, row in enumerate(data, 1):
                self.tree.insert("", "end", values=(
                    i, row['name'], row['card_no'], 
                    row['order_count'], f"¥{row['total_amount']:,.2f}"
                ))
        
        elif self.current_tab == "orders":
            self._setup_orders_columns()
            data = self.logic.get_order_list(start, end)
            status_map = {
                "completed": "已完成",
                "full_returned": "已退货",
                "part_returned": "部分退货",
                "cancelled": "已取消",
                "pending_pay": "待支付",
                "hanged": "挂单中"
            }
            for row in data:
                self.tree.insert("", "end", values=(
                    row['order_no'],
                    row['member_name'] or "散客",
                    f"¥{row['actual_amount']:,.2f}",
                    status_map.get(row['order_status'], row['order_status']),
                    row['create_time'].strftime('%Y-%m-%d %H:%M') if row['create_time'] else ""
                ))
    
    def _setup_daily_columns(self):
        """设置每日销售列"""
        self.tree["columns"] = ("日期", "订单数", "销售额", "毛利")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
    
    def _setup_goods_columns(self):
        """设置商品销量列"""
        self.tree["columns"] = ("排名", "商品名称", "销量", "销售额")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.column("排名", width=60, anchor="center")
        self.tree.column("商品名称", width=200)
        self.tree.column("销量", width=80, anchor="center")
        self.tree.column("销售额", width=120, anchor="center")
    
    def _setup_member_columns(self):
        """设置会员排行列"""
        self.tree["columns"] = ("排名", "会员姓名", "卡号", "订单数", "消费金额")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.column("排名", width=60, anchor="center")
        self.tree.column("会员姓名", width=100, anchor="center")
        self.tree.column("卡号", width=120, anchor="center")
        self.tree.column("订单数", width=80, anchor="center")
        self.tree.column("消费金额", width=120, anchor="center")
    
    def _setup_orders_columns(self):
        """设置订单查询列"""
        self.tree["columns"] = ("订单号", "会员", "实付金额", "状态", "下单时间")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.column("订单号", width=180, anchor="center")
        self.tree.column("会员", width=100, anchor="center")
        self.tree.column("实付金额", width=100, anchor="center")
        self.tree.column("状态", width=80, anchor="center")
        self.tree.column("下单时间", width=140, anchor="center")
