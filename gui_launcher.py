#!/usr/bin/env python3
"""
TFT卡牌统计GUI启动器
避免相对导入问题
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import json
from datetime import datetime
import sqlite3

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from capture import grab_fullscreen, grab_region
    from matching import load_templates_from_dir, match_template
    from database import TFTStatsDatabase
    from ocr_module import NumberOCR
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有依赖包")
    print("运行: pip install -r requirements.txt")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import numpy as np
except ImportError as e:
    print(f"matplotlib导入错误: {e}")
    print("请安装matplotlib: pip install matplotlib")
    sys.exit(1)


class TFTStatsGUI:
    """TFT卡牌统计GUI主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TFT卡牌统计系统")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')
        
        # 初始化变量
        self.is_running = False
        self.trigger_count = 0
        self.current_session_id = None
        self.monitor_index = 1
        self.threshold = 0.68
        self.templates_dir = "tft_units"
        self.enable_ocr = True
        self.selected_level = None
        
        # 新增：手动触发按钮状态控制
        self.manual_trigger_active = False
        self.manual_trigger_thread = None
        self.manual_trigger_event = threading.Event()
        
        # 新增：费用筛选控制
        self.selected_cost_filter = None
        
        # 初始化组件
        self.database = TFTStatsDatabase()
        self.ocr = None
        if self.enable_ocr:
            try:
                self.ocr = NumberOCR()
            except Exception as e:
                print(f"OCR初始化失败: {e}")
                self.enable_ocr = False
        
        # 创建界面
        self.create_widgets()
        self.setup_styles()
        
        # 从数据库获取最新的capture_sequence值并更新触发次数
        self.update_trigger_count_from_database()
        
        # 启动更新线程
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置样式
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='white')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='white')
        style.configure('Info.TLabel', font=('Arial', 10), foreground='white')
        style.configure('Success.TButton', font=('Arial', 10, 'bold'))
        style.configure('Warning.TButton', font=('Arial', 10, 'bold'))
        style.configure('Info.TButton', font=('Arial', 10))
    
    def create_widgets(self):
        """创建界面组件"""
        # 主标题
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(fill='x', padx=10, pady=5)
        
        title_label = tk.Label(title_frame, text="TFT Units Statistics", 
                              font=('Consola', 20, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack()
        
        # 顶部控制面板
        self.create_control_panel()
        
        # 数据表格
        self.create_data_table()
        
        # 图表区域
        self.create_charts_area()
        
        # 日志区域
        self.create_log_area()
    
    def create_control_panel(self):
        """创建顶部控制面板"""
        control_frame = tk.Frame(self.root, bg='#db7891', relief='raised', bd=2)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # 第一行：主要控制按钮
        row1 = tk.Frame(control_frame, bg='#db7891')
        row1.pack(padx=10, pady=5, anchor='center')
        
        # 开始/停止按钮
        self.start_stop_btn = tk.Button(row1, text="开始监控", command=self.toggle_monitoring,
                                       font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                                       width=15, height=2)
        self.start_stop_btn.pack(side='left', padx=5)
        
        # 手动触发按钮
        self.trigger_btn = tk.Button(row1, text="手动触发", command=self.manual_trigger,
                                    font=('Arial', 12), bg='#3498db', fg='white',
                                    width=15, height=2)
        self.trigger_btn.pack(side='left', padx=5)
        
        # 手动触发状态指示标签
        self.trigger_status_label = tk.Label(row1, text="", font=('Arial', 10), 
                                           fg='#f1c40f', bg='#db7891')
        self.trigger_status_label.pack(side='left', padx=5)
        
        # 记录保存按钮
        self.save_btn = tk.Button(row1, text="保存记录", command=self.save_records,
                                 font=('Arial', 12), bg='#f39c12', fg='white',
                                 width=15, height=2)
        self.save_btn.pack(side='left', padx=5)
        
        # 分享按钮
        self.share_btn = tk.Button(row1, text="分享数据", command=self.share_data,
                                  font=('Arial', 12), bg='#9b59b6', fg='white',
                                  width=15, height=2)
        self.share_btn.pack(side='left', padx=5)
        
        # 第二行：状态信息和参数设置
        row2 = tk.Frame(control_frame, bg='#db7891')
        row2.pack(padx=10, pady=5, anchor='center')
        
        # 当前触发次数
        tk.Label(row2, text="触发次数:", font=('Arial', 10), fg='white', bg='#34495e').pack(side='left', padx=5)
        self.trigger_count_label = tk.Label(row2, text="0", font=('Arial', 12, 'bold'), 
                                          fg='#f1c40f', bg='#34495e')
        self.trigger_count_label.pack(side='left', padx=5)
        
        # 匹配阈值设置
        tk.Label(row2, text="匹配阈值:", font=('Arial', 10), fg='white', bg='#34495e').pack(side='left', padx=20)
        self.threshold_var = tk.DoubleVar(value=self.threshold)
        threshold_scale = tk.Scale(row2, from_=0.5, to=1.0, resolution=0.01, 
                                 variable=self.threshold_var, orient='horizontal',
                                 bg='#34495e', fg='white', highlightthickness=0)
        threshold_scale.pack(side='left', padx=5)
        
        # 显示器选择
        tk.Label(row2, text="显示器:", font=('Arial', 10), fg='white', bg='#34495e').pack(side='left', padx=20)
        self.monitor_var = tk.IntVar(value=self.monitor_index)
        monitor_spin = tk.Spinbox(row2, from_=1, to=4, textvariable=self.monitor_var,
                                 width=5, bg='#34495e', fg='white')
        monitor_spin.pack(side='left', padx=5)
        
        # OCR开关
        self.ocr_var = tk.BooleanVar(value=self.enable_ocr)
        ocr_check = tk.Checkbutton(row2, text="启用OCR", variable=self.ocr_var,
                                  bg='#34495e', fg='white', selectcolor='#2c3e50')
        ocr_check.pack(side='left', padx=20)
    
    def update_trigger_count_from_database(self):
        """从数据库获取最新的capture_sequence值并更新触发次数标签"""
        try:
            latest_sequence = self.database.get_latest_capture_sequence()
            self.trigger_count = latest_sequence
            self.trigger_count_label.config(text=str(latest_sequence))
            print(f"✅ 从数据库更新触发次数: {latest_sequence}")
        except Exception as e:
            print(f"⚠️ 更新触发次数失败: {e}")
            self.trigger_count = 0
            self.trigger_count_label.config(text="0")
    
    def create_data_table(self):
        """创建数据表格"""
        table_frame = tk.Frame(self.root, bg='#2c3e50')
        table_frame.pack(fill='x', padx=10, pady=5)
        
        # 表格标题
        tk.Label(table_frame, text="刷新牌库次数统计", font=('Arial', 14, 'bold'), 
                fg='white', bg='#2c3e50').pack(pady=5)
        
        # 创建表格容器，使用网格布局确保对齐
        table_container = tk.Frame(table_frame, bg='#2c3e50')
        table_container.pack(expand=True, fill='both')
        
        # 使用网格布局来确保列对齐
        # 第一行：Level标签和数字按钮
        row1_frame = tk.Frame(table_container, bg='#34495e')
        row1_frame.pack(pady=2)
        
        # Level标签 - 第0列
        tk.Label(row1_frame, text="Level", font=('Arial', 12, 'bold'), 
                fg='white', bg='#34495e', width=8).grid(row=0, column=0, padx=2, pady=2)
        
        # 数字按钮 2-10 - 第1-9列
        self.level_buttons = {}
        for i, level in enumerate(range(2, 11), 1):
            btn = tk.Button(row1_frame, text=str(level), font=('Arial', 10, 'bold'),
                           bg='#3498db', fg='white', width=7, height=1,
                           command=lambda l=level: self.on_level_button_click(l))
            btn.grid(row=0, column=i, padx=2, pady=2)
            self.level_buttons[level] = btn
        
        # 第二行：Count标签和计数器
        row2_frame = tk.Frame(table_container, bg='#34495e')
        row2_frame.pack(pady=2)
        
        # Count标签 - 第0列
        tk.Label(row2_frame, text="Count", font=('Arial', 12, 'bold'), 
                fg='white', bg='#34495e', width=8).grid(row=0, column=0, padx=2, pady=2)
        
        # 计数器标签 2-10 - 第1-9列
        self.count_labels = {}
        for i, level in enumerate(range(2, 11), 1):
            label = tk.Label(row2_frame, text="0", font=('Arial', 12, 'bold'),
                            fg='#f1c40f', bg='#34495e', width=6, relief='sunken', bd=2)
            label.grid(row=0, column=i, padx=2, pady=2)
            self.count_labels[level] = label
        
        # 清空表格按钮
        # clear_btn = tk.Button(table_frame, text="清空统计", command=self.clear_table,
        #                      bg='#e74c3c', fg='white', font=('Arial', 10))
        # clear_btn.pack(side='right', padx=5, pady=5)
    
    def on_level_button_click(self, level):
        """处理Level按钮点击事件"""
        try:
            # 更新选中的Level值
            if self.selected_level == level:
                # 如果点击的是已选中的按钮，则取消选择
                self.selected_level = None
                self.level_buttons[level].config(bg='#3498db')  # 恢复默认颜色
                self.log_message(f"取消Level {level} 筛选")
            else:
                # 选择新的Level值
                # 恢复所有按钮的默认颜色
                for btn_level, btn in self.level_buttons.items():
                    btn.config(bg='#3498db')
                
                # 设置选中按钮的高亮颜色
                self.selected_level = level
                self.level_buttons[level].config(bg='#e74c3c')  # 红色高亮
                self.log_message(f"选择Level {level} 进行数据筛选")
            
            # 更新图表显示
            self.update_charts()
            
        except Exception as e:
            self.log_message(f"Level按钮点击错误: {e}")
    
    def reset_all_counts(self):
        """重置所有计数器为0"""
        try:
            for level in range(2, 11):
                if level in self.count_labels:
                    self.count_labels[level].config(text="0")
            self.log_message("所有Level计数器已重置为0")
        except Exception as e:
            self.log_message(f"重置计数器错误: {e}")
    
    def create_charts_area(self):
        """创建图表区域"""
        charts_frame = tk.Frame(self.root, bg='#2c3e50')
        charts_frame.pack(fill='both', expand=False, padx=10, pady=5)
        
        # 左侧饼图
        left_frame = tk.Frame(charts_frame, bg='#34495e', relief='raised', bd=2)
        left_frame.pack(side='left', fill='both', expand=False, padx=(0, 5))
        
        tk.Label(left_frame, text="卡牌费用分布", font=('Arial', 12, 'bold'), 
                fg='white', bg='#34495e').pack(pady=5)
        
        # 创建饼图
        self.fig_pie = Figure(figsize=(3, 3), facecolor='#34495e')
        self.ax_pie = self.fig_pie.add_subplot(111)
        self.ax_pie.set_facecolor('#34495e')
        
        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, left_frame)
        self.canvas_pie.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        
        # 右侧直方图
        right_frame = tk.Frame(charts_frame, bg='#34495e', relief='raised', bd=2)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        tk.Label(right_frame, text="棋子出现统计", font=('Arial', 12, 'bold'), 
                fg='white', bg='#34495e').pack(pady=5)
        
        # 创建直方图
        self.fig_line = Figure(figsize=(7, 3), facecolor='#34495e')
        self.ax_line = self.fig_line.add_subplot(111)
        self.ax_line.set_facecolor('#34495e')
        
        # 调整子图边距，减少两侧空白
        self.fig_line.subplots_adjust(left=0.05, right=0.99, top=0.99, bottom=0.15)
        
        self.canvas_line = FigureCanvasTkAgg(self.fig_line, right_frame)
        self.canvas_line.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        
        # 初始化图表
        self.init_charts()
    
    def create_log_area(self):
        """创建日志显示区域"""
        log_frame = tk.Frame(self.root, bg='#2c3e50')
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 日志标题
        log_header = tk.Frame(log_frame, bg='#34495e')
        log_header.pack(fill='x')
        
        tk.Label(log_header, text="运行日志", font=('Arial', 12, 'bold'), 
                fg='white', bg='#34495e').pack(side='left', padx=5, pady=2)
        
        # 清空日志按钮
        clear_log_btn = tk.Button(log_header, text="清空日志", command=self.clear_log,
                                 bg='#e74c3c', fg='white', font=('Arial', 10))
        clear_log_btn.pack(side='right', padx=5, pady=2)
        
        # 日志文本框
        self.log_text = tk.Text(log_frame, height=8, bg='#2c3e50', fg='#ecf0f1',
                               font=('Consolas', 9), wrap='word')
        log_scrollbar = tk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
        # 添加初始日志
        self.log_message("系统启动完成")
        self.log_message("=== TFT卡牌统计系统 ===")
        self.log_message("功能说明:")
        self.log_message("1. 点击'开始监控'启动连续监控模式")
        self.log_message("2. 在监控模式下，按D键可触发匹配")
        self.log_message("3. 所有结果自动保存到数据库")
        self.log_message("4. 支持实时统计图表显示")
        self.log_message("="*30)
    
    def init_charts(self):
        """初始化图表"""
        # 初始化饼图
        self.ax_pie.clear()
        self.ax_pie.set_facecolor('#34495e')

        if self.selected_level is not None:
            title = f'Level {self.selected_level} Units Cost Distribution'
        else:
            title = 'All Units Cost Distribution'
        
        self.ax_pie.text(0.5, 0.5, 'No Data', ha='center', va='center', 
                        transform=self.ax_pie.transAxes, color='white', fontsize=12)
        self.ax_pie.set_title(title, color='white', fontsize=12)
        self.canvas_pie.draw()
        
        # 初始化折线图
        self.ax_line.clear()
        self.ax_line.set_facecolor('#34495e')

        if self.selected_level is not None:
            title = f'Level {self.selected_level} Units Appearence Statistics'
        else:
            title = 'All Units Appearence Statistics'

        self.ax_line.text(0.5, 0.5, 'No Data', ha='center', va='center', 
                         transform=self.ax_line.transAxes, color='white', fontsize=12)
        self.ax_line.set_title(title, color='white', fontsize=12)
        self.ax_line.set_xlabel('Units Name', color='white')
        self.ax_line.set_ylabel('Count', color='white')
        self.canvas_line.draw()
    
    def toggle_monitoring(self):
        """切换监控状态"""
        if not self.is_running:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """开始监控"""
        self.is_running = True
        self.start_stop_btn.config(text="停止监控", bg='#e74c3c')
        self.trigger_btn.config(state='normal')
        
        # 重置手动触发按钮状态
        self.manual_trigger_active = False
        self.trigger_btn.config(text="手动触发", bg='#3498db')
        self.trigger_status_label.config(text="")
        
        # 开始新的会话
        self.current_session_id = self.database.start_session(
            self.templates_dir, self.threshold_var.get(), self.monitor_var.get()
        )

        # 重置所有计数器
        self.reset_all_counts()
        
        # 重置费用筛选
        self.selected_cost_filter = None
        
        self.log_message("开始监控...")
        self.log_message(f"会话ID: {self.current_session_id}")
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        self.start_stop_btn.config(text="开始监控", bg='#27ae60')
        self.trigger_btn.config(state='disabled')
        
        # 停止手动触发模式（如果正在运行）
        if self.manual_trigger_active:
            self.stop_manual_trigger_mode()
        
        # 停止键盘监听器
        self.stop_keyboard_listener()

        # 结束会话
        if self.current_session_id:
            self.database.end_session(self.current_session_id)
            self.log_message("="*30)
            self.log_message("📊 最终统计结果")
            self.log_message("="*30)
            self.print_session_summary()
            
            # 自动保存记录到log文件夹
            try:
                self.auto_save_records_on_stop()
            except Exception as e:
                self.log_message(f"⚠️ 自动保存记录失败: {e}")
        
        self.log_message("停止监控")
    
    def print_session_summary(self):
        """打印会话统计摘要"""
        try:
            if not self.current_session_id:
                return
            
            conn = sqlite3.connect(self.database.db_path)
            cursor = conn.cursor()
            
            # 获取总匹配数
            cursor.execute('''
                SELECT COUNT(*) as total_matches
                FROM matches 
                WHERE session_id = ?
            ''', (self.current_session_id,))
            total_matches = cursor.fetchone()[0]
            
            # 获取费用分布
            cursor.execute('''
                SELECT cost, COUNT(*) as count
                FROM matches 
                WHERE session_id = ?
                GROUP BY cost
                ORDER BY cost
            ''', (self.current_session_id,))
            cost_distribution = cursor.fetchall()
            
            conn.close()
            
            self.log_message(f"总匹配数: {total_matches}")
            if cost_distribution:
                self.log_message("费用分布:")
                for cost, count in cost_distribution:
                    self.log_message(f"  {cost}费: {count}张")
            
        except Exception as e:
            self.log_message(f"获取统计信息错误: {e}")
    
    def monitoring_loop(self):
        """连续监控循环 - 集成原有的continuous模式功能"""
        self.log_message("连续监控模式已启动")
        self.log_message("快捷键说明:")
        self.log_message("  D键     - 触发截图和模板匹配")
        self.log_message("  Ctrl+F1 - 退出程序")
        self.log_message("程序将持续运行，等待快捷键输入...")
        
        # 初始化OCR实例（如果启用）
        ocr = None
        if self.ocr_var.get():
            try:
                ocr = NumberOCR()
                self.log_message("✅ OCR识别器初始化成功")
            except Exception as e:
                self.log_message(f"⚠️ OCR识别器初始化失败: {e}")
                self.log_message("将禁用OCR功能")
        
        # 启动键盘监听器
        self.start_keyboard_listener()
        
        try:
            while self.is_running:
                # 等待触发事件或程序退出
                if hasattr(self, 'trigger_event') and self.trigger_event.wait(timeout=0.1):
                    self.trigger_event.clear()
                    if self.is_running:  # 确保程序仍在运行
                        # 执行匹配并记录结果
                        self.log_message("检测到D键触发，执行匹配...")
                        self.perform_matching()
                        
                        # 显示当前会话统计
                        self.log_message("="*30)
                        self.log_message("📊 当前会话统计")
                        self.log_message("="*30)
                        
                time.sleep(0.01)  # 减少CPU占用
                
        except Exception as e:
            self.log_message(f"监控循环错误: {e}")
        finally:
            self.stop_keyboard_listener()
            self.log_message("连续监控模式已停止")
    
    def start_keyboard_listener(self):
        """启动键盘监听器"""
        try:
            from pynput import keyboard
            
            def on_key_press(key):
                """键盘按键回调函数"""
                try:
                    # D 触发截图和匹配
                    if key == keyboard.KeyCode.from_char('d'):
                        if hasattr(self, 'trigger_event'):
                            self.trigger_event.set()
                        else:
                            # 如果没有trigger_event，直接执行匹配
                            self.manual_trigger()
                            
                except AttributeError:
                    pass
            
            def on_key_release(key):
                """键盘释放回调函数"""
                pass
            
            # 创建事件对象
            self.trigger_event = threading.Event()
            
            # 启动键盘监听器
            self.keyboard_listener = keyboard.Listener(
                on_press=on_key_press,
                on_release=on_key_release
            )
            self.keyboard_listener.start()
            
            self.log_message("✅ 键盘监听器已启动")
            
        except ImportError:
            self.log_message("⚠️ pynput未安装，无法使用键盘监听功能")
            self.log_message("请安装: pip install pynput")
        except Exception as e:
            self.log_message(f"⚠️ 键盘监听器启动失败: {e}")
    
    def stop_keyboard_listener(self):
        """停止键盘监听器"""
        try:
            if hasattr(self, 'keyboard_listener'):
                self.keyboard_listener.stop()
                self.log_message("键盘监听器已停止")
        except Exception as e:
            self.log_message(f"停止键盘监听器错误: {e}")
    
    def manual_trigger(self):
        """手动触发匹配 - 切换按下/释放状态"""
        if not self.is_running:
            messagebox.showwarning("警告", "请先开始监控")
            return
        
        try:
            if not self.manual_trigger_active:
                # 激活手动触发模式
                self.start_manual_trigger_mode()
            else:
                # 停止手动触发模式
                self.stop_manual_trigger_mode()
                
        except Exception as e:
            self.log_message(f"手动触发错误: {e}")
            messagebox.showerror("错误", f"手动触发失败: {e}")
    
    def start_manual_trigger_mode(self):
        """启动手动触发模式"""
        try:
            self.manual_trigger_active = True
            self.trigger_btn.config(text="停止触发", bg='#e74c3c')
            self.trigger_status_label.config(text="🟢 监听中 (按D键触发)")
            
            self.log_message("🟢 手动触发模式已启动")
            self.log_message("现在按D键将自动触发截图匹配")
            self.log_message("再次点击按钮可停止监听")
            
            # 启动手动触发监听线程
            self.manual_trigger_thread = threading.Thread(target=self.manual_trigger_listener_loop, daemon=True)
            self.manual_trigger_thread.start()
            
        except Exception as e:
            self.log_message(f"启动手动触发模式错误: {e}")
            self.manual_trigger_active = False
    
    def stop_manual_trigger_mode(self):
        """停止手动触发模式"""
        try:
            self.manual_trigger_active = False
            self.trigger_btn.config(text="手动触发", bg='#3498db')
            self.trigger_status_label.config(text="")
            
            # 设置事件以停止监听线程
            self.manual_trigger_event.set()
            
            self.log_message("🔴 手动触发模式已停止")
            
        except Exception as e:
            self.log_message(f"停止手动触发模式错误: {e}")
    
    def manual_trigger_listener_loop(self):
        """手动触发监听循环"""
        try:
            from pynput import keyboard
            
            def on_key_press(key):
                """键盘按键回调函数"""
                try:
                    # D 触发截图和匹配
                    if key == keyboard.KeyCode.from_char('d'):
                        if self.manual_trigger_active:
                            self.log_message("检测到D键，执行匹配...")
                            self.execute_single_trigger()
                            
                except AttributeError:
                    pass
            
            def on_key_release(key):
                """键盘释放回调函数"""
                pass
            
            # 启动键盘监听器
            keyboard_listener = keyboard.Listener(
                on_press=on_key_press,
                on_release=on_key_release
            )
            keyboard_listener.start()
            
            self.log_message("✅ 手动触发键盘监听器已启动")
            
            # 等待停止信号
            while self.manual_trigger_active:
                if self.manual_trigger_event.wait(timeout=0.1):
                    break
                time.sleep(0.01)
            
            # 停止键盘监听器
            keyboard_listener.stop()
            self.log_message("手动触发键盘监听器已停止")
            
        except ImportError:
            self.log_message("⚠️ pynput未安装，无法使用键盘监听功能")
            self.log_message("请安装: pip install pynput")
            self.stop_manual_trigger_mode()
        except Exception as e:
            self.log_message(f"⚠️ 手动触发监听器错误: {e}")
            self.stop_manual_trigger_mode()
    
    def execute_single_trigger(self):
        """执行单次触发匹配"""
        try:
            self.trigger_count += 1
            self.trigger_count_label.config(text=str(self.trigger_count))
            
            self.log_message(f"🔄 手动触发 #{self.trigger_count}")
            
            # 执行匹配
            self.perform_matching()
            
        except Exception as e:
            self.log_message(f"执行单次触发错误: {e}")
    
    def perform_matching(self):
        """执行模板匹配"""
        try:
            # 固定的五个TFT卡牌区域
            fixed_regions = [
                (645, 1240, 250, 185),   # 区域1
                (914, 1240, 250, 185),   # 区域2
                (1183, 1240, 250, 185),  # 区域3
                (1452, 1240, 250, 185),  # 区域4
                (1721, 1240, 250, 185),  # 区域5
            ]
            
            # OCR识别区域
            ocr_region = (360, 1173, 27, 36)
            
            templates = load_templates_from_dir(self.templates_dir)
            all_matches = []
            ocr_number = None
            ocr_confidence = None
            
            # 执行OCR识别（如果启用）
            if self.ocr_var.get() and self.ocr:
                try:
                    full_screen = grab_fullscreen(monitor_index=self.monitor_var.get())
                    ocr_number = self.ocr.recognize_number_from_region(full_screen, ocr_region)
                    ocr_confidence = 0.9  # 默认置信度
                    self.log_message(f"🔍 OCR识别结果: Level {ocr_number}")
                except Exception as e:
                    self.log_message(f"⚠️ OCR识别失败: {e}")
                    # 使用OCR回退值
                    try:
                        ocr_number = self.ocr._get_fallback_number()
                        ocr_confidence = 0.5
                        self.log_message(f"使用OCR回退值: Level {ocr_number}")
                    except:
                        ocr_number = 1
                        ocr_confidence = 0.3
                        self.log_message("使用默认Level值: 1")
            
            self.log_message(f"开始匹配 {len(templates)} 个模板...")
            
            # 准备匹配数据，使用与main函数相同的格式
            matches_data = []
            match_details = []
            
            for i, (x, y, w, h) in enumerate(fixed_regions):
                region_img = grab_region((x, y, w, h), monitor_index=self.monitor_var.get())
                region_matched = False
                region_templates = []
                region_detail = {}
                
                for name, tmpl in templates:
                    res = match_template(region_img, tmpl, threshold=self.threshold_var.get())
                    if res is not None:
                        # 解析卡牌信息
                        unit_name, cost = self.parse_card_name(name)
                        
                        # 记录匹配详情
                        if 'score' not in region_detail or res['score'] > region_detail.get('score', 0):
                            region_detail = {
                                'score': res['score'],
                                'bbox': {
                                    'top_left': res['top_left'],
                                    'bottom_right': res['bottom_right'],
                                    'center': res['center']
                                }
                            }
                        
                        region_templates.append(name)
                        region_matched = True
                        
                        all_matches.append({
                            'region': i+1,
                            'name': unit_name,
                            'cost': cost,
                            'score': res['score']
                        })
                
                if region_matched:
                    matches_data.append((i+1, region_templates))
                    # 添加OCR信息到匹配详情
                    region_detail['ocr_number'] = ocr_number
                    region_detail['ocr_confidence'] = ocr_confidence
                    match_details.append(region_detail)
                else:
                    self.log_message(f"⚠️ 区域{i+1}: 未匹配到任何模板")
                    match_details.append({})
            
            # 记录到数据库，使用与main函数相同的方法
            if self.current_session_id and matches_data:
                try:
                    self.database.record_matches(self.current_session_id, matches_data, match_details)
                    self.log_message(f"✅ 数据库记录成功，记录了 {len(matches_data)} 个区域的匹配结果")
                except Exception as db_error:
                    self.log_message(f"❌ 数据库记录失败: {db_error}")
            
            # 更新Level计数
            if ocr_number and ocr_number >= 2 and ocr_number <= 10:
                current_count = int(self.count_labels[ocr_number]['text'])
                self.count_labels[ocr_number].config(text=str(current_count + 1))
                self.log_message(f"📊 Level {ocr_number} 计数更新: {current_count} → {current_count + 1}")
                # 从数据库获取最新的capture_sequence值并更新触发次数
                self.update_trigger_count_from_database()  
            
            self.log_message(f"🎯 匹配完成，找到 {len(all_matches)} 个匹配")
            
            # 显示匹配结果摘要
            if all_matches:
                self.log_message("匹配结果摘要:")
                for match in all_matches:
                    self.log_message(f"  区域{match['region']}: {match['name']} (费用{match['cost']})")
            
            # 更新图表
            self.update_charts()
            
        except Exception as e:
            self.log_message(f"❌ 匹配错误: {e}")
            import traceback
            self.log_message(f"错误详情: {traceback.format_exc()}")
    
    def parse_card_name(self, template_name):
        """解析卡牌名称，提取单位名称和费用"""
        try:
            # 格式: "1c_Aatrox.png" -> cost=1, name="Aatrox"
            parts = template_name.replace('.png', '').split('_')
            if len(parts) >= 2:
                cost = int(parts[0].replace('c', ''))
                name = '_'.join(parts[1:])
                return name, cost
            else:
                return template_name, 0
        except:
            return template_name, 0
    
    def update_charts(self):
        """更新图表"""
        try:
            # 更新饼图
            self.update_pie_chart()
            
            # 更新折线图
            self.update_line_chart()
            
        except Exception as e:
            self.log_message(f"图表更新错误: {e}")
    
    def update_pie_chart(self):
        """更新饼图"""
        try:
            # 获取费用分布数据
            cost_data = self.get_cost_distribution()
            
            if not cost_data:
                return
            
            self.ax_pie.clear()
            self.ax_pie.set_facecolor('#34495e')
            
            costs = list(cost_data.keys())
            counts = list(cost_data.values())
            # colors = ['#2c373d', '#1E5C39', '#1C617E', '#8F3384', '#9E681F']
            colors = ['#677380', '#069926', '#09529c', '#b70cc2', '#c77712']
            
            wedges, texts, autotexts = self.ax_pie.pie(counts, labels=costs, autopct='%1.1f%%',
                                                       colors=colors[:len(costs)])
            
            # 设置文本颜色
            for text in texts:
                text.set_color('white')
            for autotext in autotexts:
                autotext.set_color('white')
            
            # self.ax_pie.set_title('卡牌费用分布', color='white', fontsize=12)
            self.canvas_pie.draw()
            
        except Exception as e:
            self.log_message(f"饼图更新错误: {e}")
    
    def update_line_chart(self):
        """更新直方图"""
        try:
            # 获取棋子统计数据
            unit_data = self.get_unit_statistics_data()
            
            if not unit_data:
                return
            
            self.ax_line.clear()
            self.ax_line.set_facecolor('#34495e')
            
            unit_name = list(unit_data.keys())
            counts = [row[0] for row in unit_data.values()]
            costs = [row[1] for row in unit_data.values()]

            # 定义不同cost值的颜色映射
            cost_colors = {
                1: '#677380',    # 1费
                2: '#069926',    # 2费
                3: '#09529c',    # 3费
                4: '#b70cc2',    # 4费
                5: '#c77712',    # 5费
            }
            
            # 如果选择了特定费用筛选，只显示该费用的数据
            if hasattr(self, 'selected_cost_filter') and self.selected_cost_filter is not None:
                filtered_data = [(name, count, cost) for name, count, cost in zip(unit_name, counts, costs) 
                               if cost == self.selected_cost_filter]
                if filtered_data:
                    unit_name = [item[0] for item in filtered_data]
                    counts = [item[1] for item in filtered_data]
                    costs = [item[2] for item in filtered_data]
                    colors = [cost_colors.get(cost, '#95a5a6') for cost in costs]
                else:
                    # 如果没有数据，显示"无数据"信息
                    self.ax_line.text(0.5, 0.5, f'费用 {self.selected_cost_filter} 无数据', 
                                    ha='center', va='center', transform=self.ax_line.transAxes, 
                                    color='white', fontsize=12)
                    self.canvas_line.draw()
                    return
            else:
                # 为每个条形设置对应的颜色
                colors = [cost_colors.get(cost, '#95a5a6') for cost in costs]
            
            # 创建条形图
            bars = self.ax_line.bar(unit_name, counts, color=colors, alpha=0.8, edgecolor='white', linewidth=1)
            
            # 设置图表属性
            self.ax_line.set_xlabel('Units Name', color='white')
            self.ax_line.set_ylabel('Count', color='white')
            self.ax_line.tick_params(colors='white')
            self.ax_line.tick_params(axis='x', rotation=45)
            self.ax_line.grid(True, alpha=0.2, color='white', axis='y')
            
            # 创建可点击的图例按钮
            self.create_clickable_legend(cost_colors, costs)
            
            self.canvas_line.draw()

        except Exception as e:
            self.log_message(f"折线图更新错误: {e}")
    
    def create_clickable_legend(self, cost_colors, costs):
        """创建可点击的费用图例按钮"""
        try:
            # 清除之前的图例按钮（如果存在）
            if hasattr(self, 'legend_frame'):
                self.legend_frame.destroy()
            
            # 创建图例容器
            self.legend_frame = tk.Frame(self.root, bg='#34495e', relief='raised', bd=1)
            self.legend_frame.place(relx=0.98, rely=0.33, anchor='ne')
            
            # 创建费用按钮
            self.cost_buttons = {}
            for cost in sorted(set(costs)):
                if cost in cost_colors:
                    # 创建按钮
                    btn = tk.Button(self.legend_frame, text=f"{cost}Cost", 
                                  font=('Arial', 9, 'bold'), width=6, height=1,
                                  bg=cost_colors[cost], fg='white', 
                                  command=lambda c=cost: self.on_cost_button_click(c))
                    btn.pack(side='left', pady=1, padx=2)
                    self.cost_buttons[cost] = btn
                    
                    # 如果当前选中了该费用，高亮显示
                    if self.selected_cost_filter == cost:
                        btn.config(relief='sunken', bd=3)
                
        except Exception as e:
            self.log_message(f"创建图例按钮错误: {e}")
    
    def on_cost_button_click(self, cost):
        """处理费用按钮点击事件"""
        try:
            # 更新选中的费用筛选
            if self.selected_cost_filter == cost:
                # 如果点击的是已选中的按钮，则取消选择
                self.selected_cost_filter = None
                self.cost_buttons[cost].config(relief='raised', bd=1)
                self.log_message(f"取消费用 {cost} 筛选")
            else:
                # 选择新的费用值
                # 恢复所有按钮的默认样式
                for btn_cost, btn in self.cost_buttons.items():
                    btn.config(relief='raised', bd=1)
                
                # 设置选中按钮的高亮样式
                self.selected_cost_filter = cost
                self.cost_buttons[cost].config(relief='sunken', bd=3)
                self.log_message(f"选择费用 {cost} 进行数据筛选")
            
            # 更新图表显示
            self.update_charts()
            
        except Exception as e:
            self.log_message(f"费用按钮点击错误: {e}")
    
    def get_cost_distribution(self):
        """获取费用分布数据"""
        try:
            if not self.current_session_id:
                return {}
            
            conn = sqlite3.connect(self.database.db_path)
            cursor = conn.cursor()
            
            # 构建查询条件
            where_conditions = []
            params = []
            
            if self.selected_level is not None:
                where_conditions.append("ocr_number = ?")
                params.append(self.selected_level)
            
            if self.selected_cost_filter is not None:
                where_conditions.append("cost = ?")
                params.append(self.selected_cost_filter)
            
            # 构建SQL查询
            if where_conditions:
                where_clause = " AND ".join(where_conditions)
                sql = f'''
                    SELECT cost, SUM(total_matches) as count
                    FROM template_stats 
                    WHERE {where_clause}
                    GROUP BY cost
                    ORDER BY cost
                '''
            else:
                sql = '''
                    SELECT cost, SUM(total_matches) as count
                    FROM template_stats 
                    GROUP BY cost
                    ORDER BY cost
                '''
            
            cursor.execute(sql, params)
            result = dict(cursor.fetchall())
            conn.close()
            
            return result
            
        except Exception as e:
            self.log_message(f"获取费用分布错误: {e}")
            return {}
    
    def get_unit_statistics_data(self):
        """获取棋子统计数据"""
        try:
            if not self.current_session_id:
                return {}
            
            conn = sqlite3.connect(self.database.db_path)
            cursor = conn.cursor()
            
            # 构建查询条件
            where_conditions = []
            params = []
            
            if self.selected_level is not None:
                where_conditions.append("ocr_number = ?")
                params.append(self.selected_level)
            
            if self.selected_cost_filter is not None:
                where_conditions.append("cost = ?")
                params.append(self.selected_cost_filter)
            
            # 构建SQL查询
            if where_conditions:
                where_clause = " AND ".join(where_conditions)
                sql = f'''
                    SELECT unit_name, total_matches, cost
                    FROM template_stats 
                    WHERE {where_clause}
                    GROUP BY unit_name
                    ORDER BY cost ASC
                '''
            else:
                sql = '''
                    SELECT unit_name, total_matches, cost
                    FROM template_stats 
                    GROUP BY unit_name
                    ORDER BY cost ASC
                '''
            
            cursor.execute(sql, params)
            result = cursor.fetchall()
            conn.close()
            
            return {row[0]: (row[1], row[2]) for row in result}
            
        except Exception as e:
            self.log_message(f"获取棋子统计错误: {e}")
            return {}
    
    def save_records(self):
        """保存记录"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                self.export_to_csv(filename)
                self.log_message(f"记录已保存到: {filename}")
                messagebox.showinfo("成功", "记录保存成功！")
                
        except Exception as e:
            self.log_message(f"保存记录错误: {e}")
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def export_to_csv(self, filename):
        """导出数据到CSV - 使用新的导出格式"""
        try:
            if not self.current_session_id:
                self.log_message("⚠️ 没有活动会话，无法导出数据")
                return
            
            conn = sqlite3.connect(self.database.db_path)
            cursor = conn.cursor()
            
            try:
                # 查询matches表的指定字段
                cursor.execute('''
                    SELECT capture_sequence, unit_name, cost, ocr_number
                    FROM matches
                    ORDER BY capture_sequence, unit_name
                ''')
                matches_data = cursor.fetchall()
    
                # 查询template_stats表的指定字段
                cursor.execute('''
                    SELECT id, unit_name, cost, ocr_number, total_matches
                    FROM template_stats
                    ORDER BY id
                ''')
                template_stats_data = cursor.fetchall()
            
                conn.close()
            
                # 写入CSV文件
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    import csv
                    writer = csv.writer(csvfile)
                
                    # 写入matches表数据
                    writer.writerow(['=== MATCHES TABLE ==='])
                    writer.writerow(['capture_sequence', 'unit_name', 'cost', 'ocr_number'])
                    for row in matches_data:
                        writer.writerow(row)
                
                    # 写入空行分隔
                    writer.writerow([])
                
                    # 写入template_stats表数据
                    writer.writerow(['=== TEMPLATE_STATS TABLE ==='])
                    writer.writerow(['id', 'unit_name', 'cost', 'ocr_number', 'total_matches'])
                    for row in template_stats_data:
                        writer.writerow(row)
            
                    print(f"✅ 新CSV格式数据已导出到: {filename}")
                    print(f"  - matches表: {len(matches_data)} 条记录")
                    print(f"  - template_stats表: {len(template_stats_data)} 条记录")
            
            # except Exception as e:
            #     print(f"❌ 导出失败: {e}")
            #     import traceback
            #     traceback.print_exc()
            finally:
                if conn:
                    conn.close()

        except Exception as e:
            self.log_message(f"❌ 导出CSV错误: {e}")
            raise
    
    def auto_save_records_on_stop(self):
        """停止监控时自动保存记录到log文件夹"""
        try:
            # 创建log文件夹（如果不存在）
            log_dir = "log"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                self.log_message(f"📁 创建log文件夹: {log_dir}")
            
            # 生成文件名：yyyy-mm-dd-hh-mm-ss.csv
            timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            filename = os.path.join(log_dir, f"{timestamp}.csv")
            
            # 导出数据到CSV
            self.export_to_csv(filename)
            
            self.log_message(f"✅ 自动保存记录成功: {filename}")
            self.log_message(f"📊 数据已保存到log文件夹")
            
        except Exception as e:
            self.log_message(f"❌ 自动保存记录失败: {e}")
            raise
    
    def share_data(self):
        """保存当前程序窗口截图到剪贴板"""
        try:
            # 获取当前窗口位置和大小
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            # 截取当前窗口区域
            from PIL import ImageGrab
            import io
            
            # 截取指定区域（窗口位置）
            screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            
            # 尝试将图片直接复制到剪贴板
            try:
                # 方法1: 使用PIL的clipboard功能（如果可用）
                try:
                    screenshot.save("temp_screenshot.png")
                    self.log_message("✅ 窗口截图已保存为临时文件")
                    
                    # 方法2: 使用系统剪贴板API
                    import win32clipboard
                    from PIL import Image
                    
                    # 将图片转换为BMP格式
                    output = io.BytesIO()
                    screenshot.convert('RGB').save(output, 'BMP')
                    data = output.getvalue()[14:]  # 去掉BMP文件头
                    output.close()
                    
                    # 复制到剪贴板
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                    win32clipboard.CloseClipboard()
                    
                    self.log_message(f"✅ 窗口截图已复制到剪贴板")
                    self.log_message(f"  窗口位置: ({x}, {y})")
                    self.log_message(f"  窗口大小: {width} x {height}")
                    messagebox.showinfo("成功", "窗口截图已复制到剪贴板！\n现在可以在其他应用程序中粘贴使用。")
                    
                except ImportError:
                    # 如果没有win32clipboard，尝试使用其他方法
                    try:
                        import pyperclip
                        # 将图片转换为base64编码
                        import base64
                        output = io.BytesIO()
                        screenshot.save(output, 'PNG')
                        img_data = output.getvalue()
                        output.close()
                        
                        # 创建HTML格式的剪贴板数据
                        html_data = f'<img src="data:image/png;base64,{base64.b64encode(img_data).decode()}">'
                        
                        # 复制到剪贴板
                        pyperclip.copy(html_data)
                        
                        self.log_message(f"✅ 窗口截图已复制到剪贴板（HTML格式）")
                        self.log_message(f"  窗口位置: ({x}, {y})")
                        self.log_message(f"  窗口大小: {width} x {height}")
                        messagebox.showinfo("成功", "窗口截图已复制到剪贴板！\n现在可以在支持HTML的应用程序中粘贴使用。")
                        
                    except ImportError:
                        # 最后的回退方案：保存文件并提示用户
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"screenshot_{timestamp}.png"
                        screenshot.save(filename)
                        
                        self.log_message(f"✅ 窗口截图已保存为文件: {filename}")
                        self.log_message(f"  窗口位置: ({x}, {y})")
                        self.log_message(f"  窗口大小: {width} x {height}")
                        self.log_message(f"  ⚠️ 无法复制到剪贴板，请手动复制文件")
                        messagebox.showinfo("成功", f"窗口截图已保存！\n文件名: {filename}\n请手动复制此文件。")
                        
            except Exception as clipboard_error:
                # 如果剪贴板操作失败，保存文件
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"screenshot_{timestamp}.png"
                screenshot.save(filename)
                
                self.log_message(f"✅ 窗口截图已保存为文件: {filename}")
                self.log_message(f"  窗口位置: ({x}, {y})")
                self.log_message(f"  窗口大小: {width} x {height}")
                self.log_message(f"  ⚠️ 剪贴板复制失败: {clipboard_error}")
                messagebox.showinfo("成功", f"窗口截图已保存！\n文件名: {filename}\n剪贴板复制失败，请手动复制文件。")
            
        except ImportError:
            self.log_message("❌ 缺少PIL库，无法截图")
            messagebox.showerror("错误", "请安装PIL库: pip install Pillow")
        except Exception as e:
            self.log_message(f"❌ 截图失败: {e}")
            messagebox.showerror("错误", f"截图失败: {e}")
    
    def clear_table(self):
        """清空统计表格"""
        self.reset_all_counts()
        self.log_message("统计表格已清空")
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("日志已清空")
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 限制日志行数
        lines = self.log_text.get(1.0, tk.END).split('\n')
        if len(lines) > 100:
            self.log_text.delete(1.0, f"{len(lines) - 100}.0")
    
    def update_loop(self):
        """更新循环"""
        while True:
            try:
                # 更新触发次数显示
                self.trigger_count_label.config(text=str(self.trigger_count))
                
                # 定期更新图表
                if self.is_running and self.current_session_id:
                    self.update_charts()
                
                time.sleep(2)  # 每2秒更新一次
                
            except Exception as e:
                print(f"更新循环错误: {e}")
                time.sleep(5)


def main():
    """主函数"""
    root = tk.Tk()
    app = TFTStatsGUI(root)
    
    # 设置快捷键
    root.bind('<Control-s>', lambda e: app.save_records())
    root.bind('<Control-t>', lambda e: app.manual_trigger())
    root.bind('<Control-l>', lambda e: app.clear_log())
    root.bind('<Control-c>', lambda e: app.clear_table())
    
    # 启动GUI
    root.mainloop()


if __name__ == "__main__":
    main()
