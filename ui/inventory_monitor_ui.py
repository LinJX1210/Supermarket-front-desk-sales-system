# -*- coding: utf-8 -*-
"""库存监控界面"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from logic.inventory_logic import InventoryLogic
from logic.inventory_warning import InventoryWarning


class InventoryMonitorUI(ctk.CTkFrame):
    """库存监控界面"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.logic = InventoryLogic()
        self.warning = InventoryWarning()
        self.setup_ui()
        self.load_inventory()
    
    def setup_ui(self):
        """初始化界面"""
        # 顶部操作栏
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(top_frame, text="库存监控", font=("", 18, "bold")).pack(side="left", padx=10)
        
        # 搜索框
        self.search_entry = ctk.CTkEntry(top_frame, width=200, placeholder_text="搜索商品名称/条码")
        self.search_entry.pack(side="left", padx=20)
        
        ctk.CTkButton(top_frame, text="查询", width=80, command=self.search_inventory).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="刷新", width=80, command=self.refresh_and_check).pack(side="left", padx=5)
        
        # 筛选按钮
        filter_frame = ctk.CTkFrame(top_frame)
        filter_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(filter_frame, text="全部", width=60, command=self.load_inventory).pack(side="left", padx=2)
        ctk.CTkButton(filter_frame, text="库存预警", width=80, fg_color="#e74c3c", hover_color="#c0392b",
                     command=self.show_stock_warning).pack(side="left", padx=2)
        ctk.CTkButton(filter_frame, text="货架预警", width=80, fg_color="#f39c12", hover_color="#d68910",
                     command=self.show_shelf_warning).pack(side="left", padx=2)
        
        # 统计信息
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="x", padx=20, pady=5)
        
        self.total_label = ctk.CTkLabel(stats_frame, text="商品总数: 0")
        self.total_label.pack(side="left", padx=20)
        
        self.warning_label = ctk.CTkLabel(stats_frame, text="预警商品: 0", text_color="#e74c3c")
        self.warning_label.pack(side="left", padx=20)
        
        self.sufficient_label = ctk.CTkLabel(stats_frame, text="库存充足: 0", text_color="#27ae60")
        self.sufficient_label.pack(side="left", padx=20)
        
        # 库存列表
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("ID", "条码", "商品名称", "库存数量", "货架数量", "库存预警线", "货架预警线", "状态")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("条码", text="条码")
        self.tree.heading("商品名称", text="商品名称")
        self.tree.heading("库存数量", text="库存数量")
        self.tree.heading("货架数量", text="货架数量")
        self.tree.heading("库存预警线", text="库存预警线")
        self.tree.heading("货架预警线", text="货架预警线")
        self.tree.heading("状态", text="状态")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("条码", width=120, anchor="center")
        self.tree.column("商品名称", width=200)
        self.tree.column("库存数量", width=80, anchor="center")
        self.tree.column("货架数量", width=80, anchor="center")
        self.tree.column("库存预警线", width=90, anchor="center")
        self.tree.column("货架预警线", width=90, anchor="center")
        self.tree.column("状态", width=80, anchor="center")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # 底部操作区
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", padx=20, pady=10)
        
        # 补货操作
        ctk.CTkLabel(bottom_frame, text="补货数量:").pack(side="left", padx=10)
        self.restock_entry = ctk.CTkEntry(bottom_frame, width=100)
        self.restock_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(bottom_frame, text="入库补货", width=100, fg_color="#27ae60", hover_color="#229954",
                     command=self.restock).pack(side="left", padx=10)
        
        ctk.CTkButton(bottom_frame, text="上架补货", width=100, fg_color="#3498db", hover_color="#2980b9",
                     command=self.restock_shelf).pack(side="left", padx=10)
        
        # 预警设置
        ctk.CTkLabel(bottom_frame, text="设置预警线:").pack(side="left", padx=(30, 10))
        self.warning_entry = ctk.CTkEntry(bottom_frame, width=80)
        self.warning_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(bottom_frame, text="设置库存预警", width=100,
                     command=self.set_stock_warning).pack(side="left", padx=5)
        ctk.CTkButton(bottom_frame, text="设置货架预警", width=100,
                     command=self.set_shelf_warning).pack(side="left", padx=5)
        
        self.selected_goods_id = None
    
    def load_inventory(self):
        """加载库存数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        inventory_list = self.logic.get_all_inventory()
        self.display_inventory(inventory_list)
    
    def refresh_and_check(self):
        """刷新并检查库存状态，触发预警通知"""
        # 检查库存状态并创建通知
        self.warning.check_all_inventory()
        # 重新加载数据
        self.load_inventory()
        # 尝试刷新主窗口的通知计数
        try:
            main_window = self.winfo_toplevel()
            if hasattr(main_window, '_refresh_notification_count'):
                main_window._refresh_notification_count()
        except:
            pass
    
    def display_inventory(self, inventory_list):
        """显示库存数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        warning_count = 0
        sufficient_count = 0
        
        status_map = {
            'sufficient': '充足',
            'stock_shortage': '库存不足',
            'shelf_shortage': '货架不足',
            'stock_warning': '库存预警',
            'shelf_warning': '货架预警',
            'both_warning': '双重预警',
            'warning': '预警',
            'shortage': '缺货'
        }
        
        for inv in inventory_list:
            stock_status = inv.get('stock_status', 'sufficient')
            status = status_map.get(stock_status, stock_status)
            
            # 根据实际数量判断状态
            stock_num = inv.get('stock_num', 0)
            on_shelf_num = inv.get('on_shelf_num', 0)
            stock_warning = inv.get('stock_warning', 10)
            shelf_warning = inv.get('shelf_warning', 5)
            
            if stock_num <= 0:
                status = '库存不足'
                warning_count += 1
            elif stock_num <= stock_warning:
                status = '库存预警'
                warning_count += 1
            elif on_shelf_num <= shelf_warning:
                status = '货架预警'
                warning_count += 1
            else:
                status = '充足'
                sufficient_count += 1
            
            self.tree.insert("", "end", values=(
                inv['goods_id'],
                inv.get('barcode', ''),
                inv.get('goods_name', ''),
                inv['stock_num'],
                inv['on_shelf_num'],
                inv['stock_warning'],
                inv['shelf_warning'],
                status
            ))
        
        self.total_label.configure(text=f"商品总数: {len(inventory_list)}")
        self.warning_label.configure(text=f"预警商品: {warning_count}")
        self.sufficient_label.configure(text=f"库存充足: {sufficient_count}")
    
    def search_inventory(self):
        """搜索库存"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_inventory()
            return
        
        inventory_list = self.logic.search_inventory(keyword)
        self.display_inventory(inventory_list)
    
    def show_stock_warning(self):
        """显示库存预警商品"""
        warning_list = self.warning.get_stock_warning_list()
        self.display_inventory(warning_list)
    
    def show_shelf_warning(self):
        """显示货架预警商品"""
        warning_list = self.warning.get_shelf_warning_list()
        self.display_inventory(warning_list)
    
    def on_select(self, event):
        """选中商品"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_goods_id = item['values'][0]
    
    def restock(self):
        """入库补货"""
        if not self.selected_goods_id:
            messagebox.showwarning("提示", "请先选择商品")
            return
        
        try:
            quantity = int(self.restock_entry.get())
            if quantity <= 0:
                raise ValueError()
        except:
            messagebox.showwarning("提示", "请输入有效的补货数量")
            return
        
        result = self.logic.add_stock(self.selected_goods_id, quantity)
        if isinstance(result, dict):
            # 返回字典格式
            if result.get('success'):
                messagebox.showinfo("成功", result.get('message', '入库成功'))
                self.load_inventory()
                self.restock_entry.delete(0, "end")
            else:
                messagebox.showerror("错误", result.get('message', '入库失败'))
        else:
            # 返回元组格式 (success, msg)
            success, msg = result
            if success:
                messagebox.showinfo("成功", msg)
                self.load_inventory()
                self.restock_entry.delete(0, "end")
            else:
                messagebox.showerror("错误", msg)
    
    def restock_shelf(self):
        """上架补货"""
        if not self.selected_goods_id:
            messagebox.showwarning("提示", "请先选择商品")
            return
        
        try:
            quantity = int(self.restock_entry.get())
            if quantity <= 0:
                raise ValueError()
        except:
            messagebox.showwarning("提示", "请输入有效的上架数量")
            return
        
        success, msg = self.logic.move_to_shelf(self.selected_goods_id, quantity)
        if success:
            messagebox.showinfo("成功", msg)
            self.load_inventory()
            self.restock_entry.delete(0, "end")
        else:
            messagebox.showerror("错误", msg)
    
    def set_stock_warning(self):
        """设置库存预警线"""
        if not self.selected_goods_id:
            messagebox.showwarning("提示", "请先选择商品")
            return
        
        try:
            warning_num = int(self.warning_entry.get())
            if warning_num < 0:
                raise ValueError()
        except:
            messagebox.showwarning("提示", "请输入有效的预警数量")
            return
        
        success, msg = self.logic.set_stock_warning(self.selected_goods_id, warning_num)
        if success:
            messagebox.showinfo("成功", msg)
            self.load_inventory()
            self.warning_entry.delete(0, "end")
        else:
            messagebox.showerror("错误", msg)
    
    def set_shelf_warning(self):
        """设置货架预警线"""
        if not self.selected_goods_id:
            messagebox.showwarning("提示", "请先选择商品")
            return
        
        try:
            warning_num = int(self.warning_entry.get())
            if warning_num < 0:
                raise ValueError()
        except:
            messagebox.showwarning("提示", "请输入有效的预警数量")
            return
        
        success, msg = self.logic.set_shelf_warning(self.selected_goods_id, warning_num)
        if success:
            messagebox.showinfo("成功", msg)
            self.load_inventory()
            self.warning_entry.delete(0, "end")
        else:
            messagebox.showerror("错误", msg)
