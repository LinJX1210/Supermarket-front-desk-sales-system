# -*- coding: utf-8 -*-
"""
系统主界面 - 组员1负责
"""

import customtkinter as ctk


class MainApp(ctk.CTk):
    """主应用程序窗口"""
    
    def __init__(self):
        super().__init__()
        self.title("超市前台销售系统")
        self.geometry("1200x800")
        # TODO: 实现主界面布局
