# ZMG Community - Django REST Framework 后端

## 项目说明

这是一个功能完整的 Django + DRF 后端项目，专为教育资源社区设计，包含：
- 用户体系（学生、教师、管理员角色）
- 资源管理（上传、审核、分类）
- AI 预留接口（向量搜索、自动标签）
- RESTful API

## 安装依赖

```bash
pip install -r requirements.txt
```

## 初始化数据库

```bash
python manage.py makemigrations
python manage.py migrate
```

## 创建超级管理员

```bash
python manage.py createsuperuser
```

## 启动服务器

```bash
python manage.py runserver
```

## API 端点

- `GET /api/resources/` - 获取资源列表
- `POST /api/resources/` - 上传资源
- `GET /api/resources/{id}/` - 获取资源详情
- `POST /api/resources/{id}/like/` - 点赞
- `POST /api/resources/{id}/view/` - 增加浏览量
- `GET /api/categories/` - 获取分类列表

## 后台管理

访问 `http://localhost:8000/admin/` 使用超级管理员登录，可以：
- 管理用户
- 审核资源
- 管理分类

## 权限说明

- **游客**: 只能浏览已发布的资源
- **学生**: 可以上传资源（需审核）、点赞、浏览
- **教师**: 可以上传资源（自动通过审核）
- **管理员**: 可以审核资源、管理所有内容

## 搜索与筛选

- 搜索: `?search=物理`
- 按分类筛选: `?category=1`
- 排序: `?ordering=-views`
