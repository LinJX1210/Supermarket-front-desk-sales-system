# -*- coding: utf-8 -*-
"""
会员规则管理界面 - 组员3负责
"""

import customtkinter as ctk
from tkinter import messagebox
from logic.member_rule_logic import MemberRuleLogic

COLORS = {
    "primary": "#4A90D9",
    "card_bg": "#FFFFFF",
    "text_dark": "#2C3E50",
    "success": "#27AE60",
    "gray": "#95A5A6",
    "border": "#E0E0E0",
}

FONTS = {
    "title": ("微软雅黑", 16, "bold"),
    "subtitle": ("微软雅黑", 14, "bold"),
    "body": ("微软雅黑", 13),
}


class MemberRuleUI(ctk.CTkFrame):
    """会员规则管理界面"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.logic = MemberRuleLogic()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_header()
        self._create_rules_panel()
        self._load_rules()
    
    def _create_header(self):
        """标题栏"""
        header = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        ctk.CTkLabel(header, text="会员规则设置", font=FONTS["title"], 
                    text_color=COLORS["text_dark"]).pack(side="left", padx=20, pady=15)
        
        ctk.CTkButton(header, text="保存设置", width=100, height=36,
            font=FONTS["body"], fg_color=COLORS["success"],
            command=self._save_settings).pack(side="right", padx=20, pady=15)
    
    def _create_rules_panel(self):
        """规则设置面板"""
        panel = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        panel.grid(row=1, column=0, sticky="nsew")
        
        self.level_frames = {}
        levels = [
            ("普通会员", "normal", "#95A5A6"),
            ("银卡会员", "silver", "#BDC3C7"),
            ("金卡会员", "gold", "#F1C40F"),
        ]
        
        for level_name, level_code, color in levels:
            frame = ctk.CTkFrame(panel, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=15)
            
            # 标题
            title_row = ctk.CTkFrame(frame, fg_color="transparent")
            title_row.pack(fill="x")
            ctk.CTkLabel(title_row, text="●", font=("微软雅黑", 16), 
                        text_color=color).pack(side="left")
            ctk.CTkLabel(title_row, text=level_name, font=FONTS["subtitle"], 
                        text_color=COLORS["text_dark"]).pack(side="left", padx=(8, 0))
            
            # 设置项
            settings = ctk.CTkFrame(frame, fg_color="#F8F9FA", corner_radius=8)
            settings.pack(fill="x", pady=(10, 0))
            
            row1 = ctk.CTkFrame(settings, fg_color="transparent")
            row1.pack(fill="x", padx=15, pady=(12, 8))
            ctk.CTkLabel(row1, text="升级最低消费", font=FONTS["body"], 
                        text_color=COLORS["gray"]).pack(side="left")
            consume_entry = ctk.CTkEntry(row1, width=100, height=32, font=FONTS["body"])
            consume_entry.pack(side="right")
            ctk.CTkLabel(row1, text="元", font=FONTS["body"], 
                        text_color=COLORS["gray"]).pack(side="right", padx=(0, 8))
            
            row2 = ctk.CTkFrame(settings, fg_color="transparent")
            row2.pack(fill="x", padx=15, pady=(8, 12))
            ctk.CTkLabel(row2, text="折扣比例", font=FONTS["body"], 
                        text_color=COLORS["gray"]).pack(side="left")
            discount_entry = ctk.CTkEntry(row2, width=100, height=32, font=FONTS["body"])
            discount_entry.pack(side="right")
            ctk.CTkLabel(row2, text="(0.95=95折)", font=("微软雅黑", 11), 
                        text_color=COLORS["gray"]).pack(side="right", padx=(0, 8))
            
            self.level_frames[level_code] = {
                "consume": consume_entry,
                "discount": discount_entry,
            }
    
    def _load_rules(self):
        """加载规则"""
        result = self.logic.get_all_rules()
        if not result['success']:
            return
        
        for rule in result['data']:
            level_code = rule['level_code']
            if level_code in self.level_frames:
                frames = self.level_frames[level_code]
                frames['consume'].delete(0, "end")
                frames['consume'].insert(0, str(rule['min_consume']))
                frames['discount'].delete(0, "end")
                frames['discount'].insert(0, str(rule['discount_rate']))
    
    def _save_settings(self):
        """保存设置"""
        try:
            rules_data = {}
            for level_code, frames in self.level_frames.items():
                consume = frames['consume'].get().strip()
                discount = frames['discount'].get().strip()
                
                rules_data[level_code] = {
                    'min_consume': float(consume) if consume else 0,
                    'min_points': 0,
                    'discount_rate': float(discount) if discount else 1.00,
                    'points_rate': 1,
                }
            
            result = self.logic.save_all_rules(rules_data)
            if result['success']:
                messagebox.showinfo("成功", result['message'])
            else:
                messagebox.showerror("失败", result['message'])
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的数字")
