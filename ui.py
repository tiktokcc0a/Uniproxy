import os
import sys
import tkinter as tk
import threading
from tkinter import ttk, messagebox
import webbrowser
from i18n import translations
from proxy_manager import ProxyManager

class UniproxyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Uniproxy Version 1.0")
        self.root.resizable(False, False)
        
        # 居中窗口，不修改尺寸
        self.center_window()
        
        # 设置窗口图标
        try:
            # 动态获取图标路径，支持 PyInstaller 打包环境
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)
            icon_path = os.path.join(base_path, "assets", "u.ico")
            self.root.iconbitmap(icon_path)
            print(f"图标路径: {icon_path}")
        except Exception as e:
            print(f"加载图标失败: {e}")

        # 初始化代理管理器
        self.proxy_manager = ProxyManager()

        # 当前语言
        self.current_lang = "zh-CN"
        self.languages = {
            "zh-CN": "中文 (简体)",
            "zh-TW": "中文 (繁體)",
            "en": "English",
            "ru": "Русский",
            "de": "Deutsch",
            "fr": "Français",
            "es": "Español",
            "ar": "العربية"
        }

        # 创建 UI 元素
        self.setup_ui()
        self.update_texts()

    def center_window(self):
        """将窗口居中显示在屏幕上，不修改窗口尺寸"""
        # 更新窗口，确保尺寸计算准确
        self.root.update_idletasks()
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # 获取窗口当前尺寸（由内容决定）
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        # 设置窗口位置，不改变尺寸
        self.root.geometry(f"+{x}+{y}")

    def setup_ui(self):
        # 主框架，设置边距和背景色
        self.main_frame = ttk.Frame(self.root, padding="15 15 15 15", style="Main.TFrame")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 顶部框架，用于语言选择（右上角）
        self.top_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        self.top_frame.grid(row=0, column=1, sticky=(tk.E), pady=5)

        # 语言选择（右上角，紧凑设计）
        self.lang_label = ttk.Label(self.top_frame, text="语言 / Language:", style="Label.TLabel")
        self.lang_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.lang_var = tk.StringVar(value="zh-CN")
        self.lang_combobox = ttk.Combobox(self.top_frame, textvariable=self.lang_var, 
                                          values=list(self.languages.values()), state='readonly', width=10, 
                                          style="Custom.TCombobox")
        self.lang_combobox.grid(row=0, column=1, sticky=tk.E)
        self.lang_combobox.bind("<<ComboboxSelected>>", self.change_language)

        # SOCKS5 代理信息输入框
        self.proxy_info_label = ttk.Label(self.main_frame, text="SOCKS5 代理信息:", style="Label.TLabel")
        self.proxy_info_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.proxy_info_entry = ttk.Entry(self.main_frame, width=38, style="Custom.TEntry")
        self.proxy_info_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        # API 链接输入框和“?”提示图标
        self.api_link_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        self.api_link_frame.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_link_label = ttk.Label(self.api_link_frame, text="API 链接:", style="Label.TLabel")
        self.api_link_label.grid(row=0, column=0, sticky=tk.W)
        self.api_help_label = ttk.Label(self.api_link_frame, text="?", style="Help.TLabel", cursor="question_arrow")
        self.api_help_label.grid(row=0, column=1, sticky=tk.W, padx=3)
        self.api_help_label.bind("<Enter>", lambda e: self.show_api_help())
        self.api_help_label.bind("<Leave>", lambda e: self.hide_api_help())
        self.api_link_entry = ttk.Entry(self.main_frame, width=38, style="Custom.TEntry")
        self.api_link_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        # 起始端口
        self.start_port_label = ttk.Label(self.main_frame, text="起始端口:", style="Label.TLabel")
        self.start_port_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.start_port_entry = ttk.Entry(self.main_frame, width=15, style="Custom.TEntry")
        self.start_port_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        # 代理数量
        self.port_count_label = ttk.Label(self.main_frame, text="代理数量:", style="Label.TLabel")
        self.port_count_label.grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.port_count_entry = ttk.Entry(self.main_frame, width=15, style="Custom.TEntry")
        self.port_count_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

        # 启动按钮
        self.start_button = ttk.Button(self.main_frame, text="启用代理", style="Button.TButton",
                                       command=lambda: threading.Thread(target=self.start_proxies).start())
        self.start_button.grid(row=5, column=0, columnspan=2, pady=15)

        # 超链接：使用教程 & 常见问题
        self.tutorial_link = ttk.Label(self.main_frame, text="使用教程 & 常见问题", style="Link.TLabel", cursor="hand2")
        self.tutorial_link.grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.tutorial_link.bind("<Button-1>", lambda e: webbrowser.open("https://5555.blog/archives/uniproxy"))

        # 设置样式
        self.setup_styles()

    def setup_styles(self):
        """设置 UI 样式，打造高级商务风"""
        style = ttk.Style()
        style.configure("Main.TFrame", background="#F0F2F5")
        style.configure("Label.TLabel", font=("Segoe UI", 10), background="#F0F2F5", foreground="#333333")
        style.configure("Button.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Link.TLabel", font=("Segoe UI", 9, "underline"), background="#F0F2F5", foreground="#0066CC")
        style.configure("Help.TLabel", font=("Segoe UI", 10, "bold"), background="#F0F2F5", foreground="#0066CC")
        style.configure("Custom.TEntry", font=("Segoe UI", 10), padding=5)
        style.configure("Custom.TCombobox", font=("Segoe UI", 9), padding=3)

        # 自定义输入框和选择栏样式，增加边框和阴影效果
        style.map("Custom.TEntry",
                  fieldbackground=[('focus', '#FFFFFF'), ('!focus', '#FFFFFF')],
                  foreground=[('focus', '#000000'), ('!focus', '#555555')])
        style.map("Custom.TCombobox",
                  fieldbackground=[('focus', '#FFFFFF'), ('!focus', '#FFFFFF')],
                  foreground=[('focus', '#000000'), ('!focus', '#555555')])
        
        # 调整选择栏下拉框样式
        style.configure("TComboboxPopup", font=("Segoe UI", 9))

    def show_api_help(self):
        """显示 API 链接帮助提示"""
        texts = translations.get(self.current_lang, translations["zh-CN"])
        self.api_help_tip = tk.Toplevel(self.root)
        self.api_help_tip.wm_overrideredirect(True)
        self.api_help_tip.geometry(f"300x80+{self.api_help_label.winfo_rootx()+20}+{self.api_help_label.winfo_rooty()+20}")
        ttk.Label(self.api_help_tip, text=texts["api_help_text"], wraplength=280, background="#FFFFE0", foreground="#000000", padding=5).pack()

    def hide_api_help(self):
        """隐藏 API 链接帮助提示"""
        if hasattr(self, 'api_help_tip'):
            self.api_help_tip.destroy()

    def change_language(self, event=None):
        """切换语言"""
        selected_lang_text = self.lang_var.get()
        self.current_lang = next(key for key, value in self.languages.items() if value == selected_lang_text)
        self.update_texts()

    def update_texts(self):
        """更新 UI 文本为当前语言"""
        texts = translations.get(self.current_lang, translations["zh-CN"])
        self.lang_label.config(text=texts["language_label"])
        self.proxy_info_label.config(text=texts["proxy_info_label"].split(' (')[0])  # 去掉括号内容
        self.api_link_label.config(text=texts["api_link_label"].split(' (')[0])  # 去掉括号内容
        self.start_port_label.config(text=texts["start_port_label"])
        self.port_count_label.config(text=texts["port_count_label"])
        self.start_button.config(text=texts["start_button"])
        self.tutorial_link.config(text=texts["tutorial_link"])
        self.root.title(texts["window_title"])

        # 更新输入框占位符文本（使用插入和删除来模拟 placeholder）
        self.update_placeholder(self.proxy_info_entry, texts["proxy_info_label"].split(' (')[1].rstrip(')') if '(' in texts["proxy_info_label"] else "")
        self.update_placeholder(self.api_link_entry, texts["api_link_label"].split(' (')[1].rstrip(')') if '(' in texts["api_link_label"] else "")

    def update_placeholder(self, entry, placeholder_text):
        """模拟输入框占位符文本"""
        def on_focus_in(event):
            if entry.get() == placeholder_text:
                entry.delete(0, tk.END)
                entry.config(foreground='#000000')

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder_text)
                entry.config(foreground='#888888')

        # 清除旧的事件绑定，避免重复绑定
        entry.unbind("<FocusIn>")
        entry.unbind("<FocusOut>")
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        # 如果当前输入框为空或内容是旧的占位符，则更新为新占位符
        if not entry.get() or entry.get() in [t["proxy_info_label"].split(' (')[1].rstrip(')') if '(' in t["proxy_info_label"] else "" for t in translations.values()] or entry.get() in [t["api_link_label"].split(' (')[1].rstrip(')') if '(' in t["api_link_label"] else "" for t in translations.values()]:
            entry.delete(0, tk.END)
            entry.insert(0, placeholder_text)
            entry.config(foreground='#888888')

    def start_proxies(self):
        """启动代理"""
        try:
            proxy_input = self.proxy_info_entry.get().strip()
            api_link = self.api_link_entry.get().strip()
            # 如果输入框内容是占位符，则清空
            texts = translations[self.current_lang]
            proxy_placeholder = texts["proxy_info_label"].split(' (')[1].rstrip(')') if '(' in texts["proxy_info_label"] else ""
            api_placeholder = texts["api_link_label"].split(' (')[1].rstrip(')') if '(' in texts["api_link_label"] else ""
            if proxy_input == proxy_placeholder:
                proxy_input = ""
            if api_link == api_placeholder:
                api_link = ""

            try:
                start_port = int(self.start_port_entry.get())
                port_count = int(self.port_count_entry.get())
            except ValueError:
                messagebox.showerror(translations[self.current_lang]["error_title"], 
                                     translations[self.current_lang]["input_error_numbers"])
                self.start_button.config(state="normal")
                return

            if not proxy_input and not api_link:
                messagebox.showerror(translations[self.current_lang]["error_title"], 
                                     translations[self.current_lang]["input_error_empty"])
                self.start_button.config(state="normal")
                return

            self.start_button.config(state="disabled")
            success_count, failed_ports = self.proxy_manager.start_proxies(
                proxy_input, api_link, start_port, port_count
            )
            self.start_button.config(state="normal")

            texts = translations[self.current_lang]
            if success_count == port_count:
                messagebox.showinfo(texts["success_title"], 
                                    texts["success_message"].format(success_count=success_count, start_port=start_port))
            elif success_count > 0:
                messagebox.showwarning(texts["partial_success_title"], 
                                       texts["partial_success_message"].format(success_count=success_count, 
                                                                               port_count=port_count, 
                                                                               start_port=start_port, 
                                                                               failed_ports=failed_ports))
            else:
                messagebox.showerror(texts["failure_title"], 
                                     texts["failure_message"].format(port_count=port_count, start_port=start_port))
        except Exception as e:
            error_msg = f"启动代理时发生错误: {str(e)}"
            print(error_msg)  # 打印到控制台（如果有）
            messagebox.showerror(translations[self.current_lang]["error_title"], error_msg)
            self.start_button.config(state="normal")

    def on_closing(self):
        """窗口关闭事件"""
        self.proxy_manager.stop_all_proxies()
        self.root.destroy()
