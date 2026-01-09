# -*- coding: utf-8 -*-
"""商品分类管理界面"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from logic.goods_category_logic import GoodsCategoryLogic


class GoodsCategoryUI(ctk.CTkFrame):
    """商品分类管理界面"""
    
    def __init__(self, parent, on_select_callback=None):
        super().__init__(parent)
        self.logic = GoodsCategoryLogic()
        self.selected_category = None
        self.on_select_callback = on_select_callback  # 双击回调
        self.setup_ui()
        self.load_categories()
    
    def setup_ui(self):
        """初始化界面"""
        # 顶部操作栏
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(top_frame, text="商品分类管理", font=("", 18, "bold")).pack(side="left", padx=10)
        
        ctk.CTkButton(top_frame, text="刷新", width=80, command=self.load_categories).pack(side="right", padx=5)
        ctk.CTkButton(top_frame, text="删除", width=80, fg_color="#e74c3c", hover_color="#c0392b",
                     command=self.delete_category).pack(side="right", padx=5)
        ctk.CTkButton(top_frame, text="修改", width=80, fg_color="#3498db", hover_color="#2980b9",
                     command=self.edit_category).pack(side="right", padx=5)
        ctk.CTkButton(top_frame, text="+ 新增分类", width=100, fg_color="#27ae60", hover_color="#229954",
                     command=self.add_category).pack(side="right", padx=5)
        
        # 主内容区
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 左侧：分类树
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(left_frame, text="分类结构 (课-类-种)", font=("", 14)).pack(pady=10)
        
        # 分类列表
        columns = ("ID", "分类名称", "级别", "上级分类", "排序")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=20)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("分类名称", text="分类名称")
        self.tree.heading("级别", text="级别")
        self.tree.heading("上级分类", text="上级分类")
        self.tree.heading("排序", text="排序")
        
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("分类名称", width=200)
        self.tree.column("级别", width=80, anchor="center")
        self.tree.column("上级分类", width=150)
        self.tree.column("排序", width=60, anchor="center")
        
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_double_click)  # 双击查看商品
        
        # 右侧：分类详情/编辑
        right_frame = ctk.CTkFrame(content_frame, width=320)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)
        
        ctk.CTkLabel(right_frame, text="分类信息", font=("", 14)).pack(pady=10)
        
        # 提示文字
        ctk.CTkLabel(right_frame, text="💡 双击分类可查看该分类下的商品", 
                    font=("", 10), text_color="#888").pack(pady=(0, 5))
        
        form_frame = ctk.CTkFrame(right_frame)
        form_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(form_frame, text="分类名称:").pack(anchor="w", padx=10, pady=(10, 0))
        self.name_entry = ctk.CTkEntry(form_frame, width=260)
        self.name_entry.pack(padx=10, pady=5)
        
        ctk.CTkLabel(form_frame, text="级别:").pack(anchor="w", padx=10, pady=(10, 0))
        self.level_combo = ctk.CTkComboBox(form_frame, width=260, 
                                           values=["1-课(大类)", "2-类(中类)", "3-种(小类)"])
        self.level_combo.pack(padx=10, pady=5)
        self.level_combo.set("1-课(大类)")
        
        ctk.CTkLabel(form_frame, text="上级分类:").pack(anchor="w", padx=10, pady=(10, 0))
        self.parent_combo = ctk.CTkComboBox(form_frame, width=260, values=["无"])
        self.parent_combo.pack(padx=10, pady=5)
        self.parent_combo.set("无")
        
        ctk.CTkLabel(form_frame, text="排序号:").pack(anchor="w", padx=10, pady=(10, 0))
        self.sort_entry = ctk.CTkEntry(form_frame, width=260)
        self.sort_entry.pack(padx=10, pady=5)
        self.sort_entry.insert(0, "1")
        
        # 级别变化时更新上级分类选项
        self.level_combo.configure(command=self.on_level_change)
    
    def load_categories(self):
        """加载分类数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        categories = self.logic.get_all_categories()
        level_names = {1: "课(大类)", 2: "类(中类)", 3: "种(小类)"}
        
        for cat in categories:
            parent_name = cat.get('parent_name') or "无"
            level_text = level_names.get(cat['level'], str(cat['level']))
            indent = "  " * (cat['level'] - 1)
            
            self.tree.insert("", "end", values=(
                cat['category_id'],
                indent + cat['category_name'],
                level_text,
                parent_name,
                cat['sort_order']
            ))
        
        self.update_parent_options()
    
    def update_parent_options(self):
        """更新上级分类选项"""
        level_text = self.level_combo.get()
        level = int(level_text[0]) if level_text else 1
        
        if level == 1:
            self.parent_combo.configure(values=["无"])
            self.parent_combo.set("无")
        else:
            parent_level = level - 1
            parents = self.logic.get_categories_by_level(parent_level)
            options = ["无"] + [f"{p['category_id']}-{p['category_name']}" for p in parents]
            self.parent_combo.configure(values=options)
            self.parent_combo.set("无")
    
    def on_level_change(self, value):
        """级别变化时更新上级分类"""
        self.update_parent_options()
    
    def on_select(self, event):
        """选中分类"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            self.selected_category = values[0]
            self.selected_category_name = values[1].strip()
            
            # 填充表单
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, values[1].strip())
            
            level_map = {"课(大类)": "1-课(大类)", "类(中类)": "2-类(中类)", "种(小类)": "3-种(小类)"}
            self.level_combo.set(level_map.get(values[2], "1-课(大类)"))
            
            self.update_parent_options()
            if values[3] != "无":
                self.parent_combo.set(values[3])
            
            self.sort_entry.delete(0, "end")
            self.sort_entry.insert(0, str(values[4]))
    
    def on_double_click(self, event):
        """双击分类查看商品"""
        if self.selected_category and self.on_select_callback:
            self.on_select_callback(self.selected_category, self.selected_category_name)
    
    def add_category(self):
        """新增分类"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入分类名称")
            return
        
        level = int(self.level_combo.get()[0])
        parent_text = self.parent_combo.get()
        parent_id = None
        if parent_text != "无" and "-" in parent_text:
            parent_id = int(parent_text.split("-")[0])
        
        sort_order = int(self.sort_entry.get() or 1)
        
        success, msg = self.logic.add_category(name, parent_id, level, sort_order)
        if success:
            messagebox.showinfo("成功", msg)
            self.load_categories()
            self.clear_form()
        else:
            messagebox.showerror("错误", msg)
    
    def edit_category(self):
        """修改分类"""
        if not self.selected_category:
            messagebox.showwarning("提示", "请先选择要修改的分类")
            return
        
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入分类名称")
            return
        
        sort_order = int(self.sort_entry.get() or 1)
        
        success, msg = self.logic.update_category(self.selected_category, name, sort_order)
        if success:
            messagebox.showinfo("成功", msg)
            self.load_categories()
        else:
            messagebox.showerror("错误", msg)
    
    def delete_category(self):
        """删除分类"""
        if not self.selected_category:
            messagebox.showwarning("提示", "请先选择要删除的分类")
            return
        
        if not messagebox.askyesno("确认", "确定要删除该分类吗？\n注意：有子分类或商品的分类无法删除"):
            return
        
        success, msg = self.logic.delete_category(self.selected_category)
        if success:
            messagebox.showinfo("成功", msg)
            self.load_categories()
            self.clear_form()
        else:
            messagebox.showerror("错误", msg)
    
    def clear_form(self):
        """清空表单"""
        self.selected_category = None
        self.name_entry.delete(0, "end")
        self.level_combo.set("1-课(大类)")
        self.parent_combo.set("无")
        self.sort_entry.delete(0, "end")
        self.sort_entry.insert(0, "1")
