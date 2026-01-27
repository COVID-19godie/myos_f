#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZMG Cloud OS 智能启动器 v2.0
功能：
- 一键启动前后端服务
- 自动检测端口占用
- 实时日志监控
- 服务状态管理
- 现代化GUI界面
"""

import subprocess
import time
import sys
import os
import signal
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import psutil
import requests
from datetime import datetime
import webbrowser

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.logs = {}
        self.running = True
        
    def is_port_in_use(self, port):
        """检查端口是否被占用"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                connections = proc.net_connections()
                for conn in connections:
                    if hasattr(conn.laddr, 'port') and conn.laddr.port == port:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def start_backend(self):
        """启动后端服务"""
        if self.is_port_in_use(8000):
            return True, "后端服务已在运行中 (端口8000)"
        
        try:
            backend_path = r"d:\MyOS\zmg_backend"
            if not os.path.exists(backend_path):
                return False, f"后端路径不存在: {backend_path}"
            
            # 启动Django开发服务器
            cmd = [sys.executable, "manage.py", "runserver", "8000"]
            process = subprocess.Popen(
                cmd,
                cwd=backend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes['backend'] = process
            self.logs['backend'] = []
            
            # 启动日志收集线程
            thread = threading.Thread(target=self._collect_logs, args=('backend',))
            thread.daemon = True
            thread.start()
            
            # 等待服务启动
            for i in range(30):  # 最多等待30秒
                if self.is_port_in_use(8000):
                    return True, "后端服务启动成功"
                time.sleep(1)
            
            return False, "后端服务启动超时"
            
        except Exception as e:
            return False, f"启动后端服务失败: {str(e)}"
    
    def start_frontend_dev(self):
        """启动前端开发服务器"""
        if self.is_port_in_use(3000):
            return True, "前端开发服务器已在运行中 (端口3000)"
        
        try:
            frontend_path = r"d:\MyOS\frontend"
            if not os.path.exists(frontend_path):
                return False, f"前端路径不存在: {frontend_path}"
            
            # 使用Node.js启动Vite开发服务器
            cmd = ["npm", "run", "dev"]
            process = subprocess.Popen(
                cmd,
                cwd=frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes['frontend_dev'] = process
            self.logs['frontend_dev'] = []
            
            # 启动日志收集线程
            thread = threading.Thread(target=self._collect_logs, args=('frontend_dev',))
            thread.daemon = True
            thread.start()
            
            # 等待服务启动
            for i in range(45):  # Vite启动较慢，等待45秒
                if self.is_port_in_use(3000):
                    return True, "前端开发服务器启动成功"
                time.sleep(1)
            
            return False, "前端开发服务器启动超时"
            
        except FileNotFoundError:
            return False, "未找到npm命令，请确保Node.js已安装"
        except Exception as e:
            return False, f"启动前端开发服务器失败: {str(e)}"
    
    def start_frontend_static(self):
        """启动静态文件服务器"""
        if self.is_port_in_use(8080):
            return True, "静态文件服务器已在运行中 (端口8080)"
        
        try:
            frontend_path = r"d:\MyOS\frontend"
            if not os.path.exists(frontend_path):
                return False, f"前端路径不存在: {frontend_path}"
            
            # 使用Python HTTP服务器
            cmd = [sys.executable, "-m", "http.server", "8080"]
            process = subprocess.Popen(
                cmd,
                cwd=frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes['frontend_static'] = process
            self.logs['frontend_static'] = []
            
            # 启动日志收集线程
            thread = threading.Thread(target=self._collect_logs, args=('frontend_static',))
            thread.daemon = True
            thread.start()
            
            # 等待服务启动
            for i in range(10):
                if self.is_port_in_use(8080):
                    return True, "静态文件服务器启动成功"
                time.sleep(1)
            
            return False, "静态文件服务器启动超时"
            
        except Exception as e:
            return False, f"启动静态文件服务器失败: {str(e)}"
    
    def stop_service(self, service_name):
        """停止指定服务"""
        if service_name in self.processes:
            try:
                process = self.processes[service_name]
                process.terminate()
                process.wait(timeout=10)
                del self.processes[service_name]
                return True, f"{service_name} 服务已停止"
            except subprocess.TimeoutExpired:
                process.kill()
                del self.processes[service_name]
                return True, f"{service_name} 服务已强制终止"
            except Exception as e:
                return False, f"停止 {service_name} 服务失败: {str(e)}"
        return True, f"{service_name} 服务未运行"
    
    def stop_all_services(self):
        """停止所有服务"""
        services = list(self.processes.keys())
        for service in services:
            self.stop_service(service)
    
    def _collect_logs(self, service_name):
        """收集服务日志"""
        process = self.processes.get(service_name)
        if not process:
            return
        
        while self.running and process.poll() is None:
            try:
                line = process.stdout.readline()
                if line:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    log_entry = f"[{timestamp}] {line.strip()}"
                    self.logs[service_name].append(log_entry)
                    
                    # 限制日志行数
                    if len(self.logs[service_name]) > 1000:
                        self.logs[service_name] = self.logs[service_name][-500:]
            except:
                break
    
    def get_service_status(self):
        """获取服务状态"""
        status = {}
        
        # 检查端口占用
        status['backend'] = self.is_port_in_use(8000)
        status['frontend_dev'] = self.is_port_in_use(3000)
        status['frontend_static'] = self.is_port_in_use(8080)
        
        # 检查进程状态
        for service, process in self.processes.items():
            status[f"{service}_process"] = process.poll() is None
        
        return status

class SmartLauncherGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ZMG Cloud OS 智能启动器 v2.0")
        self.root.geometry("900x700")
        self.root.configure(bg='#f5f5f7')
        
        self.service_manager = ServiceManager()
        
        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        self.update_status()
    
    def setup_ui(self):
        """设置用户界面"""
        # 标题
        title_frame = tk.Frame(self.root, bg='#f5f5f7')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="🚀 ZMG Cloud OS 智能启动器",
            font=("Microsoft YaHei", 20, "bold"),
            fg='#007aff',
            bg='#f5f5f7'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="一键启动 · 实时监控 · 智能管理",
            font=("Microsoft YaHei", 12),
            fg='#666',
            bg='#f5f5f7'
        )
        subtitle_label.pack()
        
        # 服务控制面板
        control_frame = tk.LabelFrame(
            self.root,
            text="服务控制",
            font=("Microsoft YaHei", 12, "bold"),
            bg='white',
            fg='#333'
        )
        control_frame.pack(padx=20, pady=10, fill='x')
        
        # 服务按钮
        button_frame = tk.Frame(control_frame, bg='white')
        button_frame.pack(pady=15)
        
        # 后端服务
        self.backend_btn = tk.Button(
            button_frame,
            text="🔧 启动后端服务",
            command=lambda: self.toggle_service('backend'),
            font=("Microsoft YaHei", 11),
            bg='#007aff',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            relief='flat'
        )
        self.backend_btn.grid(row=0, column=0, padx=10)
        
        # 前端开发服务器
        self.frontend_dev_btn = tk.Button(
            button_frame,
            text="⚡ 启动前端开发服务器",
            command=lambda: self.toggle_service('frontend_dev'),
            font=("Microsoft YaHei", 11),
            bg='#34c759',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            relief='flat'
        )
        self.frontend_dev_btn.grid(row=0, column=1, padx=10)
        
        # 前端静态服务器
        self.frontend_static_btn = tk.Button(
            button_frame,
            text="🌐 启动前端静态服务器",
            command=lambda: self.toggle_service('frontend_static'),
            font=("Microsoft YaHei", 11),
            bg='#ff9500',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            relief='flat'
        )
        self.frontend_static_btn.grid(row=0, column=2, padx=10)
        
        # 停止所有服务
        stop_all_btn = tk.Button(
            button_frame,
            text="🛑 停止所有服务",
            command=self.stop_all_services,
            font=("Microsoft YaHei", 11),
            bg='#ff3b30',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            relief='flat'
        )
        stop_all_btn.grid(row=0, column=3, padx=10)
        
        # 状态面板
        status_frame = tk.LabelFrame(
            self.root,
            text="服务状态",
            font=("Microsoft YaHei", 12, "bold"),
            bg='white',
            fg='#333'
        )
        status_frame.pack(padx=20, pady=10, fill='x')
        
        self.status_text = tk.Text(
            status_frame,
            height=8,
            font=("Consolas", 10),
            bg='#f8f9fa',
            fg='#333',
            relief='flat',
            state='disabled'
        )
        self.status_text.pack(padx=10, pady=10, fill='x')
        
        # 快速访问面板
        access_frame = tk.LabelFrame(
            self.root,
            text="快速访问",
            font=("Microsoft YaHei", 12, "bold"),
            bg='white',
            fg='#333'
        )
        access_frame.pack(padx=20, pady=10, fill='x')
        
        access_btn_frame = tk.Frame(access_frame, bg='white')
        access_btn_frame.pack(pady=15)
        
        # 访问链接按钮
        links = [
            ("🏠 后端主页", "http://localhost:8000"),
            ("💻 前端开发版", "http://localhost:3000"),
            ("📱 前端静态版", "http://localhost:8080"),
            ("🔍 API健康检查", "http://localhost:8000/api/health/")
        ]
        
        for i, (text, url) in enumerate(links):
            btn = tk.Button(
                access_btn_frame,
                text=text,
                command=lambda u=url: webbrowser.open(u),
                font=("Microsoft YaHei", 10),
                bg='#5856d6',
                fg='white',
                padx=15,
                pady=8,
                cursor='hand2',
                relief='flat'
            )
            btn.grid(row=0, column=i, padx=10)
        
        # 日志面板
        log_frame = tk.LabelFrame(
            self.root,
            text="实时日志",
            font=("Microsoft YaHei", 12, "bold"),
            bg='white',
            fg='#333'
        )
        log_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # 日志选项卡
        notebook = ttk.Notebook(log_frame)
        notebook.pack(padx=10, pady=10, fill='both', expand=True)
        
        self.log_texts = {}
        services = ['backend', 'frontend_dev', 'frontend_static']
        
        for service in services:
            frame = tk.Frame(notebook, bg='white')
            notebook.add(frame, text=service.replace('_', ' ').title())
            
            text_widget = scrolledtext.ScrolledText(
                frame,
                font=("Consolas", 9),
                bg='#1e1e1e',
                fg='#ffffff',
                relief='flat'
            )
            text_widget.pack(fill='both', expand=True, padx=5, pady=5)
            self.log_texts[service] = text_widget
    
    def toggle_service(self, service_name):
        """切换服务状态"""
        if service_name in self.service_manager.processes:
            success, message = self.service_manager.stop_service(service_name)
        else:
            if service_name == 'backend':
                success, message = self.service_manager.start_backend()
            elif service_name == 'frontend_dev':
                success, message = self.service_manager.start_frontend_dev()
            elif service_name == 'frontend_static':
                success, message = self.service_manager.start_frontend_static()
            else:
                success, message = False, f"未知服务: {service_name}"
        
        if success:
            self.show_notification("成功", message, "success")
        else:
            self.show_notification("错误", message, "error")
        
        self.update_status()
    
    def stop_all_services(self):
        """停止所有服务"""
        self.service_manager.stop_all_services()
        self.show_notification("信息", "所有服务已停止", "info")
        self.update_status()
    
    def update_status(self):
        """更新状态显示"""
        status = self.service_manager.get_service_status()
        
        status_text = """服务状态监控
"""
        status_text += f"📊 后端服务 (端口8000): {'🟢 运行中' if status['backend'] else '🔴 未运行'}\n"
        status_text += f"⚡ 前端开发服务器 (端口3000): {'🟢 运行中' if status['frontend_dev'] else '🔴 未运行'}\n"
        status_text += f"🌐 前端静态服务器 (端口8080): {'🟢 运行中' if status['frontend_static'] else '🔴 未运行'}\n"
        status_text += f"\n🕐 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 更新状态文本
        self.status_text.config(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, status_text)
        self.status_text.config(state='disabled')
        
        # 更新按钮状态
        self.update_button_states(status)
        
        # 更新日志显示
        self.update_logs()
    
    def update_button_states(self, status):
        """更新按钮状态"""
        # 后端按钮
        if status['backend']:
            self.backend_btn.config(text="🔧 停止后端服务", bg='#ff3b30')
        else:
            self.backend_btn.config(text="🔧 启动后端服务", bg='#007aff')
        
        # 前端开发服务器按钮
        if status['frontend_dev_process']:
            self.frontend_dev_btn.config(text="⚡ 停止前端开发服务器", bg='#ff3b30')
        else:
            self.frontend_dev_btn.config(text="⚡ 启动前端开发服务器", bg='#34c759')
        
        # 前端静态服务器按钮
        if status['frontend_static_process']:
            self.frontend_static_btn.config(text="🌐 停止前端静态服务器", bg='#ff3b30')
        else:
            self.frontend_static_btn.config(text="🌐 启动前端静态服务器", bg='#ff9500')
    
    def update_logs(self):
        """更新日志显示"""
        for service, text_widget in self.log_texts.items():
            logs = self.service_manager.logs.get(service, [])
            
            text_widget.config(state='normal')
            text_widget.delete(1.0, tk.END)
            
            # 显示最新50行日志
            recent_logs = logs[-50:] if len(logs) > 50 else logs
            for log in recent_logs:
                text_widget.insert(tk.END, log + "\n")
            
            text_widget.yview(tk.END)  # 滚动到底部
            text_widget.config(state='disabled')
    
    def show_notification(self, title, message, type_="info"):
        """显示通知"""
        colors = {
            "success": "green",
            "error": "red", 
            "info": "blue"
        }
        
        messagebox.showinfo(title, message)
    
    def update_loop(self):
        """更新循环"""
        while self.service_manager.running:
            try:
                self.root.after(0, self.update_status)
                time.sleep(2)  # 每2秒更新一次
            except:
                break
    
    def on_closing(self):
        """关闭事件处理"""
        if messagebox.askokcancel("退出", "确定要退出启动器吗？这将停止所有运行的服务。"):
            self.service_manager.running = False
            self.service_manager.stop_all_services()
            self.root.destroy()
    
    def run(self):
        """运行启动器"""
        # 启动更新线程
        update_thread = threading.Thread(target=self.update_loop)
        update_thread.daemon = True
        update_thread.start()
        
        # 运行GUI
        self.root.mainloop()

def main():
    """主函数"""
    print("🚀 启动 ZMG Cloud OS 智能启动器...")
    
    try:
        launcher = SmartLauncherGUI()
        launcher.run()
    except KeyboardInterrupt:
        print("\n👋 启动器已退出")
    except Exception as e:
        print(f"❌ 启动器运行出错: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()