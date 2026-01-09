# -*- coding: utf-8 -*-
"""
退货处理界面 - 组员4负责
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from decimal import Decimal

COLORS = {
    "primary": "#4A90D9",
    "card_bg": "#FFFFFF",
    "text_dark": "#2C3E50",
    "success": "#27AE60",
    "danger": "#E74C3C",
    "warning": "#F39C12",
    "gray": "#95A5A6",
    "border": "#E0E0E0",
}

FONTS = {
    "title": ("微软雅黑", 16, "bold"),
    "subtitle": ("微软雅黑", 14, "bold"),
    "body": ("微软雅黑", 13),
    "price": ("微软雅黑", 24, "bold"),
}

REASON_MAP = {
    "质量问题": "quality_issue",
    "7天无理由": "no_reason_7day",
    "规格不符": "spec_mismatch",
    "商品损坏": "damaged",
    "其他": "other"
}


class ReturnHandleUI(ctk.CTkFrame):
    """退货处理界面"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 初始化逻辑层
        try:
            from logic.return_full_logic import ReturnFullLogic
            from logic.return_part_logic import ReturnPartLogic
            from logic.return_query_logic import ReturnQueryLogic
            self.full_return_logic = ReturnFullLogic()
            self.part_return_logic = ReturnPartLogic()
            self.query_logic = ReturnQueryLogic()
        except ImportError:
            self.full_return_logic = None
            self.part_return_logic = None
            self.query_logic = None
        
        self.current_order = None
        self.return_items = []
        self.return_type = "part"
        self.operator_id = 1
        
        self._create_left_panel()
        self._create_right_panel()

    def _create_left_panel(self):
        """左侧面板：查询和商品列表"""
        left = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_rowconfigure(2, weight=1)
        left.grid_columnconfigure(0, weight=1)
        
        # 标题
        header = ctk.CTkFrame(left, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        ctk.CTkLabel(header, text="↩️ 退货处理", font=FONTS["title"], 
                    text_color=COLORS["text_dark"]).pack(side="left")
        
        # 查询区域
        query_frame = ctk.CTkFrame(left, fg_color="transparent")
        query_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        self.order_entry = ctk.CTkEntry(query_frame, width=250, height=36,
            placeholder_text="输入订单号/会员卡号/手机号", font=FONTS["body"])
        self.order_entry.pack(side="left", padx=(0, 10))
        self.order_entry.bind("<Return>", lambda e: self._query_order())
        
        ctk.CTkButton(query_frame, text="查询订单", width=100, height=36,
            font=FONTS["body"], fg_color=COLORS["primary"],
            command=self._query_order).pack(side="left")
        
        self.order_info_label = ctk.CTkLabel(query_frame, text="", font=FONTS["body"], 
                                             text_color=COLORS["gray"])
        self.order_info_label.pack(side="left", padx=20)
        
        # 商品列表
        list_frame = ctk.CTkFrame(left, fg_color="transparent")
        list_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 15))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        columns = ("goods_name", "barcode", "unit_price", "quantity", "returnable")
        self.goods_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        self.goods_tree.heading("goods_name", text="商品名称")
        self.goods_tree.heading("barcode", text="条码")
        self.goods_tree.heading("unit_price", text="单价")
        self.goods_tree.heading("quantity", text="购买数量")
        self.goods_tree.heading("returnable", text="可退数量")
        
        self.goods_tree.column("goods_name", width=180)
        self.goods_tree.column("barcode", width=130, anchor="center")
        self.goods_tree.column("unit_price", width=90, anchor="center")
        self.goods_tree.column("quantity", width=90, anchor="center")
        self.goods_tree.column("returnable", width=90, anchor="center")
        
        self.goods_tree.grid(row=0, column=0, sticky="nsew")
        self.goods_tree.bind("<Double-1>", self._add_to_return)

    def _create_right_panel(self):
        """右侧面板：退货原因和退款信息"""
        right = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew")
        
        # 退货原因
        ctk.CTkLabel(right, text="退货原因", font=FONTS["subtitle"], 
                    text_color=COLORS["text_dark"]).pack(anchor="w", padx=20, pady=(20, 10))
        
        self.return_reason = ctk.CTkOptionMenu(right, 
            values=["质量问题", "7天无理由", "规格不符", "商品损坏", "其他"],
            font=FONTS["body"], height=38)
        self.return_reason.pack(fill="x", padx=20)
        self.return_reason.set("请选择退货原因")
        
        # 问题描述
        ctk.CTkLabel(right, text="问题描述", font=FONTS["subtitle"], 
                    text_color=COLORS["text_dark"]).pack(anchor="w", padx=20, pady=(15, 10))
        
        self.desc_text = ctk.CTkTextbox(right, height=80, font=FONTS["body"])
        self.desc_text.pack(fill="x", padx=20)
        
        # 退款金额
        ctk.CTkLabel(right, text="退款金额", font=FONTS["subtitle"], 
                    text_color=COLORS["text_dark"]).pack(anchor="w", padx=20, pady=(20, 10))
        
        self.refund_label = ctk.CTkLabel(right, text="¥ 0.00", font=FONTS["price"], 
                                         text_color=COLORS["danger"])
        self.refund_label.pack(pady=10)
        
        # 操作按钮
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(btn_frame, text="整单退货", width=120, height=40,
            font=FONTS["body"], fg_color=COLORS["danger"],
            command=self._full_return).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(btn_frame, text="部分退货", width=120, height=40,
            font=FONTS["body"], fg_color=COLORS["warning"],
            command=self._part_return).pack(side="left")
        
        ctk.CTkButton(right, text="确认退货", height=50,
            font=FONTS["title"], fg_color=COLORS["success"],
            command=self._confirm_return).pack(fill="x", padx=20, pady=(10, 0))
        
        ctk.CTkButton(right, text="清空", height=40,
            font=FONTS["body"], fg_color=COLORS["gray"],
            command=self._clear).pack(fill="x", padx=20, pady=(10, 20))

    def _query_order(self):
        """查询订单"""
        keyword = self.order_entry.get().strip()
        if not keyword:
            messagebox.showwarning("提示", "请输入查询条件")
            return
        
        if not self.query_logic:
            messagebox.showwarning("提示", "退货查询模块未加载")
            return
        
        result = self.query_logic.query_order_for_return(keyword)
        if not result['success'] or not result['data']:
            messagebox.showinfo("提示", result['message'] or "未找到可退货订单")
            return
        
        order = result['data'][0]
        detail_result = self.query_logic.get_order_detail(order['order_id'])
        if not detail_result['success']:
            messagebox.showerror("错误", detail_result['message'])
            return
        
        self.current_order = detail_result['data']
        self._display_order()
    
    def _display_order(self):
        """显示订单详情"""
        if not self.current_order:
            return
        
        order = self.current_order
        self.order_info_label.configure(text=f"订单: {order['order_no']} | 实付: ¥{order['actual_amount']}")
        
        for item in self.goods_tree.get_children():
            self.goods_tree.delete(item)
        
        for detail in order.get('details', []):
            returnable = float(detail['quantity']) - float(detail['returned_quantity'])
            self.goods_tree.insert("", "end", iid=str(detail['detail_id']), values=(
                detail['goods_name'], detail['barcode'],
                f"¥{detail['unit_price']}", detail['quantity'],
                returnable if returnable > 0 else "已退完"
            ))
    
    def _add_to_return(self, event):
        """双击添加到退货列表"""
        selected = self.goods_tree.selection()
        if not selected or not self.current_order:
            return
        
        detail_id = int(selected[0])
        for detail in self.current_order.get('details', []):
            if detail['detail_id'] == detail_id:
                returnable = float(detail['quantity']) - float(detail['returned_quantity'])
                if returnable > 0:
                    self.return_items.append({
                        'detail_id': detail_id,
                        'goods_id': detail['goods_id'],
                        'goods_name': detail['goods_name'],
                        'quantity': returnable,
                        'unit_price': float(detail['unit_price']),
                        'discount': float(detail['discount'])
                    })
                    self._update_refund()
                    messagebox.showinfo("提示", f"已添加 {detail['goods_name']} 到退货列表")
                break
    
    def _update_refund(self):
        """更新退款金额"""
        total = sum(item['unit_price'] * item['quantity'] * item['discount'] for item in self.return_items)
        self.refund_label.configure(text=f"¥ {total:.2f}")
    
    def _full_return(self):
        """整单退货"""
        if not self.current_order:
            messagebox.showwarning("提示", "请先查询订单")
            return
        
        self.return_type = "full"
        self.return_items = []
        
        for detail in self.current_order.get('details', []):
            returnable = float(detail['quantity']) - float(detail['returned_quantity'])
            if returnable > 0:
                self.return_items.append({
                    'detail_id': detail['detail_id'],
                    'goods_id': detail['goods_id'],
                    'goods_name': detail['goods_name'],
                    'quantity': returnable,
                    'unit_price': float(detail['unit_price']),
                    'discount': float(detail['discount'])
                })
        
        self._update_refund()
        messagebox.showinfo("提示", "已切换为整单退货模式")
    
    def _part_return(self):
        """部分退货"""
        self.return_type = "part"
        messagebox.showinfo("提示", "部分退货模式：双击商品添加到退货列表")
    
    def _confirm_return(self):
        """确认退货"""
        if not self.current_order:
            messagebox.showwarning("提示", "请先查询订单")
            return
        
        if not self.return_items:
            messagebox.showwarning("提示", "请选择退货商品")
            return
        
        reason_text = self.return_reason.get()
        if reason_text == "请选择退货原因":
            messagebox.showwarning("提示", "请选择退货原因")
            return
        
        reason = REASON_MAP.get(reason_text, "other")
        reason_detail = self.desc_text.get("1.0", "end").strip()
        
        total_refund = sum(item['unit_price'] * item['quantity'] * item['discount'] for item in self.return_items)
        
        if not messagebox.askyesno("确认退货", f"确认退款 ¥{total_refund:.2f}？"):
            return
        
        order_id = self.current_order['order_id']
        
        if self.return_type == "full" and self.full_return_logic:
            result = self.full_return_logic.process_full_return(
                order_id=order_id, reason=reason, reason_detail=reason_detail, operator_id=self.operator_id)
        elif self.part_return_logic:
            return_items_data = [{'detail_id': item['detail_id'], 'goods_id': item['goods_id'], 
                                  'quantity': item['quantity']} for item in self.return_items]
            result = self.part_return_logic.process_part_return(
                order_id=order_id, return_items=return_items_data, reason=reason, 
                operator_id=self.operator_id, reason_detail=reason_detail)
        else:
            messagebox.showwarning("提示", "退货模块未加载")
            return
        
        if result['success']:
            messagebox.showinfo("退货成功", f"退货单号: {result['data']['return_no']}\n退款金额: ¥{result['data']['refund_amount']:.2f}")
            self._clear()
            # 通知退货查询界面刷新
            self._notify_return_query_refresh()
        else:
            messagebox.showerror("退货失败", result['message'])
    
    def _notify_return_query_refresh(self):
        """通知退货查询界面刷新数据（退货查询界面会在切换时自动刷新）"""
        pass  # 退货查询界面已改为每次显示时自动加载数据
    
    def _clear(self):
        """清空"""
        self.current_order = None
        self.return_items = []
        self.order_entry.delete(0, "end")
        self.order_info_label.configure(text="")
        for item in self.goods_tree.get_children():
            self.goods_tree.delete(item)
        self.return_reason.set("请选择退货原因")
        self.desc_text.delete("1.0", "end")
        self.refund_label.configure(text="¥ 0.00")
