@echo off
chcp 65001 > nul
title ZMG Cloud OS - 完整启动（前端+后端）

echo ============================================
echo   ZMG Cloud OS - 完整启动（前端+后端）
echo ============================================
echo.

:: 设置后端路径（根据实际情况修改）
set BACKEND_PATH=..\backend
set BACKEND_PORT=8000

:: 启动后端服务
echo [1/2] 启动后端服务...
if exist "%BACKEND_PATH%" (
    cd /d "%BACKEND_PATH%"
    start "ZMG Backend" python manage.py runserver %BACKEND_PORT%
    cd /d "%~dp0"
    echo ✅ 后端服务启动中: http://localhost:%BACKEND_PORT%
) else (
    echo ⚠️  后端路径不存在: %BACKEND_PATH%
    echo 📝 请修改脚本中的 BACKEND_PATH 变量
)
echo.

:: 等待后端启动
echo ⏳ 等待后端服务就绪...
timeout /t 3 /nobreak >nul
echo.

:: 启动前端服务
echo [2/2] 启动前端服务...
echo ============================================
echo 🚀 ZMG Cloud OS 已启动
echo.
echo 📍 启动器: http://localhost:3000/launcher.html
echo 📍 主应用: http://localhost:3000/
echo 📍 后端API: http://localhost:%BACKEND_PORT%
echo.
echo 按 Ctrl+C 停止前端（后端需手动关闭）
echo ============================================
echo.

call npm run dev

pause
