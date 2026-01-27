@echo off
chcp 65001 > nul
title ZMG Cloud OS - 快速启动

echo 🚀 正在启动 ZMG Cloud OS...
echo.

:: 快速启动，不检查依赖
if not exist "node_modules\" (
    echo 📦 首次运行，安装依赖中...
    call npm install
    if %errorlevel% neq 0 (
        echo ❌ 安装失败
        pause
        exit /b 1
    )
)

echo 🌐 服务地址: http://localhost:3000
echo 📱 启动器: http://localhost:3000/launcher.html
echo.
echo 按 Ctrl+C 停止服务器
echo.

call npm run dev

pause
