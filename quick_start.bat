@echo off
chcp 65001 >nul
title ZMG Cloud OS - 快速启动
echo ========================================
echo          ZMG Cloud OS 快速启动
echo ========================================
echo.

:: 检查并启动后端
echo [1/2] 检查后端服务...
cd /d "d:\MyOS\zmg_backend"
if not exist "venv\Scripts\activate.bat" (
    echo [信息] 首次运行，正在初始化后端环境...
    call start.bat
) else (
    echo [信息] 启动后端服务...
    start "Backend" cmd /k "call start.bat"
)

:: 检查并启动前端  
echo [2/2] 检查前端服务...
timeout /t 3 /nobreak >nul
echo [信息] 启动前端服务...
cd /d "d:\MyOS\frontend"
if not exist "node_modules" (
    echo [警告] 前端依赖未安装，正在安装...
    call install_deps.bat
)
start "Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo [成功] 服务启动完成!
echo ========================================
echo 后端地址: http://127.0.0.1:8000
echo 前端地址: http://localhost:5173
echo ========================================
echo.
echo 两个服务已在独立窗口启动
echo 关闭窗口即可停止对应服务
echo.
pause