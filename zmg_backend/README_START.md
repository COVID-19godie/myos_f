# ZMG Backend 启动指南

## 🚀 快速启动方式

### 方式一：Windows 用户（推荐）
双击运行 `start.bat`，按照提示选择启动模式。

### 方式二：Linux/Mac 用户
```bash
chmod +x start.sh
./start.sh
```

### 方式三：Python 脚本启动
```bash
python quick_start.py
```

### 方式四：手动启动
```bash
# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 启动服务器
python manage.py runserver
```

## 📋 启动选项说明

1. **启动开发服务器** - 标准Django开发服务器，支持代码热重载
2. **启动带自动重载的开发服务器** - 禁用某些重载功能，适合调试
3. **仅检查配置** - 验证项目配置和数据库连接
4. **退出** - 退出启动程序

## 🌐 访问地址

- **主应用**: http://127.0.0.1:8000
- **管理后台**: http://127.0.0.1:8000/admin
- **API文档**: 根据项目配置可能存在 `/api/docs/`

## ⚙️ 项目特性

- ✅ Django REST Framework API
- ✅ JWT 认证
- ✅ CORS 跨域支持
- ✅ SQLite 数据库
- ✅ 中文界面支持
- ✅ 分页和过滤功能

## 🔧 故障排除

1. **端口被占用**: 修改启动端口 `python manage.py runserver 8001`
2. **依赖安装失败**: 检查网络连接或使用国内镜像源
3. **数据库错误**: 删除 `db.sqlite3` 重新迁移
4. **静态文件问题**: 运行 `python manage.py collectstatic`

## 📞 技术支持

如遇问题请检查：
- Python版本 >= 3.7
- 虚拟环境是否正确激活
- requirements.txt中的所有包是否安装成功