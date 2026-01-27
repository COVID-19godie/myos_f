@echo off
chcp 65001 >nul
echo.
echo ========================================
echo         🔧 Node.js 环境配置向导
echo ========================================
echo.

:: 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Node.js，请先安装Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

node --version
npm --version
echo ✅ Node.js环境正常
echo.

:: 切换到前端目录
cd /d "d:\MyOS\frontend"
echo 📁 当前目录: %CD%
echo.

:: 检查package.json是否存在
if not exist "package.json" (
    echo ❌ 未找到 package.json
    echo 正在创建...
    copy "d:\MyOS\frontend\package.json.template" "d:\MyOS\frontend\package.json" >nul 2>&1
    if errorlevel 1 (
        echo 创建package.json失败，请手动创建
        pause
        exit /b 1
    )
)

echo 📦 正在安装前端依赖包...
echo 这可能需要几分钟时间，请耐心等待...
echo.

:: 使用cmd直接执行npm install
cmd /c "npm install"

if errorlevel 1 (
    echo.
    echo ❌ npm install 失败
    echo 尝试使用yarn...
    
    :: 检查yarn
    yarn --version >nul 2>&1
    if not errorlevel 1 (
        yarn install
        if errorlevel 1 (
            echo ❌ yarn install 也失败了
            echo 请检查网络连接或手动安装依赖
        ) else (
            echo ✅ yarn install 成功
        )
    ) else (
        echo ❌ 未找到yarn，请手动安装依赖
    )
) else (
    echo.
    echo ✅ 依赖包安装成功！
)

echo.
echo ========================================
echo 🎉 Node.js 配置完成！
echo.
echo 📱 现在可以使用以下命令启动前端:
echo   cd frontend
cho   npm run dev
echo.
echo 🔗 前端将运行在: http://localhost:3000
echo ========================================
echo.
pause