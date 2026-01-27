@echo off
chcp 65001 >nul
echo ========================================
echo          ZMG Backend 启动程序
cho ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装或未添加到环境变量
    pause
    exit /b 1
)

echo [信息] Python已安装

:: 检查虚拟环境是否存在
if not exist "venv" (
    echo [信息] 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

echo [信息] 激活虚拟环境...
call venv\Scripts\activate.bat

:: 安装依赖
echo [信息] 检查并安装依赖包...
pip install -r requirements.txt

:: 数据库迁移
echo [信息] 执行数据库迁移...
python manage.py migrate

:: 加载初始数据（如果存在）
if exist "init_data.py" (
    echo [信息] 加载初始数据...
    python init_data.py
)

echo.
echo [成功] 启动准备完成！
echo.
echo 选择运行模式：
echo 1. 启动开发服务器 (推荐)
echo 2. 启动带自动重载的开发服务器
echo 3. 仅检查配置
echo 4. 退出

echo.
set /p choice=请输入选择 (1-4): 

if "%choice%"=="1" (
    echo.
    echo [信息] 启动开发服务器... 
echo 访问地址: http://127.0.0.1:8000
    echo 按 Ctrl+C 停止服务器
    echo.
    python manage.py runserver
)

if "%choice%"=="2" (
    echo.
    echo [信息] 启动带自动重载的开发服务器...
    echo 访问地址: http://127.0.0.1:8000
    echo 按 Ctrl+C 停止服务器
    echo.
    python manage.py runserver --noreload
)

if "%choice%"=="3" (
    echo.
    echo [信息] 检查项目配置...
    python manage.py check
    echo.
    python manage.py showmigrations
)

if "%choice%"=="4" (
    echo [信息] 退出程序
)

pause