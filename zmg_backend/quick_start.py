#!/usr/bin/env python
"""
ZMG Backend 快速启动脚本
一键启动Django开发服务器
"""

import os
import sys
import subprocess
import time

def run_command(cmd, description):
    """执行命令并显示进度"""
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"[SUCCESS] {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description}失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def main():
    print("="*50)
    print("        ZMG Backend 快速启动程序")
    print("="*50)
    print()
    
    # 检查是否在正确的目录
    if not os.path.exists('manage.py'):
        print("[ERROR] 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("[ERROR] 需要Python 3.7或更高版本")
        sys.exit(1)
    
    print(f"[INFO] Python版本: {sys.version}")
    
    # 创建并激活虚拟环境
    if not os.path.exists('venv'):
        if not run_command('python -m venv venv', '创建虚拟环境'):
            sys.exit(1)
    
    # 激活虚拟环境并安装依赖
    if os.name == 'nt':  # Windows
        pip_path = 'venv\\Scripts\\pip'
        python_path = 'venv\\Scripts\\python'
    else:  # Linux/Mac
        pip_path = 'venv/bin/pip'
        python_path = 'venv/bin/python'
    
    if not run_command(f'{pip_path} install -r requirements.txt', '安装依赖包'):
        sys.exit(1)
    
    # 数据库迁移
    if not run_command(f'{python_path} manage.py migrate', '执行数据库迁移'):
        sys.exit(1)
    
    # 收集静态文件
    if not run_command(f'{python_path} manage.py collectstatic --noinput', '收集静态文件'):
        print("[WARNING] 静态文件收集失败，但继续启动...")
    
    # 加载初始数据
    if os.path.exists('init_data.py'):
        if not run_command(f'{python_path} init_data.py', '加载初始数据'):
            print("[WARNING] 初始数据加载失败，但继续启动...")
    
    print()
    print("="*50)
    print("[SUCCESS] 所有准备工作完成！")
    print("="*50)
    print()
    print("服务器信息:")
    print("  地址: http://127.0.0.1:8000")
    print("  管理后台: http://127.0.0.1:8000/admin")
    print("  按 Ctrl+C 停止服务器")
    print()
    
    # 启动开发服务器
    try:
        subprocess.run([python_path, 'manage.py', 'runserver'])
    except KeyboardInterrupt:
        print("\n[INFO] 服务器已停止")

if __name__ == '__main__':
    main()