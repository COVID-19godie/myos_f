# ZMG OS 前端项目

## 项目结构
```
frontend/
├── src/                    # 源代码目录
│   ├── assets/            # 静态资源
│   ├── components/        # 组件
│   ├── views/             # 页面
│   ├── utils/             # 工具函数
│   └── main.js            # 入口文件
├── public/                # 公共资源
│   └── index.html         # HTML 模板
├── package.json           # 项目配置
└── vite.config.js         # 构建配置
```

## 开发环境配置

### API 配置
前端通过环境变量配置 API 地址：
- 开发环境：`http://localhost:8000/api`
- 生产环境：根据部署环境动态配置

### 跨域配置
后端需要允许前端域名跨域访问。