@echo off
chcp 65001 >nul
title ZMG Cloud OS - 一键启动器
echo ========================================
echo          ZMG Cloud OS 一键启动器
echo ========================================
echo.

:: 设置路径变量
set BACKEND_DIR=d:\MyOS\zmg_backend
set FRONTEND_DIR=d:\MyOS\frontend
set LOG_DIR=d:\MyOS\logs

:: 创建日志目录
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: 检查后端启动脚本
if not exist "%BACKEND_DIR%\start.bat" (
    echo [错误] 未找到后端启动脚本: %BACKEND_DIR%\start.bat
    pause
    exit /b 1
)

:: 检查前端文件
if not exist "%FRONTEND_DIR%\package.json" (
    echo [错误] 未找到前端package.json: %FRONTEND_DIR%\package.json
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%\install_deps.bat" (
    echo [错误] 未找到前端依赖安装脚本
    pause
    exit /b 1
)

echo [信息] 检测到项目结构完整
if not exist "%FRONTEND_DIR%\node_modules" (
    echo [警告] 前端依赖未安装
    echo.
    set /p choice=是否现在安装前端依赖? (y/N): 
    if /i "%choice%"=="y" (
        echo.
        echo [信息] 启动前端依赖安装...
        call "%FRONTEND_DIR%\install_deps.bat"
        if errorlevel 1 (
            echo [错误] 前端依赖安装失败
            pause
            exit /b 1
        )
    ) else (
        echo [信息] 跳过前端依赖安装，请确保已手动安装
        echo 可运行: %FRONTEND_DIR%\install_deps.bat
    )
)

echo.
echo ========================================
echo 选择启动模式:
echo ========================================
echo 1. 仅启动后端服务

echo 2. 仅启动前端服务

echo 3. 前后端同时启动 (推荐)
echo 4. 启动后端 + 安装前端依赖 + 启动前端
echo 5. 退出
echo.

set /p choice=请输入选择 (1-5): 

if "%choice%"=="1" goto backend_only
if "%choice%"=="2" goto frontend_only  
if "%choice%"=="3" goto both_services
if "%choice%"=="4" goto full_setup
if "%choice%"=="5" goto exit_app

echo [错误] 无效选择
echo.
goto menu

:backend_only
echo.
echo [信息] 启动后端服务...
echo 日志文件: %LOG_DIR%\backend.log
echo 按 Ctrl+C 停止服务
echo.
cd /d "%BACKEND_DIR%"
call start.bat
if errorlevel 1 (
    echo [错误] 后端启动失败
    pause
    exit /b 1
)
goto end

:frontend_only
echo.
echo [信息] 启动前端服务...
echo 日志文件: %LOG_DIR%\frontend.log
echo 按 Ctrl+C 停止服务
echo.
cd /d "%FRONTEND_DIR%"
start "ZMG Frontend" cmd /k "npm run dev ^> %LOG_DIR%\frontend.log 2^>^&1"
echo [成功] 前端服务已在独立窗口启动
echo 访问地址: http://localhost:5173
echo.
goto end

:both_services
echo.
echo [信息] 同时启动前后端服务...
echo.

:: 启动后端
echo [1/2] 启动后端服务...
cd /d "%BACKEND_DIR%"
start "ZMG Backend" cmd /k "call start.bat ^| tee %LOG_DIR%\backend.log"

echo [2/2] 启动前端服务...
cd /d "%FRONTEND_DIR%"
start "ZMG Frontend" cmd /k "npm run dev ^| tee %LOG_DIR%\frontend.log"

echo.
echo [成功] 前后端服务已启动!
echo ========================================
echo 后端地址: http://127.0.0.1:8000
echo 前端地址: http://localhost:5173
echo 后端日志: %LOG_DIR%\backend.log
echo 前端日志: %LOG_DIR%\frontend.log
echo ========================================
echo.
echo 提示:
echo - 两个服务在独立窗口运行
echo - 关闭对应窗口可停止相应服务
echo - 查看日志文件了解运行状态
echo.
goto end

:full_setup
echo.
echo [信息] 完整设置流程...
echo.

:: 安装前端依赖
echo [1/3] 安装前端依赖...
cd /d "%FRONTEND_DIR%"
call install_deps.bat
if errorlevel 1 (
    echo [错误] 前端依赖安装失败
    pause
    exit /b 1
)

:: 启动后端
echo.
echo [2/3] 启动后端服务...
cd /d "%BACKEND_DIR%"
start "ZMG Backend" cmd /k "call start.bat ^| tee %LOG_DIR%\backend.log"

:: 启动前端
echo.
echo [3/3] 启动前端服务...
cd /d "%FRONTEND_DIR%"
start "ZMG Frontend" cmd /k "npm run dev ^| tee %LOG_DIR%\frontend.log"

echo.
echo [成功] 完整设置完成!
echo ========================================
echo 后端地址: http://127.0.0.1:8000
echo 前端地址: http://localhost:5173
echo ========================================
echo.
goto end

:exit_app
echo [信息] 退出程序
echo.goto end

:menu
echo.
echo 返回主菜单...
echo.pause
goto start

:end
echo.
echo 启动器执行完毕
echo 日志保存在: %LOG_DIR%
if "%choice%"=="3" goto show_urls
if "%choice%"=="4" goto show_urls
pause
goto show_urls

:show_urls
echo.
echo ========================================
echo 服务访问地址:
echo ========================================
echo 后端API:    http://127.0.0.1:8000
echo 前端界面:  http://localhost:5173
echo API文档:    http://127.0.0.1:8000/api/docs/
echo 管理后台:  http://127.0.0.1:8000/admin/
echo ========================================
echo.
echo 常用操作:
echo - 查看后端日志: type %LOG_DIR%\backend.log
echo - 查看前端日志: type %LOG_DIR%\frontend.log
echo - 停止服务: 关闭对应的命令行窗口
echo ========================================