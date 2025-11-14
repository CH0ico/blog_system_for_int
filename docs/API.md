# 博客系统 API 文档

## 概述

本文档描述了博客系统的 RESTful API 接口，包括认证、文章管理、评论系统、用户管理等功能。

## 认证

### 登录

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123",
  "remember": false
}
```

**响应:**

```json
{
  "message": "登录成功",
  "user": {
    "id": 1,
    "username": "demo_user",
    "email": "demo@example.com",
    "nickname": "演示用户",
    "avatar": "",
    "bio": "",
    "website": "",
    "location": "",
    "followers_count": 10,
    "following_count": 5,
    "posts_count": 3,
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 注册

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "nickname": "新用户"
}
```

### 刷新Token

```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

### 获取当前用户信息

```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

## 文章管理

### 获取文章列表

```http
GET /api/posts?page=1&per_page=10&search=关键词&tag=vue&category=前端
```

**查询参数:**
- `page`: 页码，默认为1
- `per_page`: 每页数量，默认为10
- `search`: 搜索关键词
- `tag`: 标签slug
- `category`: 分类slug
- `author`: 作者用户名
- `sort_by`: 排序字段 (created_at, view_count, like_count, comment_count)
- `order`: 排序顺序 (asc, desc)

**响应:**

```json
{
  "posts": [
    {
      "id": 1,
      "title": "文章标题",
      "slug": "article-title",
      "summary": "文章摘要...",
      "status": "published",
      "is_featured": false,
      "allow_comments": true,
      "view_count": 100,
      "like_count": 20,
      "comment_count": 5,
      "favorite_count": 3,
      "author": {
        "id": 1,
        "username": "demo_user",
        "nickname": "演示用户",
        "avatar": ""
      },
      "tags": [
        {
          "id": 1,
          "name": "Vue.js",
          "slug": "vue-js"
        }
      ],
      "categories": [
        {
          "id": 1,
          "name": "前端开发",
          "slug": "frontend"
        }
      ],
      "liked": false,
      "favorited": false,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00",
      "published_at": "2024-01-01T00:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "pages": 10,
    "has_prev": false,
    "has_next": true
  }
}
```

### 获取单篇文章

```http
GET /api/posts/{post_id}
```

### 创建文章

```http
POST /api/posts
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "新文章标题",
  "content": "文章内容（支持Markdown）",
  "summary": "文章摘要（可选）",
  "tags": ["Vue.js", "前端"],
  "categories": ["前端开发"],
  "status": "published",
  "is_featured": false,
  "allow_comments": true
}
```

### 更新文章

```http
PUT /api/posts/{post_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "更新后的标题",
  "content": "更新后的内容"
}
```

### 删除文章

```http
DELETE /api/posts/{post_id}
Authorization: Bearer <access_token>
```

### 点赞文章

```http
POST /api/posts/{post_id}/like
Authorization: Bearer <access_token>
```

### 收藏文章

```http
POST /api/posts/{post_id}/favorite
Authorization: Bearer <access_token>
```

## 评论系统

### 获取文章评论

```http
GET /api/posts/{post_id}/comments?page=1&per_page=10
```

### 创建评论

```http
POST /api/posts/{post_id}/comments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "评论内容",
  "parent_id": null
}
```

## 用户管理

### 关注用户

```http
POST /api/users/{user_id}/follow
Authorization: Bearer <access_token>
```

### 获取用户信息

```http
GET /api/users/{username}
```

## 标签和分类

### 获取所有标签

```http
GET /api/posts/tags
```

### 获取所有分类

```http
GET /api/posts/categories
```

## 通知系统

### 获取用户通知

```http
GET /api/notifications?page=1&per_page=20&unread_only=false
Authorization: Bearer <access_token>
```

### 标记通知为已读

```http
PUT /api/notifications/{notification_id}/read
Authorization: Bearer <access_token>
```

## 数据统计

### 获取仪表板统计

```http
GET /api/stats/dashboard
Authorization: Bearer <access_token>
```

**响应:**

```json
{
  "total_posts": 10,
  "total_views": 1000,
  "total_likes": 200,
  "total_comments": 50,
  "unread_notifications": 5,
  "followers_count": 100,
  "following_count": 50,
  "view_trend": [
    {
      "date": "2024-01-01",
      "views": 100
    }
  ]
}
```

## 搜索

### 获取搜索建议

```http
GET /api/posts/search/suggestions?q=关键词
```

## 热门内容

### 获取热门文章

```http
GET /api/posts/popular?limit=10&period=week
```

### 获取推荐文章

```http
GET /api/posts/featured?limit=10
```

## 归档

### 获取文章归档

```http
GET /api/posts/archives
```

## WebSocket 事件

### 客户端事件

- `user_online`: 用户上线
- `join_post`: 加入文章房间
- `leave_post`: 离开文章房间
- `typing`: 正在输入
- `stop_typing`: 停止输入

### 服务器事件

- `connected`: 连接成功
- `online_count`: 在线用户数更新
- `new_comment`: 新评论
- `user_typing`: 用户正在输入
- `user_stop_typing`: 用户停止输入
- `new_notification`: 新通知

## 错误处理

### 错误响应格式

```json
{
  "message": "错误描述",
  "error": "错误代码",
  "status_code": 400,
  "details": {
    "field": "具体错误信息"
  }
}
```

### 常见错误代码

- `missing_fields`: 缺少必填字段
- `invalid_email`: 邮箱格式错误
- `invalid_password`: 密码格式错误
- `invalid_username`: 用户名格式错误
- `email_exists`: 邮箱已存在
- `username_exists`: 用户名已存在
- `invalid_credentials`: 用户名或密码错误
- `account_disabled`: 账户被禁用
- `access_denied`: 无权限访问
- `token_expired`: Token已过期
- `invalid_token`: Token无效

## 状态码

- `200`: 成功
- `201`: 创建成功
- `400`: 请求错误
- `401`: 未认证
- `403`: 无权限
- `404`: 资源不存在
- `422`: 验证错误
- `429`: 请求过于频繁
- `500`: 服务器内部错误

## 分页

所有列表接口都支持分页，返回格式如下:

```json
{
  "data": [...], // 数据列表
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "pages": 10,
    "has_prev": false,
    "has_next": true
  }
}
```

## 认证

所有需要认证的接口都需要在请求头中包含:

```
Authorization: Bearer <access_token>
```

## 速率限制

API 有速率限制，超出限制会返回 `429` 状态码。