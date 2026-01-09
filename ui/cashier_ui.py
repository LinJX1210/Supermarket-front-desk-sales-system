# -*- coding: utf-8 -*-
"""
收银界面 - 组员1负责
已对接逻辑层
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from decimal import Decimal

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
    "light_gray": "#F8F9FA",
}

FONTS = {
    "title": ("微软雅黑", 16, "bold"),
    "subtitle": ("微软雅黑", 13, "bold"),
    "body": ("微软雅黑", 12),
    "small": ("微软雅黑", 10),
    "price": ("微软雅黑", 24, "bold"),
}


class CashierUI(ctk.CTkFrame):
    """收银界面"""
    
    def __init__(self, parent, user_info=None):
        super().__init__(parent, fg_color="transparent")
        
        # 当前订单数据
        self.order_items = []
        self.current_member = None
        self.discount_rate = 1.0
        self.current_order_id = None  # 调单时使用
        
        # 从登录用户信息获取收银员ID
        self.user_info = user_info or {}
        self.cashier_id = self.user_info.get('user_id', 1)
        
        # 布局
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_left_panel()
        self._create_right_panel()
        self._setup_treeview_style()

    def _setup_treeview_style(self):
        """设置Treeview样式"""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="white",
            foreground=COLORS["text_dark"],
            rowheight=36,
            fieldbackground="white",
            font=("微软雅黑", 12)
        )
        style.configure(
            "Treeview.Heading",
            font=("微软雅黑", 12, "bold"),
            background="#F0F0F0",
            foreground=COLORS["text_dark"]
        )
        style.map("Treeview", background=[("selected", COLORS["primary"])])
    
    def _create_left_panel(self):
        """左侧面板：条码输入 + 散装商品 + 商品列表"""
        left = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_rowconfigure(2, weight=1)
        left.grid_columnconfigure(0, weight=1)
        
        # ===== 条码输入区 =====
        barcode_frame = ctk.CTkFrame(left, fg_color="transparent")
        barcode_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(
            barcode_frame, text="商品条码",
            font=FONTS["subtitle"], text_color=COLORS["text_dark"]
        ).pack(anchor="w")
        
        input_row = ctk.CTkFrame(barcode_frame, fg_color="transparent")
        input_row.pack(fill="x", pady=(8, 0))
        
        self.barcode_entry = ctk.CTkEntry(
            input_row, height=42,
            placeholder_text="扫码枪扫描或手动输入商品条码后回车",
            font=FONTS["body"]
        )
        self.barcode_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.barcode_entry.bind("<Return>", lambda e: self._add_goods())
        
        ctk.CTkButton(
            input_row, text="添加", width=80, height=42,
            font=FONTS["body"], fg_color=COLORS["primary"],
            command=self._add_goods
        ).pack(side="left")

        # ===== 散装商品区 =====
        bulk_frame = ctk.CTkFrame(left, fg_color=COLORS["light_gray"], corner_radius=8)
        bulk_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        bulk_title = ctk.CTkFrame(bulk_frame, fg_color="transparent")
        bulk_title.pack(fill="x", padx=15, pady=(10, 5))
        ctk.CTkLabel(
            bulk_title, text="🥬 散装商品",
            font=FONTS["subtitle"], text_color=COLORS["text_dark"]
        ).pack(side="left")
        
        bulk_input = ctk.CTkFrame(bulk_frame, fg_color="transparent")
        bulk_input.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(bulk_input, text="条码:", font=FONTS["body"]).grid(row=0, column=0, padx=(0, 5))
        self.bulk_barcode = ctk.CTkEntry(bulk_input, width=120, height=36, font=FONTS["body"])
        self.bulk_barcode.grid(row=0, column=1, padx=(0, 15))
        
        ctk.CTkLabel(bulk_input, text="重量(kg):", font=FONTS["body"]).grid(row=0, column=2, padx=(0, 5))
        self.bulk_weight = ctk.CTkEntry(bulk_input, width=80, height=36, font=FONTS["body"], placeholder_text="0.00")
        self.bulk_weight.grid(row=0, column=3, padx=(0, 15))
        
        ctk.CTkButton(
            bulk_input, text="计价添加", width=90, height=36,
            font=FONTS["body"], fg_color=COLORS["info"],
            command=self._add_bulk_goods
        ).grid(row=0, column=4)
        
        # ===== 商品列表 =====
        list_frame = ctk.CTkFrame(left, fg_color="transparent")
        list_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 15))
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        title_row = ctk.CTkFrame(list_frame, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        
        ctk.CTkLabel(
            title_row, text="📋 购物清单",
            font=FONTS["subtitle"], text_color=COLORS["text_dark"]
        ).pack(side="left")
        
        ctk.CTkButton(
            title_row, text="删除选中", width=80, height=30,
            font=FONTS["small"], fg_color=COLORS["danger"],
            command=self._delete_selected
        ).pack(side="right", padx=(0, 5))
        
        ctk.CTkButton(
            title_row, text="清空", width=60, height=30,
            font=FONTS["small"], fg_color=COLORS["gray"],
            command=self._clear_list
        ).pack(side="right")
        
        columns = ("name", "price", "qty", "subtotal")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.tree.heading("name", text="商品名称")
        self.tree.heading("price", text="单价")
        self.tree.heading("qty", text="数量")
        self.tree.heading("subtotal", text="小计")
        self.tree.column("name", width=200, anchor="w")
        self.tree.column("price", width=100, anchor="center")
        self.tree.column("qty", width=80, anchor="center")
        self.tree.column("subtotal", width=100, anchor="center")
        self.tree.grid(row=1, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _create_right_panel(self):
        """右侧面板：会员 + 结算 + 操作按钮"""
        right = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew")
        
        # 使用grid布局确保按钮始终可见
        right.grid_rowconfigure(0, weight=0)  # 会员区域
        right.grid_rowconfigure(1, weight=0)  # 分隔线
        right.grid_rowconfigure(2, weight=1)  # 结算信息（可扩展）
        right.grid_rowconfigure(3, weight=0)  # 支付方式
        right.grid_rowconfigure(4, weight=0)  # 分隔线
        right.grid_rowconfigure(5, weight=0)  # 操作按钮
        right.grid_columnconfigure(0, weight=1)
        
        # ===== 会员区域 =====
        member_frame = ctk.CTkFrame(right, fg_color="transparent")
        member_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            member_frame, text="👤 会员信息",
            font=FONTS["subtitle"], text_color=COLORS["text_dark"]
        ).pack(anchor="w")
        
        member_input = ctk.CTkFrame(member_frame, fg_color="transparent")
        member_input.pack(fill="x", pady=(5, 0))
        
        self.member_entry = ctk.CTkEntry(
            member_input, height=32,
            placeholder_text="会员卡号/手机号",
            font=FONTS["body"]
        )
        self.member_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.member_entry.bind("<Return>", lambda e: self._query_member())
        
        ctk.CTkButton(
            member_input, text="查询", width=50, height=32,
            font=FONTS["body"], fg_color=COLORS["info"],
            command=self._query_member
        ).pack(side="left")
        
        self.member_info_label = ctk.CTkLabel(
            member_frame, text="未选择会员（散客）",
            font=FONTS["small"], text_color=COLORS["gray"]
        )
        self.member_info_label.pack(anchor="w", pady=(3, 0))
        
        # 分隔线1
        ctk.CTkFrame(right, height=1, fg_color=COLORS["border"]).grid(row=1, column=0, sticky="ew", padx=15, pady=3)
        
        # ===== 结算信息 =====
        amount_frame = ctk.CTkFrame(right, fg_color="transparent")
        amount_frame.grid(row=2, column=0, sticky="new", padx=15, pady=3)
        
        ctk.CTkLabel(
            amount_frame, text="💰 结算信息",
            font=FONTS["subtitle"], text_color=COLORS["text_dark"]
        ).pack(anchor="w", pady=(0, 5))
        
        self.total_label = self._create_amount_row(amount_frame, "商品总额", "¥0.00")
        self.discount_label = self._create_amount_row(amount_frame, "会员折扣", "无")
        self.discount_amount_label = self._create_amount_row(amount_frame, "优惠金额", "¥0.00")
        
        pay_frame = ctk.CTkFrame(amount_frame, fg_color=COLORS["light_gray"], corner_radius=6)
        pay_frame.pack(fill="x", pady=(8, 0))
        
        ctk.CTkLabel(
            pay_frame, text="实付金额",
            font=FONTS["small"], text_color=COLORS["gray"]
        ).pack(pady=(5, 0))
        
        self.actual_amount_label = ctk.CTkLabel(
            pay_frame, text="¥ 0.00",
            font=FONTS["price"], text_color=COLORS["success"]
        )
        self.actual_amount_label.pack(pady=(0, 5))

        # ===== 支付方式 =====
        pay_method_frame = ctk.CTkFrame(right, fg_color="transparent")
        pay_method_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=3)
        
        ctk.CTkLabel(
            pay_method_frame, text="支付方式",
            font=FONTS["small"], text_color=COLORS["text_dark"]
        ).pack(anchor="w", pady=(0, 3))
        
        self.pay_method = ctk.CTkSegmentedButton(
            pay_method_frame,
            values=["现金", "银行卡", "微信", "支付宝"],
            font=FONTS["small"]
        )
        self.pay_method.set("现金")
        self.pay_method.pack(fill="x")
        
        # 分隔线2
        ctk.CTkFrame(right, height=1, fg_color=COLORS["border"]).grid(row=4, column=0, sticky="ew", padx=15, pady=3)
        
        # ===== 操作按钮 =====
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.grid(row=5, column=0, sticky="sew", padx=15, pady=(3, 10))
        
        action_row = ctk.CTkFrame(btn_frame, fg_color="transparent")
        action_row.pack(fill="x", pady=(0, 5))
        
        ctk.CTkButton(
            action_row, text="📌挂单", width=70, height=32,
            font=FONTS["small"], fg_color=COLORS["gray"],
            hover_color="#7F8C8D", command=self._hang_order
        ).pack(side="left", padx=(0, 4))
        
        ctk.CTkButton(
            action_row, text="📋调单", width=70, height=32,
            font=FONTS["small"], fg_color=COLORS["info"],
            hover_color="#2980B9", command=self._load_order
        ).pack(side="left", padx=(0, 4))
        
        ctk.CTkButton(
            action_row, text="❌撤单", width=70, height=32,
            font=FONTS["small"], fg_color=COLORS["danger"],
            hover_color="#C0392B", command=self._cancel_order
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame, text="结  账", height=45,
            font=("微软雅黑", 15, "bold"),
            fg_color=COLORS["success"], hover_color="#219A52",
            command=self._checkout
        ).pack(fill="x")
    
    def _create_amount_row(self, parent, label, value):
        """创建金额行"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)
        ctk.CTkLabel(row, text=label, font=FONTS["small"], text_color=COLORS["gray"]).pack(side="left")
        value_label = ctk.CTkLabel(row, text=value, font=FONTS["body"], text_color=COLORS["text_dark"])
        value_label.pack(side="right")
        return value_label

    def _update_totals(self):
        """更新金额显示"""
        from logic.cashier_logic import calculate_order_total
        
        if not self.order_items:
            self.total_label.configure(text="¥0.00")
            self.discount_amount_label.configure(text="¥0.00")
            self.actual_amount_label.configure(text="¥ 0.00")
            return
        
        amounts = calculate_order_total(self.order_items, self.discount_rate)
        
        self.total_label.configure(text=f"¥{amounts['total_amount']:.2f}")
        self.discount_amount_label.configure(text=f"¥{amounts['discount_amount']:.2f}")
        self.actual_amount_label.configure(text=f"¥ {amounts['actual_amount']:.2f}")
    
    def _refresh_tree(self):
        """刷新商品列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for item in self.order_items:
            qty = item["quantity"]
            qty_str = str(int(qty)) if qty == int(qty) else f"{qty:.2f}"
            self.tree.insert("", "end", values=(
                item["goods_name"],
                f"¥{item['unit_price']:.2f}",
                qty_str,
                f"¥{item['subtotal']:.2f}"
            ))
        
        self._update_totals()


    
    def _add_goods(self):
        """添加商品（通过条码）"""
        from logic.cashier_logic import get_goods_by_barcode
        
        barcode = self.barcode_entry.get().strip()
        if not barcode:
            return
        
        result = get_goods_by_barcode(barcode)
        if not result["success"]:
            messagebox.showwarning("提示", result["message"])
            self.barcode_entry.delete(0, "end")
            return
        
        goods = result["data"]
        
        # 检查是否散装商品
        if goods["is_weighted"]:
            messagebox.showinfo("提示", "这是散装商品，请在散装商品区输入重量")
            self.bulk_barcode.delete(0, "end")
            self.bulk_barcode.insert(0, barcode)
            self.barcode_entry.delete(0, "end")
            return
        
        # 检查是否已在列表中
        for item in self.order_items:
            if item["goods_id"] == goods["goods_id"]:
                item["quantity"] += 1
                item["subtotal"] = float(Decimal(str(item["unit_price"])) * Decimal(str(item["quantity"])) * Decimal(str(item["discount"])))
                self._refresh_tree()
                self.barcode_entry.delete(0, "end")
                return
        
        # 添加新商品
        unit_price = goods["price"]
        discount = goods["discount"]
        subtotal = float(Decimal(str(unit_price)) * Decimal(str(discount)))
        
        self.order_items.append({
            "goods_id": goods["goods_id"],
            "goods_name": goods["goods_name"],
            "barcode": goods["barcode"],
            "unit_price": unit_price,
            "quantity": 1,
            "discount": discount,
            "subtotal": subtotal
        })
        
        self._refresh_tree()
        self.barcode_entry.delete(0, "end")

    def _add_bulk_goods(self):
        """添加散装商品"""
        from logic.cashier_logic import calculate_bulk_price
        
        barcode = self.bulk_barcode.get().strip()
        weight_str = self.bulk_weight.get().strip()
        
        if not barcode:
            messagebox.showwarning("提示", "请输入条码")
            return
        if not weight_str:
            messagebox.showwarning("提示", "请输入重量")
            return
        
        try:
            weight = float(weight_str)
            if weight <= 0:
                messagebox.showwarning("提示", "重量必须大于0")
                return
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的重量")
            return
        
        result = calculate_bulk_price(barcode, weight)
        if not result["success"]:
            messagebox.showwarning("提示", result["message"])
            return
        
        data = result["data"]
        self.order_items.append({
            "goods_id": data["goods_id"],
            "goods_name": data["goods_name"],
            "barcode": data["barcode"],
            "unit_price": data["unit_price"],
            "quantity": data["quantity"],
            "discount": data["discount"],
            "subtotal": data["subtotal"]
        })
        
        self._refresh_tree()
        self.bulk_barcode.delete(0, "end")
        self.bulk_weight.delete(0, "end")
    
    def _delete_selected(self):
        """删除选中商品"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的商品")
            return
        
        indices = [self.tree.index(item) for item in selected]
        for idx in sorted(indices, reverse=True):
            del self.order_items[idx]
        
        self._refresh_tree()
    
    def _clear_list(self):
        """清空商品列表"""
        if not self.order_items:
            return
        if messagebox.askyesno("确认", "确定要清空购物清单吗？"):
            self.order_items.clear()
            self.current_order_id = None
            self._refresh_tree()
    
    def _query_member(self):
        """查询会员"""
        from db.db_conn import DBConnection
        
        keyword = self.member_entry.get().strip()
        if not keyword:
            self.current_member = None
            self.discount_rate = 1.0
            self.member_info_label.configure(text="未选择会员（散客）")
            self.discount_label.configure(text="无")
            self._update_totals()
            return
        
        try:
            with DBConnection() as db:
                sql = """
                    SELECT m.member_id, m.card_no, m.name, m.phone, m.level_code,
                           m.total_points, mlr.discount_rate, mlr.level_name
                    FROM member m
                    JOIN member_level_rule mlr ON m.level_code = mlr.level_code
                    WHERE (m.card_no = %s OR m.phone = %s) AND m.status = 'active'
                """
                db.execute(sql, (keyword, keyword))
                member = db.fetchone()
                
                if not member:
                    messagebox.showwarning("提示", "未找到该会员")
                    return
                
                self.current_member = member
                self.discount_rate = float(member["discount_rate"])
                
                discount_text = f"{member['level_name']} ({int(self.discount_rate * 100)}折)" if self.discount_rate < 1 else "无"
                self.discount_label.configure(text=discount_text)
                self.member_info_label.configure(
                    text=f"✓ {member['name']} | {member['card_no']} | 积分: {member['total_points']}"
                )
                self._update_totals()
                
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")

    def _hang_order(self):
        """挂单"""
        from logic.cashier_hang_cancel import hang_order
        
        if not self.order_items:
            messagebox.showinfo("提示", "当前没有商品，无法挂单")
            return
        
        member_id = self.current_member["member_id"] if self.current_member else None
        result = hang_order(self.cashier_id, member_id, self.order_items)
        
        if result["success"]:
            messagebox.showinfo("成功", f"挂单成功\n订单号: {result['data']['order_no']}")
            self._reset_order()
        else:
            messagebox.showerror("错误", result["message"])
    
    def _load_order(self):
        """调单 - 显示挂单列表"""
        from logic.cashier_hang_cancel import get_hanged_orders, load_order
        
        result = get_hanged_orders(self.cashier_id)
        if not result["success"]:
            messagebox.showerror("错误", result["message"])
            return
        
        orders = result["data"]
        if not orders:
            messagebox.showinfo("提示", "没有挂单订单")
            return
        
        # 创建选择对话框
        dialog = ctk.CTkToplevel(self)
        dialog.title("选择挂单")
        dialog.geometry("500x450")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="请选择要调取的订单", font=FONTS["subtitle"]).pack(pady=15)
        
        # 订单列表
        list_frame = ctk.CTkFrame(dialog)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        columns = ("order_no", "amount", "time")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        tree.heading("order_no", text="订单号")
        tree.heading("amount", text="金额")
        tree.heading("time", text="挂单时间")
        tree.column("order_no", width=180)
        tree.column("amount", width=80, anchor="center")
        tree.column("time", width=150, anchor="center")
        tree.pack(fill="both", expand=True)
        
        for order in orders:
            tree.insert("", "end", iid=order["order_id"], values=(
                order["order_no"],
                f"¥{order['total_amount']:.2f}",
                order["create_time"]
            ))
        
        def on_select():
            selected = tree.selection()
            if not selected:
                messagebox.showinfo("提示", "请选择一个订单")
                return
            
            order_id = int(selected[0])
            load_result = load_order(order_id)
            
            if load_result["success"]:
                data = load_result["data"]
                self.order_items = data["items"]
                self.current_order_id = data["order_id"]
                
                # 恢复会员信息
                if data["member_id"]:
                    self.member_entry.delete(0, "end")
                    self.member_entry.insert(0, data["member_card"] or "")
                    self._query_member()
                
                self._refresh_tree()
                dialog.destroy()
                messagebox.showinfo("成功", "调单成功")
            else:
                messagebox.showerror("错误", load_result["message"])
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent", height=50)
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        btn_frame.pack_propagate(False)
        
        ctk.CTkButton(btn_frame, text="确定", width=120, height=36, command=on_select).pack(side="left", padx=(80, 10), pady=7)
        ctk.CTkButton(btn_frame, text="取消", width=120, height=36, fg_color=COLORS["gray"], command=dialog.destroy).pack(side="left", pady=7)

    def _cancel_order(self):
        """撤单"""
        from logic.cashier_hang_cancel import cancel_order
        
        if not self.order_items and not self.current_order_id:
            messagebox.showinfo("提示", "当前没有订单")
            return
        
        if not messagebox.askyesno("确认", "确定要撤销当前订单吗？"):
            return
        
        # 如果是调单来的订单，更新数据库状态
        if self.current_order_id:
            result = cancel_order(self.current_order_id)
            if not result["success"]:
                messagebox.showerror("错误", result["message"])
                return
        
        self._reset_order()
        messagebox.showinfo("成功", "撤单成功")
    
    def _checkout(self):
        """结账"""
        from logic.cashier_logic import create_order
        from logic.cashier_hang_cancel import resume_order
        from utils.print_utils import generate_receipt, print_receipt
        
        if not self.order_items:
            messagebox.showwarning("提示", "请先添加商品")
            return
        
        pay_method = self.pay_method.get()
        member_id = self.current_member["member_id"] if self.current_member else None
        
        # 如果是调单来的订单，使用resume_order
        if self.current_order_id:
            result = resume_order(self.current_order_id, self.cashier_id, pay_method)
        else:
            result = create_order(self.cashier_id, member_id, self.order_items, pay_method)
        
        if not result["success"]:
            messagebox.showerror("错误", result["message"])
            return
        
        order_data = result["data"]
        
        # 生成并保存小票
        member_info = None
        if self.current_member:
            member_info = {
                "card_no": self.current_member["card_no"],
                "name": self.current_member["name"],
                "total_points": self.current_member["total_points"]
            }
        
        receipt = generate_receipt(
            order_info={
                "order_no": order_data["order_no"],
                "total_amount": order_data["total_amount"],
                "discount_amount": order_data["discount_amount"],
                "actual_amount": order_data["actual_amount"],
                "points_earned": order_data["points_earned"],
                "create_time": ""
            },
            order_details=order_data["items"],
            member_info=member_info,
            cashier_name=""
        )
        
        print_receipt(receipt, order_data["order_no"])
        
        # 弹窗显示小票
        self._show_receipt_dialog(receipt, order_data)
        self._reset_order()
    
    def _show_receipt_dialog(self, receipt_text, order_data):
        """显示小票弹窗"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("结账成功 - 小票")
        dialog.geometry("420x720")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 标题
        ctk.CTkLabel(
            dialog, text="✅ 结账成功",
            font=("微软雅黑", 18, "bold"),
            text_color=COLORS["success"]
        ).pack(pady=(20, 10))
        
        # 金额信息
        info_frame = ctk.CTkFrame(dialog, fg_color=COLORS["light_gray"], corner_radius=8)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            info_frame, text=f"订单号: {order_data['order_no']}",
            font=("微软雅黑", 12), text_color=COLORS["text_dark"]
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            info_frame, text=f"实付金额: ¥{order_data['actual_amount']:.2f}",
            font=("微软雅黑", 16, "bold")
        ).pack(pady=(0, 10))
        
        if order_data["points_earned"] > 0:
            ctk.CTkLabel(
                info_frame, text=f"获得积分: +{order_data['points_earned']}",
                font=FONTS["body"], text_color=COLORS["info"]
            ).pack(pady=(0, 10))
        
        # 小票内容
        ctk.CTkLabel(dialog, text="小票预览", font=FONTS["subtitle"]).pack(anchor="w", padx=20, pady=(10, 5))
        
        receipt_box = ctk.CTkTextbox(dialog, font=("Consolas", 11), width=380, height=350)
        receipt_box.pack(padx=20, pady=(0, 10))
        receipt_box.insert("1.0", receipt_text)
        receipt_box.configure(state="disabled")
        
        # 按钮
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent", height=60)
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        btn_frame.pack_propagate(False)
        
        ctk.CTkButton(
            btn_frame, text="确定", width=150, height=40,
            font=FONTS["body"], fg_color=COLORS["success"],
            command=dialog.destroy
        ).pack(side="left", padx=(50, 10), pady=10)
        
        ctk.CTkButton(
            btn_frame, text="打印", width=150, height=40,
            font=FONTS["body"], fg_color=COLORS["info"],
            command=lambda: messagebox.showinfo("提示", f"小票已保存至:\nreceipts/receipt_{order_data['order_no']}.txt")
        ).pack(side="left", pady=10)

    def _reset_order(self):
        """重置订单状态"""
        self.order_items.clear()
        self.current_member = None
        self.discount_rate = 1.0
        self.current_order_id = None
        
        self.member_entry.delete(0, "end")
        self.member_info_label.configure(text="未选择会员（散客）")
        self.discount_label.configure(text="无")
        
        self._refresh_tree()
