# 🚀 快速启动指南

## 第一步：安装依赖

```bash
pip install -r requirements.txt
```

## 第二步：数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

## 第三步：创建超级管理员

```bash
python manage.py createsuperuser
```
按照提示输入用户名、邮箱和密码。

## 第四步：创建测试分类

登录后台管理：
1. 启动服务器：`python manage.py runserver`
2. 访问：http://localhost:8000/admin/
3. 使用刚创建的超级管理员账号登录
4. 在"Resource categories"中创建几个分类（如：物理、数学、英语）

## 第五步：启动服务器

```bash
python manage.py runserver
```

## 第六步：打开前端

直接在浏览器中打开 `index.html` 文件，或双击文件。

---

## 📡 API 接口清单

### 1. 认证模块
- `POST /api/auth/register/` - 注册新用户
- `POST /api/auth/login/` - 登录（返回 Access Token）
- `POST /api/auth/refresh/` - 刷新 Token

### 2. 用户模块
- `GET /api/users/me/` - 获取当前登录用户信息（头像、积分、角色）
- `GET /api/users/` - 获取用户列表（仅管理员）

### 3. 资源模块
- `GET /api/resources/` - 获取资源列表（支持搜索、筛选、排序）
- `POST /api/resources/` - 上传资源
- `GET /api/resources/{id}/` - 获取资源详情
- `POST /api/resources/{id}/like/` - 点赞/取消点赞
- `POST /api/resources/{id}/view/` - 增加浏览量

### 4. 评论系统
- `POST /api/resources/{id}/comment/` - 发送评论
- `GET /api/resources/{id}/comments/` - 获取评论列表

### 5. AI 功能
- `POST /api/resources/{id}/ai_tagging/` - AI 自动生成标签

---

## 🎯 测试流程

### 登录测试
1. 打开 index.html
2. 输入超级管理员账号和密码
3. 点击"登录"

### 上传资源测试
1. 右键点击桌面，选择"上传资源"
2. 或者直接拖拽文件到页面
3. 填写标题、选择分类、填写描述
4. 点击"立即发布"

### AI 标签测试
1. 上传资源后，在描述中输入一些关键词（如"物理公式"、"期末考试"）
2. 调用 AI 标签接口

### 评论测试
1. 点击任意资源图标
2. 使用评论 API 发送评论

---

## 🔍 搜索与筛选示例

- 搜索物理资源：`GET /api/resources/?search=物理`
- 按分类筛选：`GET /api/resources/?category=1`
- 按浏览量排序：`GET /api/resources/?ordering=-views`

---

## 🎨 前端功能

- ✨ iPadOS 风格磨砂玻璃效果
- 🎯 智能拖拽上传
- 🖱️ 右键菜单快捷操作
- 📱 响应式设计
- 🚀 Dock 栏悬浮效果

---

## ⚙️ 配置说明

### Token 有效期
默认 7 天，可在 `settings.py` 中修改：

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
}
```

### CORS 配置
已允许所有来源跨域访问：

```python
CORS_ALLOW_ALL_ORIGINS = True
```

### 媒体文件
上传的文件存储在 `media/` 目录下：
- 头像：`media/avatars/`
- 封面：`media/covers/`
- 资源：`media/resources/`

---

## 🛠️ 开发者指南

### 添加新功能
1. 在 `core/models.py` 定义模型
2. 在 `core/serializers.py` 创建序列化器
3. 在 `core/views.py` 编写视图逻辑
4. 在 `zmg_backend/urls.py` 配置路由
5. 运行迁移：`python manage.py makemigrations && python manage.py migrate`

### 集成真实 AI
修改 `core/ai_utils.py`，替换模拟代码为真实的 AI API 调用：

```python
import openai

def analyze_text_with_ai(text):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"为以下内容生成标签：{text}",
        max_tokens=100
    )
    return response.choices[0].text.strip()
```

---

## 📞 常见问题

### Q: 登录失败？
A: 检查用户名和密码是否正确，确保已创建超级管理员。

### Q: 上传失败？
A: 确保：
- 已创建分类
- `media/` 目录存在且有写权限
- 文件大小不超过限制

### Q: 前端无法访问后端？
A: 确保：
- Django 服务已启动
- `CORS_ALLOW_ALL_ORIGINS = True`
- API 地址配置正确（`http://127.0.0.1:8000/api`）

---

## 🎉 完成！

现在你拥有一个功能完整的教育资源社区平台，包括：
- 用户认证系统（JWT）
- 资源上传与管理
- 评论与互动
- AI 智能标签
- 精美的前端界面

开始探索吧！
