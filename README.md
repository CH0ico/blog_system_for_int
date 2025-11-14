# 现代博客系统 - 全栈开发文档

## 项目概述

这是一个功能完整的前后端分离博客系统，采用现代化的技术栈：
- **前端**: Vue.js 3 + Composition API + Element Plus
- **后端**: Flask + SQLAlchemy + JWT认证
- **通信**: HTTP/HTTPS + WebSocket实时通信
- **数据库**: SQLite(开发) / MySQL(生产)

## 核心功能特性

### 📝 文章管理
- 富文本编辑器支持Markdown
- 文章分类和标签系统
- 文章搜索和高级过滤
- 文章浏览统计

### 👥 用户系统
- JWT认证和权限控制
- 用户注册/登录/个人资料
- 用户头像上传(暂无)
- 记住登录状态

### 💬 互动功能
- 评论和回复系统(暂无)
- 文章点赞和收藏
- 用户关注系统
- 实时消息通知(暂无)

### 📊 数据分析
- 文章浏览统计
- 用户活跃度分析(暂无)
- 热门文章排行
- 实时在线用户

### 🔧 技术特性
- WebSocket实时通信
- TCP连接优化
- RESTful API设计
- 前后端分离架构

## 项目结构

```
blog_system/
├── backend/                # Flask后端
│   ├── app.py              # 主应用文件
│   ├── models.py           # 数据库模型
│   ├── routes/             # API路由
│   ├── utils/              # 工具函数
│   └── requirements.txt    # Python依赖
├── frontend/               # Vue.js前端
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   └── store/          # 状态管理
│   └── package.json        # 项目配置
├── database/               # 数据库相关
└── docs/                   # 项目文档
```

## 技术栈

### 后端技术
- **Flask** - Web框架
- **Flask-SQLAlchemy** - ORM数据库
- **Flask-JWT-Extended** - JWT认证
- **Flask-CORS** - 跨域处理
- **Flask-SocketIO** - WebSocket通信
- **Flask-Mail** - 邮件服务(没有做)

### 前端技术
- **Vue.js 3** - 渐进式JavaScript框架
- **Vue Router 4** - 路由管理
- **Vuex 4** - 状态管理
- **Element Plus** - UI组件库
- **Axios** - HTTP客户端
- **Markdown编辑器** - 富文本编辑

### 数据库
- **SQLite** - 开发环境
- **MySQL** - 生产环境

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 14+
- SQLite/MySQL

### 后端启动
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 数据库初始化
```bash
python backend/app.py init_db
```

## API文档

详细的API文档请参考 `docs/API.md`

## 部署指南

生产环境部署请参考 `docs/DEPLOY.md`

## 开发团队

本项目采用现代化开发流程，支持热重载、代码规范检查、自动化测试等开发最佳实践。

# 已实现
见readme文档

# 待实现
### 重要
1. "写文章" (目前是直接数据库上传的)
2. 文章"评论",阅读详情时的高级渲染
3. 分类/标签页 最好点击可以罗列出对应的列表
4. 自选题: AI 看板娘 RSS订阅等

### 次重要
1. TCP HTTP底层看看能不能优化 不是很懂老师的意思
2. 个人中心, 相互访问没做, 目前没法关注用户 (数据库和前端都做了 没有做实现逻辑)
3. 忘记密码功能没做 专门再做一个邮件服务可能有点冗余..
4. 用户头像(数据库做了预留 上传功能前端没做还 很简单)
5. 通知功能