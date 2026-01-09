# -*- coding: utf-8 -*-
"""
商品管理界面 - 组员2负责
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from logic.goods_manage_logic import GoodsManageLogic
from logic.goods_category_logic import GoodsCategoryLogic

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
    "body": ("微软雅黑", 13),
}


class GoodsManageUI(ctk.CTkFrame):
    """商品管理界面"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.logic = GoodsManageLogic()
        self.category_logic = GoodsCategoryLogic()
        self.categories = []
        self.category_map = {}  # name -> id
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # 商品列表行可扩展
        
        self._load_categories()
        self._create_toolbar()
        self._create_goods_list()
        self._load_goods_list()
    
    def _load_categories(self):
        """加载分类数据"""
        self.categories = self.category_logic.get_all_categories()
        self.category_map = {"全部分类": None}
        for cat in self.categories:
            indent = "  " * (cat['level'] - 1)
            name = f"{indent}{cat['category_name']}"
            self.category_map[name] = cat['category_id']
    
    def _create_toolbar(self):
        """顶部工具栏"""
        toolbar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(toolbar, text="商品管理", font=FONTS["title"], 
                    text_color=COLORS["text_dark"]).pack(side="left", padx=20, pady=15)
        
        # 搜索和筛选区
        filter_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        filter_frame.pack(side="left", padx=20)
        
        # 分类筛选
        ctk.CTkLabel(filter_frame, text="分类:", font=FONTS["body"]).pack(side="left", padx=(0, 5))
        category_names = list(self.category_map.keys())
        self.category_combo = ctk.CTkComboBox(filter_frame, width=120, height=32,
            values=category_names, font=FONTS["body"], command=self._on_filter_change)
        self.category_combo.pack(side="left", padx=(0, 10))
        self.category_combo.set("全部分类")
        
        # 状态筛选
        ctk.CTkLabel(filter_frame, text="状态:", font=FONTS["body"]).pack(side="left", padx=(0, 5))
        self.status_combo = ctk.CTkComboBox(filter_frame, width=80, height=32,
            values=["全部", "在售", "下架"], font=FONTS["body"], command=self._on_filter_change)
        self.status_combo.pack(side="left", padx=(0, 10))
        self.status_combo.set("全部")
        
        # 搜索框
        self.search_entry = ctk.CTkEntry(filter_frame, width=150, height=32,
            placeholder_text="条码/商品名", font=FONTS["body"])
        self.search_entry.pack(side="left", padx=(0, 5))
        self.search_entry.bind("<Return>", lambda e: self._search_goods())
        
        ctk.CTkButton(filter_frame, text="查询", width=50, height=32,
            font=FONTS["body"], fg_color=COLORS["info"],
            command=self._search_goods).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(filter_frame, text="重置", width=50, height=32,
            font=FONTS["body"], fg_color=COLORS["gray"],
            command=self._reset_filter).pack(side="left")
        
        # 操作按钮栏 - 单独一行
        btn_frame = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        btn_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(btn_frame, text="操作:", font=FONTS["body"]).pack(side="left", padx=(20, 10), pady=8)
        
        ctk.CTkButton(btn_frame, text="+ 新增", width=70, height=30,
            font=FONTS["body"], fg_color=COLORS["success"],
            command=self._add_goods).pack(side="left", padx=(0, 8), pady=8)
        
        ctk.CTkButton(btn_frame, text="分类管理", width=80, height=30,
            font=FONTS["body"], fg_color="#9b59b6",
            command=self._show_category).pack(side="left", padx=(0, 8), pady=8)
        
        ctk.CTkButton(btn_frame, text="上架", width=55, height=30,
            font=FONTS["body"], fg_color=COLORS["primary"],
            command=self._on_shelf).pack(side="left", padx=(0, 8), pady=8)
        
        ctk.CTkButton(btn_frame, text="下架", width=55, height=30,
            font=FONTS["body"], fg_color=COLORS["danger"],
            command=self._off_shelf).pack(side="left", padx=(0, 8), pady=8)
        
        ctk.CTkButton(btn_frame, text="补货", width=55, height=30,
            font=FONTS["body"], fg_color="#e67e22",
            command=self._restock_goods).pack(side="left", padx=(0, 8), pady=8)
    
    def _create_goods_list(self):
        """商品列表"""
        list_card = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        list_card.grid(row=2, column=0, sticky="nsew")  # 改为row=2
        list_card.grid_rowconfigure(0, weight=1)
        list_card.grid_columnconfigure(0, weight=1)
        
        columns = ("goods_id", "barcode", "goods_name", "category", "sale_price", "stock", "status")
        self.tree = ttk.Treeview(list_card, columns=columns, show="headings", height=15)
        
        self.tree.heading("goods_id", text="ID")
        self.tree.heading("barcode", text="条码")
        self.tree.heading("goods_name", text="商品名称")
        self.tree.heading("category", text="分类")
        self.tree.heading("sale_price", text="售价")
        self.tree.heading("stock", text="库存")
        self.tree.heading("status", text="状态")
        
        self.tree.column("goods_id", width=50, anchor="center")
        self.tree.column("barcode", width=130, anchor="center")
        self.tree.column("goods_name", width=200)
        self.tree.column("category", width=120, anchor="center")
        self.tree.column("sale_price", width=80, anchor="center")
        self.tree.column("stock", width=60, anchor="center")
        self.tree.column("status", width=70, anchor="center")
        
        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(20, 0), pady=20)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=20, padx=(0, 10))
    
    def _load_goods_list(self, filters=None):
        """加载商品列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        result = self.logic.get_goods_list(filters)
        if result['success']:
            for goods in result['data']:
                self.tree.insert("", "end", values=(
                    goods['goods_id'], goods['barcode'], goods['goods_name'],
                    goods.get('category_name', ''), goods['sale_price_str'],
                    goods.get('stock_num', 0), goods['status_display']
                ))
    
    def _on_filter_change(self, value=None):
        """筛选条件变化"""
        self._search_goods()
    
    def _search_goods(self):
        """搜索/筛选商品"""
        filters = {}
        
        # 分类筛选
        category_name = self.category_combo.get()
        category_id = self.category_map.get(category_name)
        if category_id:
            filters['category_id'] = category_id
        
        # 状态筛选
        status = self.status_combo.get()
        if status != "全部":
            filters['status'] = status
        
        # 关键词搜索
        keyword = self.search_entry.get().strip()
        if keyword:
            filters['keyword'] = keyword
        
        self._load_goods_list(filters if filters else None)
    
    def _reset_filter(self):
        """重置筛选"""
        self.category_combo.set("全部分类")
        self.status_combo.set("全部")
        self.search_entry.delete(0, "end")
        self._load_goods_list()
    
    def _get_selected_goods(self):
        """获取选中商品"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个商品")
            return None
        values = self.tree.item(selected[0])['values']
        return {'goods_id': values[0], 'barcode': values[1], 'goods_name': values[2]}
    
    def _add_goods(self):
        """新增商品 - 弹出新增商品对话框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("新增商品")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 500) // 2
        y = (dialog.winfo_screenheight() - 600) // 2
        dialog.geometry(f"500x600+{x}+{y}")
        
        # 主容器
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        ctk.CTkLabel(main_frame, text="📦 新增商品", font=FONTS["title"],
                    text_color=COLORS["text_dark"]).pack(anchor="w", pady=(0, 20))
        
        # 表单容器
        form_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["card_bg"], corner_radius=10)
        form_frame.pack(fill="x", pady=(0, 20))
        
        # 条码
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(row1, text="商品条码 *", font=FONTS["body"], width=80, anchor="w").pack(side="left")
        barcode_entry = ctk.CTkEntry(row1, height=36, font=FONTS["body"], placeholder_text="输入或扫描商品条码")
        barcode_entry.pack(side="left", fill="x", expand=True)
        
        # 商品名称
        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(row2, text="商品名称 *", font=FONTS["body"], width=80, anchor="w").pack(side="left")
        name_entry = ctk.CTkEntry(row2, height=36, font=FONTS["body"], placeholder_text="输入商品名称")
        name_entry.pack(side="left", fill="x", expand=True)
        
        # 商品分类
        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(row3, text="商品分类 *", font=FONTS["body"], width=80, anchor="w").pack(side="left")
        
        # 只显示第三级分类（种）
        category_options = {}
        for cat in self.categories:
            if cat['level'] == 3:  # 只显示第三级分类
                category_options[cat['category_name']] = cat['category_id']
        
        category_names = list(category_options.keys()) if category_options else ["暂无分类"]
        category_combo = ctk.CTkComboBox(row3, height=36, font=FONTS["body"], values=category_names, state="readonly")
        category_combo.pack(side="left", fill="x", expand=True)
        if category_names:
            category_combo.set(category_names[0])
        
        # 单位
        row4 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row4.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(row4, text="计量单位", font=FONTS["body"], width=80, anchor="w").pack(side="left")
        unit_combo = ctk.CTkComboBox(row4, height=36, font=FONTS["body"], 
                                     values=["个", "瓶", "袋", "盒", "kg", "斤", "件", "包"], width=120)
        unit_combo.pack(side="left")
        unit_combo.set("个")
        
        # 是否散装
        is_weighted_var = ctk.BooleanVar(value=False)
        weighted_check = ctk.CTkCheckBox(row4, text="散装称重商品", font=FONTS["body"], 
                                         variable=is_weighted_var)
        weighted_check.pack(side="left", padx=(20, 0))
        
        # 成本价
        row5 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row5.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(row5, text="成本价", font=FONTS["body"], width=80, anchor="w").pack(side="left")
        cost_entry = ctk.CTkEntry(row5, height=36, font=FONTS["body"], width=120, placeholder_text="0.00")
        cost_entry.pack(side="left")
        ctk.CTkLabel(row5, text="元", font=FONTS["body"]).pack(side="left", padx=(5, 0))
        
        # 销售价
        row6 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row6.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(row6, text="销售价 *", font=FONTS["body"], width=80, anchor="w").pack(side="left")
        price_entry = ctk.CTkEntry(row6, height=36, font=FONTS["body"], width=120, placeholder_text="0.00")
        price_entry.pack(side="left")
        ctk.CTkLabel(row6, text="元", font=FONTS["body"]).pack(side="left", padx=(5, 0))
        
        # 库存预警值
        row7 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row7.pack(fill="x", padx=20, pady=(10, 15))
        ctk.CTkLabel(row7, text="库存预警", font=FONTS["body"], width=80, anchor="w").pack(side="left")
        warning_entry = ctk.CTkEntry(row7, height=36, font=FONTS["body"], width=80, placeholder_text="10")
        warning_entry.pack(side="left")
        ctk.CTkLabel(row7, text="（低于此数量时预警）", font=("微软雅黑", 11), 
                    text_color=COLORS["gray"]).pack(side="left", padx=(10, 0))
        
        # 提示信息
        ctk.CTkLabel(main_frame, text="* 为必填项，新增商品默认为下架状态，需手动上架", 
                    font=("微软雅黑", 11), text_color=COLORS["gray"]).pack(anchor="w", pady=(0, 10))
        
        # 按钮区
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        def on_submit():
            """提交新增商品"""
            # 获取表单数据
            barcode = barcode_entry.get().strip()
            goods_name = name_entry.get().strip()
            category_name = category_combo.get()
            unit = unit_combo.get()
            is_weighted = is_weighted_var.get()
            cost_str = cost_entry.get().strip()
            price_str = price_entry.get().strip()
            warning_str = warning_entry.get().strip()
            
            # 校验必填项
            if not barcode:
                messagebox.showwarning("提示", "请输入商品条码")
                barcode_entry.focus()
                return
            if not goods_name:
                messagebox.showwarning("提示", "请输入商品名称")
                name_entry.focus()
                return
            if not category_name or category_name == "暂无分类":
                messagebox.showwarning("提示", "请选择商品分类")
                return
            if not price_str:
                messagebox.showwarning("提示", "请输入销售价")
                price_entry.focus()
                return
            
            # 校验价格格式
            try:
                sale_price = float(price_str)
                if sale_price <= 0:
                    messagebox.showwarning("提示", "销售价必须大于0")
                    return
            except ValueError:
                messagebox.showwarning("提示", "请输入有效的销售价")
                return
            
            cost_price = 0
            if cost_str:
                try:
                    cost_price = float(cost_str)
                    if cost_price < 0:
                        messagebox.showwarning("提示", "成本价不能为负数")
                        return
                except ValueError:
                    messagebox.showwarning("提示", "请输入有效的成本价")
                    return
            
            stock_warning = 10
            if warning_str:
                try:
                    stock_warning = int(warning_str)
                    if stock_warning < 0:
                        stock_warning = 10
                except ValueError:
                    stock_warning = 10
            
            # 获取分类ID
            category_id = category_options.get(category_name)
            if not category_id:
                messagebox.showwarning("提示", "请选择有效的商品分类")
                return
            
            # 调用逻辑层新增商品
            goods_data = {
                'barcode': barcode,
                'goods_name': goods_name,
                'category_id': category_id,
                'unit': unit,
                'is_weighted': 1 if is_weighted else 0,
                'cost_price': cost_price,
                'sale_price': sale_price,
                'stock_warning': stock_warning
            }
            
            result = self.logic.add_goods(goods_data)
            
            if result['success']:
                messagebox.showinfo("成功", f"商品 [{goods_name}] 添加成功！\n商品ID: {result['data']}")
                dialog.destroy()
                self._load_goods_list()  # 刷新列表
            else:
                messagebox.showerror("失败", result['message'])
        
        ctk.CTkButton(btn_frame, text="确认添加", width=120, height=40,
                     font=FONTS["body"], fg_color=COLORS["success"],
                     command=on_submit).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(btn_frame, text="取消", width=80, height=40,
                     font=FONTS["body"], fg_color=COLORS["gray"],
                     command=dialog.destroy).pack(side="left")
    
    def _on_shelf(self):
        """上架"""
        goods = self._get_selected_goods()
        if not goods:
            return
        result = self.logic.on_shelf(goods['goods_id'])
        if result['success']:
            messagebox.showinfo("成功", result['message'])
            self._search_goods()
        else:
            messagebox.showerror("失败", result['message'])
    
    def _off_shelf(self):
        """下架"""
        goods = self._get_selected_goods()
        if not goods:
            return
        if not messagebox.askyesno("确认", f"确定下架 {goods['goods_name']} 吗？"):
            return
        result = self.logic.off_shelf(goods['goods_id'])
        if result['success']:
            messagebox.showinfo("成功", result['message'])
            self._search_goods()
        else:
            messagebox.showerror("失败", result['message'])
    
    def _show_category(self):
        """显示分类管理弹窗"""
        from ui.goods_category_ui import GoodsCategoryUI
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("商品分类管理 (双击分类查看商品)")
        dialog.geometry("800x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # 传入回调函数，双击分类时筛选商品
        category_ui = GoodsCategoryUI(dialog, on_select_callback=self._filter_by_category)
        category_ui.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.category_dialog = dialog
    
    def _filter_by_category(self, category_id, category_name):
        """按分类筛选商品"""
        # 关闭弹窗
        if hasattr(self, 'category_dialog') and self.category_dialog:
            self.category_dialog.destroy()
        
        # 刷新分类列表
        self._load_categories()
        category_names = list(self.category_map.keys())
        self.category_combo.configure(values=category_names)
        
        # 找到对应的分类名并设置
        for name, cid in self.category_map.items():
            if cid == category_id:
                self.category_combo.set(name)
                break
        
        # 筛选商品
        self._search_goods()
    
    def _restock_goods(self):
        """补货 - 弹出补货对话框"""
        goods = self._get_selected_goods()
        if not goods:
            return
        
        from logic.inventory_logic import InventoryLogic
        inv_logic = InventoryLogic()
        
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"补货 - {goods['goods_name']}")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 400) // 2
        y = (dialog.winfo_screenheight() - 350) // 2
        dialog.geometry(f"400x350+{x}+{y}")
        
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text=f"📦 {goods['goods_name']}", font=FONTS["title"],
                    text_color=COLORS["text_dark"]).pack(anchor="w", pady=(0, 15))
        
        # 获取当前库存信息
        inv_result = inv_logic.get_stock(goods['goods_id'])
        stock_num = 0
        shelf_num = 0
        if inv_result['success'] and inv_result['data']:
            stock_num = inv_result['data'].get('stock_num', 0)
            shelf_num = inv_result['data'].get('on_shelf_num', 0)
        
        # 显示当前库存
        info_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["card_bg"], corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(info_frame, text=f"仓库库存: {stock_num}", font=FONTS["body"]).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(info_frame, text=f"货架库存: {shelf_num}", font=FONTS["body"]).pack(anchor="w", padx=15, pady=(0, 10))
        
        # 补货数量输入
        qty_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        qty_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(qty_frame, text="补货数量:", font=FONTS["body"], width=80).pack(side="left")
        qty_entry = ctk.CTkEntry(qty_frame, height=36, font=FONTS["body"], width=100, placeholder_text="输入数量")
        qty_entry.pack(side="left", padx=(0, 10))
        
        # 操作按钮
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        def do_restock_warehouse():
            """入库补货（增加仓库库存）"""
            try:
                qty = int(qty_entry.get())
                if qty <= 0:
                    raise ValueError()
            except:
                messagebox.showwarning("提示", "请输入有效的补货数量")
                return
            
            result = inv_logic.add_stock(goods['goods_id'], qty)
            if result.get('success'):
                messagebox.showinfo("成功", result.get('message', '入库成功'))
                dialog.destroy()
                self._load_goods_list()
            else:
                messagebox.showerror("失败", result.get('message', '入库失败'))
        
        def do_restock_shelf():
            """上架补货（从仓库移到货架）"""
            try:
                qty = int(qty_entry.get())
                if qty <= 0:
                    raise ValueError()
            except:
                messagebox.showwarning("提示", "请输入有效的上架数量")
                return
            
            success, msg = inv_logic.move_to_shelf(goods['goods_id'], qty)
            if success:
                messagebox.showinfo("成功", msg)
                dialog.destroy()
                self._load_goods_list()
            else:
                messagebox.showerror("失败", msg)
        
        ctk.CTkButton(btn_frame, text="入库补货", width=100, height=36,
                     font=FONTS["body"], fg_color="#27ae60",
                     command=do_restock_warehouse).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(btn_frame, text="上架补货", width=100, height=36,
                     font=FONTS["body"], fg_color="#3498db",
                     command=do_restock_shelf).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(btn_frame, text="关闭", width=70, height=36,
                     font=FONTS["body"], fg_color=COLORS["gray"],
                     command=dialog.destroy).pack(side="left")
        
        # 提示说明
        ctk.CTkLabel(main_frame, text="入库补货: 增加仓库库存\n上架补货: 从仓库移到货架", 
                    font=("微软雅黑", 11), text_color=COLORS["gray"]).pack(anchor="w", pady=(15, 0))
