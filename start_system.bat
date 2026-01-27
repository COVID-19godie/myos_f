@echo off
chcp 65001 >nul
echo.
echo ========================================
echo           🚀 ZMG Cloud OS 启动器
echo ========================================
echo.

:: 设置路径
set BACKEND_PATH=d:\MyOS\zmg_backend
set FRONTEND_PATH=d:\MyOS\frontend
set PYTHON_EXE=python.exe

:: 检查Python是否可用
%PYTHON_EXE% --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python并添加到PATH
    pause
    exit /b 1
)

:: 检查后端路径
if not exist "%BACKEND_PATH%\manage.py" (
    echo ❌ 错误: 后端路径不存在或缺少manage.py
    echo 期望路径: %BACKEND_PATH%
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo ✅ 项目路径检查通过
echo.

:: 检查端口占用
call :check_port 8000 "后端服务"
call :check_port 3000 "前端开发服务器"  
call :check_port 8080 "前端静态服务器"
echo.

:: 询问启动模式
echo 请选择启动模式:
echo [1] 仅启动后端服务 (Django)
echo [2] 仅启动前端静态服务器
echo [3] 启动后端 + 前端静态服务器
echo [4] 启动后端 + 前端开发服务器 (需要Node.js)
echo [5] 启动所有服务
echo [6] 退出
echo.
set /p choice=请输入选择 (1-6): 

echo.
if "%choice%"=="1" goto start_backend_only
if "%choice%"=="2" goto start_frontend_static_only
if "%choice%"=="3" goto start_backend_with_static
if "%choice%"=="4" goto start_full_development
if "%choice%"=="5" goto start_all_services
if "%choice%"=="6" goto exit_launcher
echo ❌ 无效选择，请重新运行
echo.
goto exit_launcher

:check_port
netstat -an | find ":%~1 " | find "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  端口 %~1 已被占用 (%~2)
) else (
    echo ✅ 端口 %~1 可用 (%~2)
)
 goto :eof

:start_backend_only
echo 🔧 启动后端服务...
cd /d "%BACKEND_PATH%"
start "ZMG Backend" cmd /k "%PYTHON_EXE% manage.py runserver 8000"
echo ✅ 后端服务已启动，访问: http://localhost:8000
echo.
goto show_links

:start_frontend_static_only
echo 🌐 启动前端静态服务器...
cd /d "%FRONTEND_PATH%"
start "ZMG Frontend Static" cmd /k "%PYTHON_EXE% -m http.server 8080"
echo ✅ 前端静态服务器已启动，访问: http://localhost:8080
echo.
goto show_links

:start_backend_with_static
echo 🔧 启动后端服务...
cd /d "%BACKEND_PATH%"
start "ZMG Backend" cmd /k "%PYTHON_EXE% manage.py runserver 8000"
timeout /t 3 /nobreak >nul

echo 🌐 启动前端静态服务器...
cd /d "%FRONTEND_PATH%"
start "ZMG Frontend Static" cmd /k "%PYTHON_EXE% -m http.server 8080"
echo.
echo ✅ 后端和前端静态服务器已启动
echo.
goto show_links

:start_full_development
:: 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 前端开发模式需要Node.js，但未找到
    echo 请安装Node.js后再试，或选择其他模式
    pause
    goto exit_launcher
)

echo 🔧 启动后端服务...
cd /d "%BACKEND_PATH%"
start "ZMG Backend" cmd /k "%PYTHON_EXE% manage.py runserver 8000"
timeout /t 3 /nobreak >nul

echo ⚡ 启动前端开发服务器...
cd /d "%FRONTEND_PATH%"
start "ZMG Frontend Dev" cmd /k "npm run dev"
echo.
echo ✅ 后端和前端开发服务器已启动
echo ⚠️  注意: 前端开发服务器启动较慢，请耐心等待
echo.
goto show_links

:start_all_services
echo 🔧 启动后端服务...
cd /d "%BACKEND_PATH%"
start "ZMG Backend" cmd /k "%PYTHON_EXE% manage.py runserver 8000"
timeout /t 3 /nobreak >nul

echo ⚡ 启动前端开发服务器...
cd /d "%FRONTEND_PATH%"
if exist "%FRONTEND_PATH%\package.json" (
    node --version >nul 2>&1
    if not errorlevel 1 (
        start "ZMG Frontend Dev" cmd /k "npm run dev"
    ) else (
        echo ⚠️  Node.js未安装，启动静态服务器代替
echo 🌐 启动前端静态服务器...
        start "ZMG Frontend Static" cmd /k "%PYTHON_EXE% -m http.server 8080"
    )
) else (
    echo 🌐 启动前端静态服务器...
    start "ZMG Frontend Static" cmd /k "%PYTHON_EXE% -m http.server 8080"
)

echo.
echo ✅ 所有服务已启动
echo.
goto show_links

:show_links
echo ========================================
echo 📱 快速访问链接:
echo.
echo 🏠 后端主页:     http://localhost:8000
echo 💻 前端开发版:   http://localhost:3000
echo 📱 前端静态版:   http://localhost:8080
echo 🔍 API健康检查: http://localhost:8000/api/health/
echo.
echo 💡 提示:
echo - 每个服务都在独立的命令行窗口中运行
echo - 关闭窗口即可停止对应的服务
echo - 按 Ctrl+C 可在开发服务器窗口中优雅停止
echo ========================================
echo.

goto exit_launcher

:exit_launcher
echo.
echo 👋 启动器已退出
if "%choice%"=="6" (
    echo 感谢使用 ZMG Cloud OS！
) else (
    echo 服务正在后台运行，关闭窗口即可停止服务
    echo 按任意键退出启动器...
    pause >nul
)
exit /b 0