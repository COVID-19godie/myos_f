#!/usr/bin/env python
"""
ZMG OS 快速启动器 - 简化版
专注核心功能，快速启动
"""

import os
import sys
import subprocess
import time
import platform

class ZMGLauncher:
    def __init__(self):
        self.version = "3.0.0"
        self.project_name = "ZMG OS"
        self.backend_port = 8000
        self.frontend_port = 3000
        self.is_windows = os.name == 'nt'
        
    def print_banner(self):
        """显示启动横幅"""
        print("=" * 50)
        print(f"     {self.project_name} 快速启动器 v{self.version}")
        print("=" * 50)
        print("🚀 专注快速启动，去掉繁琐检查")
        print("=" * 50)
        print()
    
    def check_environment(self):
        """快速环境检查"""
        # 只检查最重要的文件
        required_files = ['zmg_backend/manage.py', 'zmg_backend/requirements.txt']
        
        for file in required_files:
            if not os.path.exists(file):
                print(f"❌ 缺少必要文件: {file}")
                return False
        
        return True
    
    def show_progress(self, current, total, bar_length=50, prefix="安装"):
        """显示进度条"""
        percent = float(current) * 100 / total
        arrow = '-' * int(round(percent * bar_length / 100)) + '>'
        spaces = ' ' * (bar_length - len(arrow))
        
        sys.stdout.write(f'\r{prefix}: [{arrow + spaces}] {current}/{total} ({percent:.1f}%)')
        sys.stdout.flush()
    
    def get_mirror(self):
        """直接使用清华镜像源，跳过检测"""
        return 'https://pypi.tuna.tsinghua.edu.cn/simple', 'pypi.tuna.tsinghua.edu.cn'
    
    def install_dependencies(self, pip_path):
        """快速依赖包安装"""
        # 使用清华镜像源
        pip_index_url, trusted_host = self.get_mirror()
        
        print("  安装依赖包...")
        
        # 直接批量安装，不显示进度条
        result = subprocess.run([
            pip_path, 'install', '-r', 'zmg_backend/requirements.txt',
            '-i', pip_index_url, 
            '--trusted-host', trusted_host,
            '--timeout', '60'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ 依赖包安装完成")
            return True
        else:
            print(f"  ❌ 依赖安装失败: {result.stderr[:200]}")
            return False
    
    def install_packages_simple(self, pip_path, pip_index_url, trusted_host):
        """简化版本约束的单个包安装（备用方案）"""
        print("  使用简化版本约束安装...")
        
        # 简化版本约束的包列表
        simple_packages = [
            'Django', 'djangorestframework', 'django-cors-headers',
            'django-filter', 'djangorestframework-simplejwt', 'Pillow',
            'python-dotenv', 'psutil', 'bcrypt', 'cryptography',
            'python-dateutil', 'requests'
        ]
        
        success_count = 0
        failed_packages = []
        
        for i, package in enumerate(simple_packages, 1):
            self.show_progress(i, len(simple_packages), prefix=f"安装依赖包")
            
            try:
                # 安装单个包，不使用复杂版本约束
                result = subprocess.run([
                    pip_path, 'install', package,
                    '-i', pip_index_url, 
                    '--trusted-host', trusted_host,
                    '--timeout', '60',
                    '--retries', '3'
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    success_count += 1
                else:
                    failed_packages.append((package, result.stderr))
                    print(f"\n  ⚠️  {package} 安装失败: {result.stderr[:100]}...")
                    
            except subprocess.TimeoutExpired:
                failed_packages.append((package, "安装超时"))
                print(f"\n  ⚠️  {package} 安装超时")
            except Exception as e:
                failed_packages.append((package, str(e)))
                print(f"\n  ⚠️  {package} 安装异常: {e}")
        
        print()
        
        if success_count >= len(simple_packages) - 2:  # 允许少量包失败
            print(f"  ✅ {success_count}/{len(simple_packages)} 个包安装成功，继续启动")
            return True
        else:
            print(f"  ❌ 依赖安装失败过多 ({success_count}/{len(simple_packages)})")
            return False
    
    def setup_environment(self):
        """快速设置运行环境"""
        # 跳过虚拟环境创建，直接使用系统Python
        python_path = sys.executable
        
        # 检查是否已安装依赖
        try:
            import django
            print("  ✅ Django已安装")
        except ImportError:
            print("  安装依赖包...")
            # 直接使用系统pip安装
            result = subprocess.run([
                'pip', 'install', '-r', 'zmg_backend/requirements.txt',
                '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple',
                '--trusted-host', 'pypi.tuna.tsinghua.edu.cn'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"  ❌ 依赖安装失败")
                return False
        
        return python_path
    

    
    def show_launch_options(self):
        """显示启动选项"""
        print("🚀 启动选项:")
        print("1. 启动后端服务 (默认)")
        print("2. 退出")
        print()
    
    def launch_backend(self, python_path):
        """启动后端服务"""
        print("🚀 启动后端服务...")
        print(f"  访问地址: http://127.0.0.1:{self.backend_port}")
        print("  按 Ctrl+C 停止服务器")
        print()
        
        try:
            subprocess.run([python_path, 'zmg_backend/manage.py', 'runserver', 
                          f'{self.backend_port}'])
        except KeyboardInterrupt:
            print("\n[INFO] 服务已停止")
    
    def main(self):
        """主启动流程"""
        self.print_banner()
        
        # 快速环境检查
        if not self.check_environment():
            return
        
        # 快速设置环境
        python_path = self.setup_environment()
        if not python_path:
            return
        
        # 简化启动选项
        while True:
            self.show_launch_options()
            
            try:
                choice = input("请选择 (1-2): ").strip()
                
                if choice == '1' or choice == '':
                    self.launch_backend(python_path)
                    break
                elif choice == '2':
                    print("👋 再见！")
                    return
                else:
                    print("❌ 无效选择，请重新输入")
                    
            except KeyboardInterrupt:
                print("\n👋 程序已退出")
                return

if __name__ == '__main__':
    try:
        launcher = ZMGLauncher()
        launcher.main()
    except Exception as e:
        print(f"启动器错误: {e}")
        print("请检查项目配置后重试")