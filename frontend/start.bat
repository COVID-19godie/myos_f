@echo off
chcp 65001 > nul
title ZMG Cloud OS - 启动脚本

echo ============================================
echo       ZMG Cloud OS - 启动脚本
echo ============================================
echo.

:: 检查 Node.js
echo [1/5] 检查 Node.js...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 未安装 Node.js，请先安装
    pause
    exit /b 1
)
echo ✅ Node.js 已安装
node --version
echo.

:: 检查 npm
echo [2/5] 检查 npm...
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ npm 未找到
    pause
    exit /b 1
)
echo ✅ npm 已安装
npm --version
echo.

:: 检查依赖
echo [3/5] 检查项目依赖...
if not exist "node_modules\" (
    echo 📦 未安装依赖，正在安装...
    call npm install
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
) else (
    echo ✅ 依赖已安装
)
echo.

:: 检查端口占用
echo [4/5] 检查端口占用...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    echo ⚠️  端口 3000 已被占用 (PID: %%a)
    set /p choice="是否终止进程并继续？(y/n): "
    if /i "!choice!"=="y" (
        taskkill /F /PID %%a >nul 2>nul
        echo ✅ 已终止占用进程
    ) else (
        echo ❌ 启动取消
        pause
        exit /b 1
    )
)
echo ✅ 端口检查完成
echo.

:: 启动开发服务器
echo [5/5] 启动开发服务器...
echo ============================================
echo 🚀 正在启动 ZMG Cloud OS...
echo.
echo 📍 启动器: http://localhost:3000/launcher.html
echo 📍 主应用: http://localhost:3000/
echo 📍 API调试: http://localhost:3000/api-debug.html
echo.
echo 按 Ctrl+C 可停止服务器
echo ============================================
echo.

call npm run dev

pause
