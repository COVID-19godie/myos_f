@echo off
chcp 65001 >nul
echo ========================================
echo    Django 数据库迁移脚本
echo ========================================
echo.

cd /d "%~dp0zmg_backend"

echo [1/2] 正在创建迁移文件...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo 错误：创建迁移文件失败！
    pause
    exit /b 1
)

echo.
echo [2/2] 正在应用迁移到数据库...
python manage.py migrate
if %errorlevel% neq 0 (
    echo 错误：应用迁移失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo    迁移完成！
echo ========================================
pause
