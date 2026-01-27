# ZMG Cloud OS - 故障排查指南

## 🔍 常见错误诊断

### 1. API 500 错误 (`/api/token/` 返回 500)

#### 症状
```
Failed to load resource: the server responded with a status of 500 (Internal Server Error)
api/token/:1
登录失败: AxiosError: Request failed with status code 500
```

#### 可能原因及解决方案

##### 原因 A: 后端服务未运行
**检查方法:**
```bash
# Windows
netstat -ano | findstr :8000

# 或访问浏览器
http://localhost:8000/api/health/
```

**解决方案:**
```bash
# 进入后端目录
cd ..\backend

# 启动 Django 后端
python manage.py runserver 8000
```

或使用提供的启动脚本:
```batch
start-all.bat
```

##### 原因 B: 数据库未迁移
**检查方法:**
访问 http://localhost:8000/admin/ 是否能打开

**解决方案:**
```bash
cd ..\backend
python manage.py makemigrations
python manage.py migrate
```

##### 原因 C: CORS 配置问题
**检查 Django settings.py:**
```python
# 确保安装了 django-cors-headers
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 必须放在最前面
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True
```

**安装依赖:**
```bash
cd ..\backend
pip install django-cors-headers
```

##### 原因 D: JWT 认证未配置
**检查 settings.py:**
```python
# REST Framework 配置
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
]

# JWT 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```

**安装依赖:**
```bash
pip install djangorestframework
pip install djangorestframework-simplejwt
```

---

### 2. favicon.ico 404 错误

#### 症状
```
Failed to load resource: the server responded with a status of 404 (Not Found)
favicon.ico:1
```

#### 影响
- 不影响功能，仅控制台警告
- 浏览器会自动请求，可忽略

#### 解决方案（可选）
已在 `public/favicon.svg` 添加图标文件，`index.html` 已引用。

---

## 🔧 诊断工具

### 使用内置诊断工具

#### 1. 启动器诊断
访问: http://localhost:3000/launcher.html
- 实时检查前端、后端、API 状态
- 一键启动应用或调试工具

#### 2. API 调试工具
访问: http://localhost:3000/api-debug.html
- 实时日志
- API 端点测试
- 服务状态监控

#### 3. 后端诊断工具
访问: http://localhost:3000/debug-backend.html
- 后端健康检查
- 登录接口测试
- API 代理测试

---

## 📝 完整排查流程

### 步骤 1: 检查后端服务

```bash
# 1. 检查端口是否被占用
netstat -ano | findstr :8000

# 2. 如果被占用，查看进程
netstat -ano | findstr :8000
tasklist | findstr <PID>

# 3. 如果需要终止进程
taskkill /F /PID <PID>

# 4. 启动后端
cd ..\backend
python manage.py runserver 8000
```

### 步骤 2: 检查数据库

```bash
cd ..\backend

# 检查数据库文件
dir db.sqlite3

# 如果不存在，执行迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户（如果需要）
python manage.py createsuperuser
```

### 步骤 3: 检查前端配置

```bash
cd frontend

# 检查 Vite 配置
type vite.config.js

# 确认代理配置正确
# target: 'http://localhost:8000'
```

### 步骤 4: 测试接口

#### 方法 A: 使用诊断工具
1. 打开 http://localhost:3000/debug-backend.html
2. 点击"开始诊断"
3. 查看测试结果

#### 方法 B: 使用 curl
```bash
# 测试后端直连
curl http://localhost:8000/api/health/

# 测试 Vite 代理
curl http://localhost:3000/api/health/

# 测试登录接口
curl -X POST http://localhost:8000/api/token/ -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

#### 方法 C: 使用浏览器开发者工具
1. 按 F12 打开开发者工具
2. 切换到 Network 标签
3. 尝试登录
4. 查看请求和响应详情

---

## 🚀 快速修复命令

### Windows 批处理脚本

```batch
@echo off
echo 🔧 ZMG Cloud OS - 快速修复脚本

REM 1. 停止占用端口的进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo 终止进程 %%a
    taskkill /F /PID %%a
)

REM 2. 重新安装前端依赖
cd frontend
echo 正在重新安装依赖...
call npm install

REM 3. 启动服务
echo 启动服务...
call start-all.bat
```

---

## 💡 预防措施

### 开发环境配置

#### 前端配置检查清单
- [x] Vite 代理配置正确 (`vite.config.js`)
- [x] API 基础地址正确 (`src/services/api.ts`)
- [x] 智能API配置启用 (`src/services/smartApi.js`)
- [x] CORS 设置正确

#### 后端配置检查清单
- [x] Django CORS 配置
- [x] JWT 认证配置
- [x] 数据库已迁移
- [x] 管理员用户已创建

---

## 📞 获取帮助

### 检查日志

**前端日志:**
- 浏览器控制台 (F12 → Console)
- Vite 开发服务器输出

**后端日志:**
- Django 服务器输出
- 查看 Django 错误页面详情

### 常见问题速查表

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 500 Internal Server Error | 后端代码错误 | 检查后端日志 |
| 401 Unauthorized | Token 无效或过期 | 重新登录 |
| 404 Not Found | 接口不存在 | 检查 API 路径 |
| CORS 错误 | 跨域配置问题 | 检查 Django CORS 设置 |
| Connection Refused | 后端未启动 | 启动后端服务 |

---

## 🎯 推荐启动方式

### 日常开发
```batch
quick-start.bat
```

### 完整启动（前后端）
```batch
start-all.bat
```

### 调试模式
```batch
# 终端 1 - 后端
cd ..\backend
python manage.py runserver 8000

# 终端 2 - 前端
cd frontend
npm run dev

# 浏览器 - 诊断工具
# 访问 http://localhost:3000/debug-backend.html
```
