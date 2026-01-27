#!/bin/bash
# ZMG Backend 启动脚本

echo "========================================"
echo "         ZMG Backend 启动程序"
echo "========================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] Python3未安装或未添加到环境变量"
    exit 1
fi

echo "[信息] Python3已安装"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "[信息] 创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[错误] 创建虚拟环境失败"
        exit 1
    fi
fi

echo "[信息] 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "[信息] 检查并安装依赖包..."
pip install -r requirements.txt

# 数据库迁移
echo "[信息] 执行数据库迁移..."
python manage.py migrate

# 加载初始数据（如果存在）
if [ -f "init_data.py" ]; then
    echo "[信息] 加载初始数据..."
    python init_data.py
fi

echo
echo "[成功] 启动准备完成！"
echo
echo "选择运行模式："
echo "1. 启动开发服务器 (推荐)"
echo "2. 启动带自动重载的开发服务器"
echo "3. 仅检查配置"
echo "4. 退出"
echo
read -p "请输入选择 (1-4): " choice

echo
case $choice in
    1)
        echo "[信息] 启动开发服务器..."
        echo "访问地址: http://127.0.0.1:8000"
        echo "按 Ctrl+C 停止服务器"
        echo
        python manage.py runserver
        ;;
    2)
        echo "[信息] 启动带自动重载的开发服务器..."
        echo "访问地址: http://127.0.0.1:8000"
        echo "按 Ctrl+C 停止服务器"
        echo
        python manage.py runserver --noreload
        ;;
    3)
        echo "[信息] 检查项目配置..."
        python manage.py check
        echo
        python manage.py showmigrations
        ;;
    4)
        echo "[信息] 退出程序"
        ;;
    *)
        echo "[错误] 无效选择"
        ;;
esac