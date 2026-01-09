# -*- coding: utf-8 -*-
"""
退货查询界面 - 组员4负责
"""

import customtkinter as ctk
from tkinter import ttk, messagebox

COLORS = {
    "primary": "#4A90D9",
    "card_bg": "#FFFFFF",
    "text_dark": "#2C3E50",
    "info": "#3498DB",
    "gray": "#95A5A6",
}

FONTS = {
    "title": ("微软雅黑", 16, "bold"),
    "body": ("微软雅黑", 13),
}


class ReturnQueryUI(ctk.CTkFrame):
    """退货查询界面"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        try:
            from logic.return_query_logic import ReturnQueryLogic
            self.logic = ReturnQueryLogic()
        except ImportError:
            self.logic = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_query_panel()
        self._create_result_panel()
        
        # 界面加载时自动查询全部退货记录
        self.after(100, self._query_all)
    
    def _create_query_panel(self):
        """查询面板"""
        query_card = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        query_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        ctk.CTkLabel(query_card, text="🔍 退货记录查询", font=FONTS["title"], 
                    text_color=COLORS["text_dark"]).pack(anchor="w", padx=20, pady=(15, 10))
        
        search_frame = ctk.CTkFrame(query_card, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(search_frame, text="订单号/退货单号：", font=FONTS["body"], 
                    text_color=COLORS["text_dark"]).pack(side="left")
        self.order_entry = ctk.CTkEntry(search_frame, width=220, height=36, 
                                        placeholder_text="输入订单号或退货单号查询", font=FONTS["body"])
        self.order_entry.pack(side="left", padx=(5, 20))
        self.order_entry.bind("<Return>", lambda e: self._query())
        
        ctk.CTkButton(search_frame, text="查询", width=100, height=36,
            font=FONTS["body"], fg_color=COLORS["primary"],
            command=self._query).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(search_frame, text="查询全部", width=100, height=36,
            font=FONTS["body"], fg_color=COLORS["info"],
            command=self._query_all).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(search_frame, text="清空", width=80, height=36,
            font=FONTS["body"], fg_color=COLORS["gray"],
            command=self._clear).pack(side="left")
    
    def _create_result_panel(self):
        """结果面板"""
        result_card = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        result_card.grid(row=1, column=0, sticky="nsew")
        result_card.grid_rowconfigure(0, weight=1)
        result_card.grid_columnconfigure(0, weight=1)
        
        columns = ("return_no", "order_no", "return_type", "refund_amount", "reason", "create_time")
        self.tree = ttk.Treeview(result_card, columns=columns, show="headings", height=15)
        
        self.tree.heading("return_no", text="退货单号")
        self.tree.heading("order_no", text="原订单号")
        self.tree.heading("return_type", text="退货类型")
        self.tree.heading("refund_amount", text="退款金额")
        self.tree.heading("reason", text="退货原因")
        self.tree.heading("create_time", text="退货时间")
        
        self.tree.column("return_no", width=150, anchor="center")
        self.tree.column("order_no", width=150, anchor="center")
        self.tree.column("return_type", width=80, anchor="center")
        self.tree.column("refund_amount", width=100, anchor="center")
        self.tree.column("reason", width=100, anchor="center")
        self.tree.column("create_time", width=150, anchor="center")
        
        self.tree.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    
    def _query(self):
        """查询退货记录"""
        keyword = self.order_entry.get().strip()
        
        if not self.logic:
            messagebox.showwarning("提示", "查询模块未加载")
            return
        
        result = self.logic.query_return_records(keyword)
        if not result['success']:
            messagebox.showerror("错误", result['message'])
            return
        
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        records = result['data']
        if not records:
            messagebox.showinfo("提示", "没有找到退货记录")
            return
        
        # 退货类型映射
        type_map = {"full": "整单退货", "part": "部分退货"}
        reason_map = {
            "quality_issue": "质量问题",
            "no_reason_7day": "7天无理由",
            "spec_mismatch": "规格不符",
            "damaged": "商品损坏",
            "other": "其他"
        }
        
        for record in records:
            self.tree.insert("", "end", values=(
                record['return_no'],
                record['order_no'],
                type_map.get(record['return_type'], record['return_type']),
                f"¥{record['refund_amount']:.2f}",
                reason_map.get(record['return_reason'], record['return_reason']),
                record['create_time'].strftime('%Y-%m-%d %H:%M') if record['create_time'] else ""
            ))
    
    def _clear(self):
        """清空"""
        self.order_entry.delete(0, "end")
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def _query_all(self):
        """查询全部退货记录"""
        if not self.logic:
            messagebox.showwarning("提示", "查询模块未加载")
            return
        
        result = self.logic.query_return_records("")
        if not result['success']:
            messagebox.showerror("错误", result['message'])
            return
        
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        records = result['data']
        if not records:
            messagebox.showinfo("提示", "没有退货记录")
            return
        
        # 退货类型映射
        type_map = {"full": "整单退货", "part": "部分退货"}
        reason_map = {
            "quality_issue": "质量问题",
            "no_reason_7day": "7天无理由",
            "spec_mismatch": "规格不符",
            "damaged": "商品损坏",
            "other": "其他"
        }
        
        for record in records:
            self.tree.insert("", "end", values=(
                record['return_no'],
                record['order_no'],
                type_map.get(record['return_type'], record['return_type']),
                f"¥{record['refund_amount']:.2f}",
                reason_map.get(record['return_reason'], record['return_reason']),
                record['create_time'].strftime('%Y-%m-%d %H:%M') if record['create_time'] else ""
            ))
