# -*- coding: utf-8 -*-
"""
超市前台销售系统 - 程序入口
"""

import customtkinter as ctk

# 设置全局主题
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def main():
    """程序入口"""
    try:
        # 从登录界面启动
        from ui.login_ui import LoginUI
        app = LoginUI()
        app.mainloop()
    except ImportError:
        # 如果登录界面不可用，直接启动主界面
        from ui.main_ui import MainApp
        app = MainApp()
        app.mainloop()


if __name__ == "__main__":
    main()
