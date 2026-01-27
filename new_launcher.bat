@echo off
chcp 65001 >nul
title ZMG OS 新一代启动器

echo ========================================
echo          ZMG OS 新一代启动器
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装或未添加到环境变量
    echo 请安装Python 3.7或更高版本
    pause
    exit /b 1
)

echo [信息] Python已安装

:: 检查是否在项目根目录
if not exist "zmg_backend\manage.py" (
    echo [错误] 请在项目根目录运行此脚本
    echo 确保 zmg_backend\manage.py 文件存在
    pause
    exit /b 1
)

echo [信息] 项目目录检查通过

:: 检查是否需要安装psutil
python -c "import psutil" 2>nul
if errorlevel 1 (
    echo [信息] 安装性能监控依赖...
    pip install psutil
    if errorlevel 1 (
        echo [警告] psutil安装失败，性能监控功能将受限
    )
)

echo.
echo [信息] 启动新一代启动器...
echo.

:: 启动Python启动器
python new_launcher.py

:: 如果Python脚本执行失败，回退到传统启动器
if errorlevel 1 (
    echo.
    echo [警告] 新一代启动器启动失败，切换到传统启动器
    echo.
    call zmg_backend\start.bat
)

pause