#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask后端主应用
集成JWT认证、WebSocket通信、RESTful API
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from functools import wraps
import json
import logging
from threading import Thread
from queue import Queue

from flask import Flask, request, jsonify, g, Response
from flask import send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_mail import Mail, Message
from werkzeug.exceptions import HTTPException

from models import db, User, Post, Comment, Tag, Category, Like, Favorite, Follow, Notification, ViewLog
from utils.validators import (
    validate_email, validate_password, validate_username, validate_post_title,
    validate_post_content, validate_tag_name, validate_category_name,
    generate_excerpt, validate_slug, validate_comment_content
)
from utils.auth import generate_confirmation_token, confirm_token
from routes.posts import posts_bp
from routes.auth import auth_bp
from utils.renderer import render_markdown

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask应用配置
app = Flask(__name__)

# 基础配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')
app.config['PORT'] = int(os.environ.get('PORT', '5001'))

# CORS配置
app.config['CORS_ORIGINS'] = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
app.config['CORS_SUPPORTS_CREDENTIALS'] = False

# 邮件配置
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@blog.com')

# SocketIO配置
app.config['SOCKETIO_MESSAGE_QUEUE'] = os.environ.get('REDIS_URL', None)

# 初始化扩展
db.init_app(app)
jwt = JWTManager(app)
mail = Mail(app)

# CORS初始化
cors = CORS(app, resources={
    r"/api/*": {
        "origins": app.config['CORS_ORIGINS'],
        "supports_credentials": True
    }
})

# SocketIO初始化
socketio = SocketIO(app, cors_allowed_origins=app.config['CORS_ORIGINS'], logger=True, engineio_logger=True)

# 注册蓝图
app.register_blueprint(posts_bp, url_prefix='/api/posts')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# 用户自己的文章（含草稿）
@app.route('/api/posts/mine', methods=['GET'])
@jwt_required()
def get_my_posts():
    current_user_id = get_jwt_identity()
    status = request.args.get('status', None)
    query = Post.query.filter_by(author_id=current_user_id)
    if status:
        query = query.filter_by(status=status)
    query = query.order_by(Post.updated_at.desc())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    posts = [p.to_dict(include_content=False) for p in pagination.items]
    return jsonify({
        'posts': posts,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    })

# 全局变量存储在线用户
online_users = {}
notification_queue = Queue()

# JWT回调函数
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    return jsonify({'message': 'Token已过期', 'error': 'token_expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'message': 'Token无效', 'error': 'invalid_token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'message': '缺少Token', 'error': 'authorization_required'}), 401

# 全局错误处理
@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return jsonify({
        'message': e.description,
        'error': e.name.lower().replace(' ', '_'),
        'status_code': e.code
    }), e.code

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({
        'message': '服务器内部错误',
        'error': 'internal_server_error',
        'status_code': 500
    }), 500

# 请求前处理
@app.before_request
def before_request():
    g.start_time = datetime.now(timezone.utc)
    
    # 记录请求日志
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def after_request(response):
    # 计算响应时间
    if hasattr(g, 'start_time'):
        duration = datetime.now(timezone.utc) - g.start_time
        response.headers['X-Response-Time'] = f"{duration.total_seconds():.3f}s"
    
    return response

# 工具函数
def send_async_email(app, msg):
    """异步发送邮件"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")

def send_email(subject, recipients, body, html_body=None):
    """发送邮件"""
    msg = Message(subject, recipients=recipients, body=body, html=html_body or body)
    Thread(target=send_async_email, args=(app, msg)).start()

def create_notification(user_id, type, title, message, actor_id=None, post_id=None, comment_id=None, extra_data=None):
    """创建通知"""
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        actor_id=actor_id,
        post_id=post_id,
        comment_id=comment_id,
        data=json.dumps(extra_data) if extra_data else None
    )
    db.session.add(notification)
    db.session.commit()
    
    # 通过WebSocket发送实时通知
    if str(user_id) in online_users:
        socketio.emit('new_notification', notification.to_dict(), room=f"user_{user_id}")
    
    return notification

def broadcast_online_count():
    """广播在线用户数"""
    socketio.emit('online_count', {'count': len(online_users)})

# SocketIO事件处理
@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected successfully'})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    logger.info(f"Client disconnected: {request.sid}")
    
    # 从在线用户列表中移除
    user_id_to_remove = None
    for user_id, sid in online_users.items():
        if sid == request.sid:
            user_id_to_remove = user_id
            break
    
    if user_id_to_remove:
        del online_users[user_id_to_remove]
        leave_room(f"user_{user_id_to_remove}")
        broadcast_online_count()

@socketio.on('user_online')
def handle_user_online(data):
    """用户上线"""
    user_id = str(data.get('user_id'))
    online_users[user_id] = request.sid
    join_room(f"user_{user_id}")
    
    logger.info(f"User {user_id} is online")
    broadcast_online_count()

@socketio.on('join_post')
def handle_join_post(data):
    """加入文章房间"""
    post_id = data.get('post_id')
    if post_id:
        join_room(f"post_{post_id}")
        emit('joined_post', {'post_id': post_id})

@socketio.on('leave_post')
def handle_leave_post(data):
    """离开文章房间"""
    post_id = data.get('post_id')
    if post_id:
        leave_room(f"post_{post_id}")

@socketio.on('typing')
def handle_typing(data):
    """正在输入"""
    post_id = data.get('post_id')
    user_id = data.get('user_id')
    if post_id and user_id:
        emit('user_typing', {
            'user_id': user_id,
            'post_id': post_id
        }, room=f"post_{post_id}", include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    """停止输入"""
    post_id = data.get('post_id')
    user_id = data.get('user_id')
    if post_id and user_id:
        emit('user_stop_typing', {
            'user_id': user_id,
            'post_id': post_id
        }, room=f"post_{post_id}", include_self=False)


# API路由 - 文章相关
@app.route('/api/posts', methods=['GET'])
def get_posts():
    """获取文章列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '').strip()
    tag = request.args.get('tag', '').strip()
    category = request.args.get('category', '').strip()
    author = request.args.get('author', '').strip()
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    
    # 基础查询
    query = Post.query.filter_by(status='published')
    
    # 搜索过滤
    if search:
        query = query.filter(Post.title.contains(search) | Post.content.contains(search))
    
    if tag:
        query = query.join(Post.tags).filter(Tag.slug == tag)
    
    if category:
        query = query.join(Post.categories).filter(Category.slug == category)
    
    if author:
        query = query.join(User).filter(User.username == author)
    
    # 排序
    if sort_by == 'view_count':
        sort_field = Post.view_count
    elif sort_by == 'like_count':
        sort_field = Post.like_count
    elif sort_by == 'comment_count':
        sort_field = Post.comment_count
    else:
        sort_field = Post.created_at
    
    if order == 'asc':
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items
    
    return jsonify({
        'posts': [post.to_dict(include_content=False) for post in posts],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    })

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """获取单篇文章详情"""
    post = Post.query.get_or_404(post_id)
    
    if post.status != 'published':
        current_user_id = get_jwt_identity() if request.headers.get('Authorization') else None
        # 检查是否有权限查看草稿
        if not current_user_id or post.author_id != current_user_id:
            return jsonify({'message': '文章不存在或无权限查看', 'error': 'access_denied'}), 404
    
    # 增加浏览次数
    # 增加浏览次数
    post.increment_view_count()
    
    # 记录浏览日志
    user_id = get_jwt_identity() if request.headers.get('Authorization') else None

@app.route('/api/posts', methods=['POST'])
@jwt_required()
def create_post():
    """创建新文章"""
    data = request.get_json()
    
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    summary = data.get('summary', '').strip()
    tags = data.get('tags', [])
    categories = data.get('categories', [])
    status = data.get('status', 'draft')
    allow_comments = data.get('allow_comments', True)
    
    if not title or not content:
        return jsonify({'message': '标题和内容不能为空', 'error': 'missing_fields'}), 400
    if not validate_post_title(title):
        return jsonify({'message': '标题长度不能超过200个字符', 'error': 'invalid_title'}), 400
    if not validate_post_content(content):
        return jsonify({'message': '内容长度不能少于10个字符', 'error': 'invalid_content'}), 400
    if status not in ['draft', 'published', 'archived']:
        return jsonify({'message': '文章状态无效', 'error': 'invalid_status'}), 400
    
    # 生成slug
    slug = data.get('slug', title.lower().replace(' ', '-'))
    if not validate_slug(slug):
        slug = title.lower().replace(' ', '-')
    
    # 检查slug是否已存在
    if Post.query.filter_by(slug=slug).first():
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
    
    current_user_id = get_jwt_identity()
    
    post = Post(
        title=title,
        slug=slug,
        content=content,
        content_html=render_markdown(content),
        summary=summary or generate_excerpt(content),
        status=status,
        allow_comments=allow_comments,
        author_id=current_user_id
    )
    
    if status == 'published':
        post.published_at = datetime.now(timezone.utc)
    

    db.session.add(post)

    # 处理标签
    if tags:
        for tag_name in tags:
            if not validate_tag_name(tag_name):
                continue
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name, slug=tag_name.lower().replace(' ', '-'))
                db.session.add(tag)
            post.tags.append(tag)
    
    # 处理分类
    if categories:
        for category_name in categories:
            if not validate_category_name(category_name):
                continue
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name, slug=category_name.lower().replace(' ', '-'))
                db.session.add(category)
            post.categories.append(category)
    
    
    
    # 更新用户的文章计数
    user = User.query.get(current_user_id)
    user.posts_count += 1
    
    db.session.commit()
    
    # 通知关注者
    followers = user.followers.all()
    for follower in followers:
        create_notification(
            user_id=follower.id,
            type='new_post',
            title='新文章发布',
            message=f'{user.nickname or user.username} 发布了新文章《{post.title}》',
            actor_id=user.id,
            post_id=post.id
        )
    
    return jsonify({
        'message': '文章创建成功',
        'post': post.to_dict()
    }), 201

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """更新文章"""
    post = Post.query.get_or_404(post_id)
    current_user_id = get_jwt_identity()
    
    # 检查权限
    if post.author_id != current_user_id:
        return jsonify({'message': '无权限编辑此文章', 'error': 'access_denied'}), 403
    
    data = request.get_json()
    
    # 更新字段
    if 'title' in data:
        title = data['title'].strip()
        if not validate_post_title(title):
            return jsonify({'message': '标题长度不能超过200个字符', 'error': 'invalid_title'}), 400
        post.title = title

    if 'content' in data:
        content = data['content'].strip()
        if not validate_post_content(content):
            return jsonify({'message': '内容长度不能少于10个字符', 'error': 'invalid_content'}), 400
        post.content = content
        post.content_html = render_markdown(content)
        post.summary = generate_excerpt(content)

    if 'summary' in data:
        post.summary = data['summary'].strip()

    if 'allow_comments' in data:
        post.allow_comments = bool(data['allow_comments'])

    if 'status' in data:
        new_status = data['status']
        if new_status in ['draft', 'published', 'archived']:
            post.status = new_status
            if new_status == 'published' and not post.published_at:
                post.published_at = datetime.now(timezone.utc)
        else:
            return jsonify({'message': '文章状态无效', 'error': 'invalid_status'}), 400
    
    post.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify({
        'message': '文章更新成功',
        'post': post.to_dict()
    })

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """删除文章"""
    post = Post.query.get_or_404(post_id)
    current_user_id = get_jwt_identity()
    
    # 检查权限
    if post.author_id != current_user_id:
        return jsonify({'message': '无权限删除此文章', 'error': 'access_denied'}), 403
    
    db.session.delete(post)
    
    # 更新用户的文章计数
    user = User.query.get(current_user_id)
    user.posts_count -= 1
    
    db.session.commit()
    
    return jsonify({'message': '文章删除成功'})

# API路由 - 评论相关
@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    """获取文章评论"""
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 只显示已批准的评论
    comments = Comment.query.filter_by(
        post_id=post_id,
        parent_id=None,  # 顶级评论
        status='approved'
    ).order_by(Comment.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'comments': [comment.to_dict() for comment in comments.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': comments.total,
            'pages': comments.pages,
            'has_prev': comments.has_prev,
            'has_next': comments.has_next
        }
    })

@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    """创建评论"""
    post = Post.query.get_or_404(post_id)
    
    if not post.allow_comments:
        return jsonify({'message': '该文章不允许评论', 'error': 'comments_disabled'}), 400
    
    data = request.get_json()
    content = data.get('content', '').strip()
    parent_id = data.get('parent_id')
    
    if not validate_comment_content(content):
        return jsonify({'message': '评论内容不能为空或超过1000字', 'error': 'invalid_content'}), 400
    
    current_user_id = get_jwt_identity()
    
    comment = Comment(
        content=content,
        content_html=render_markdown(content),
        author_id=current_user_id,
        post_id=post_id,
        parent_id=parent_id
    )
    
    db.session.add(comment)
    
    # 更新文章评论计数
    post.comment_count += 1
    if parent_id:
        parent_comment = Comment.query.get(parent_id)
        if parent_comment:
            parent_comment.reply_count = (parent_comment.reply_count or 0) + 1
    
    db.session.commit()
    
    # 创建通知
    if parent_id:
        # 回复评论的通知
        parent_comment = Comment.query.get(parent_id)
        if parent_comment and parent_comment.author_id != current_user_id:
            create_notification(
                user_id=parent_comment.author_id,
                type='comment_reply',
                title='评论回复',
                message=f'有人回复了你的评论',
                actor_id=current_user_id,
                post_id=post_id,
                comment_id=comment.id
            )
    
    # 文章作者的通知
    if post.author_id != current_user_id:
        create_notification(
            user_id=post.author_id,
            type='new_comment',
            title='新评论',
            message=f'有人评论了你的文章《{post.title}》',
            actor_id=current_user_id,
            post_id=post_id,
            comment_id=comment.id
        )
    
    # 通过WebSocket广播新评论
    socketio.emit('new_comment', {
        'post_id': post_id,
        'comment': comment.to_dict()
    }, room=f"post_{post_id}")
    
    return jsonify({
        'message': '评论发布成功',
        'comment': comment.to_dict()
    }), 201

# API路由 - 社交功能
@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    """点赞文章"""
    post = Post.query.get_or_404(post_id)
    current_user_id = get_jwt_identity()
    
    # 检查是否已经点赞
    existing_like = Like.query.filter_by(
        user_id=current_user_id,
        post_id=post_id
    ).first()
    
    if existing_like:
        # 取消点赞
        db.session.delete(existing_like)
        post.like_count -= 1
        message = '已取消点赞'
        liked = False
    else:
        # 添加点赞
        like = Like(user_id=current_user_id, post_id=post_id)
        db.session.add(like)
        post.like_count += 1
        message = '点赞成功'
        liked = True
        
        # 创建通知（如果不是自己的文章）
        if post.author_id != current_user_id:
            create_notification(
                user_id=post.author_id,
                type='like',
                title='文章被点赞',
                message=f'有人点赞了你的文章《{post.title}》',
                actor_id=current_user_id,
                post_id=post_id
            )
    
    db.session.commit()
    
    return jsonify({
        'message': message,
        'liked': liked,
        'like_count': post.like_count
    })

@app.route('/api/posts/<int:post_id>/favorite', methods=['POST'])
@jwt_required()
def favorite_post(post_id):
    """收藏文章"""
    post = Post.query.get_or_404(post_id)
    current_user_id = get_jwt_identity()
    
    # 检查是否已经收藏
    existing_favorite = Favorite.query.filter_by(
        user_id=current_user_id,
        post_id=post_id
    ).first()
    
    if existing_favorite:
        # 取消收藏
        db.session.delete(existing_favorite)
        post.favorite_count -= 1
        message = '已取消收藏'
        favorited = False
    else:
        # 添加收藏
        favorite = Favorite(user_id=current_user_id, post_id=post_id)
        db.session.add(favorite)
        post.favorite_count += 1
        message = '收藏成功'
        favorited = True
    
    db.session.commit()
    
    return jsonify({
        'message': message,
        'favorited': favorited,
        'favorite_count': post.favorite_count
    })

@app.route('/api/users/<int:user_id>/follow', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    """关注用户"""
    user_to_follow = User.query.get_or_404(user_id)
    current_user_id = get_jwt_identity()
    
    if current_user_id == user_id:
        return jsonify({'message': '不能关注自己', 'error': 'self_follow'}), 400
    
    current_user = User.query.get(current_user_id)
    
    if current_user.is_following(user_to_follow):
        # 取消关注
        current_user.unfollow(user_to_follow)
        message = '已取消关注'
        following = False
    else:
        # 关注用户
        current_user.follow(user_to_follow)
        message = '关注成功'
        following = True
        
        # 创建通知
        create_notification(
            user_id=user_id,
            type='follow',
            title='新粉丝',
            message=f'{current_user.nickname or current_user.username} 关注了你',
            actor_id=current_user_id
        )
    
    db.session.commit()
    
    return jsonify({
        'message': message,
        'following': following,
        'followers_count': user_to_follow.followers_count
    })

# API路由 - 通知相关
@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """获取用户通知"""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    unread_only = request.args.get('unread_only', False, type=bool)
    
    query = Notification.query.filter_by(user_id=current_user_id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'notifications': [n.to_dict() for n in notifications.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': notifications.total,
            'pages': notifications.pages,
            'has_prev': notifications.has_prev,
            'has_next': notifications.has_next
        },
        'unread_count': Notification.query.filter_by(user_id=current_user_id, is_read=False).count()
    })

@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(notification_id):
    """标记通知为已读"""
    current_user_id = get_jwt_identity()
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user_id:
        return jsonify({'message': '无权限', 'error': 'access_denied'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'message': '已标记为已读'})

# API路由 - 数据统计
@app.route('/api/stats/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """获取仪表板统计数据"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # 基本统计
    stats = {
        'total_posts': Post.query.filter_by(author_id=current_user_id).count(),
        'total_views': db.session.query(db.func.sum(Post.view_count)).filter_by(author_id=current_user_id).scalar() or 0,
        'total_likes': db.session.query(db.func.sum(Post.like_count)).filter_by(author_id=current_user_id).scalar() or 0,
        'total_comments': Comment.query.join(Post).filter(Post.author_id == current_user_id).count(),
        'unread_notifications': Notification.query.filter_by(user_id=current_user_id, is_read=False).count(),
        'followers_count': user.followers_count,
        'following_count': user.following_count
    }
    
    # 最近7天的文章浏览量
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    view_stats = db.session.query(
        db.func.date(ViewLog.viewed_at).label('date'),
        db.func.count(ViewLog.id).label('views')
    ).join(Post).filter(
        Post.author_id == current_user_id,
        ViewLog.viewed_at >= start_date,
        ViewLog.viewed_at <= end_date
    ).group_by(db.func.date(ViewLog.viewed_at)).all()
    
    stats['view_trend'] = [{'date': str(item.date), 'views': item.views} for item in view_stats]
    
    return jsonify(stats)


@app.route('/api/rss', methods=['GET'])
def rss_feed():
    """输出最新文章的RSS订阅源"""
    base_url = request.url_root.rstrip('/')
    posts = Post.query.filter_by(status='published').order_by(
        Post.published_at.desc().nullslast(), Post.created_at.desc()
    ).limit(30).all()

    items_xml = []
    for post in posts:
        pub_date = (post.published_at or post.created_at).strftime('%a, %d %b %Y %H:%M:%S GMT')
        link = f"{base_url}/post/{post.id}"
        description = post.summary or generate_excerpt(post.content)
        body = post.content_html or render_markdown(post.content)
        items_xml.append(
            f"""
            <item>
                <title><![CDATA[{post.title}]]></title>
                <link>{link}</link>
                <guid isPermaLink="true">{link}</guid>
                <pubDate>{pub_date}</pubDate>
                <description><![CDATA[{description}]]></description>
                <content:encoded><![CDATA[{body}]]></content:encoded>
            </item>
            """
        )

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
      <channel>
        <title>Blog RSS</title>
        <link>{base_url}</link>
        <description>最新文章订阅</description>
        {''.join(items_xml)}
      </channel>
    </rss>"""

    return Response(rss_xml, mimetype='application/rss+xml')


@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    upload_folder = app.config.get('UPLOAD_FOLDER', os.path.join(app.instance_path, 'uploads'))
    return send_from_directory(upload_folder, filename)

# 初始化数据库命令
@app.cli.command('init-db')
def init_db():
    """初始化数据库"""
    db.create_all()
    
    # 创建默认管理员用户
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@blog.com',
            nickname='管理员',
            is_admin=True,
            is_verified=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print('Created admin user: admin / admin123')
    
    # 创建示例数据
    create_sample_data()
    
    print('Database initialized successfully!')

def create_sample_data():
    """创建示例数据"""
    # 创建示例用户
    user1 = User.query.filter_by(username='demo_user').first()
    if not user1:
        user1 = User(username='demo_user', email='demo@example.com', nickname='演示用户')
        user1.set_password('demo123')
        db.session.add(user1)
    
    # 创建示例标签
    sample_tags = ['技术', '生活', '旅行', '美食', '编程', '设计']
    for tag_name in sample_tags:
        if not Tag.query.filter_by(name=tag_name).first():
            tag = Tag(name=tag_name, slug=tag_name.lower())
            db.session.add(tag)
    
    # 创建示例分类
    sample_categories = ['前端开发', '后端开发', '移动开发', 'DevOps', '产品设计']
    for category_name in sample_categories:
        if not Category.query.filter_by(name=category_name).first():
            category = Category(name=category_name, slug=category_name.lower().replace(' ', '-'))
            db.session.add(category)
    
    db.session.commit()
    
    # 创建示例文章
    if not Post.query.filter_by(author_id=user1.id).first():
        sample_posts = [
            {
                'title': '欢迎来到我的博客',
                'content': '这是我的第一篇文章，欢迎访问我的博客系统！',
                'tags': ['技术', '生活'],
                'categories': ['前端开发']
            },
            {
                'title': 'Vue.js 3 新特性介绍',
                'content': 'Vue.js 3 带来了许多激动人心的新特性，包括Composition API、更好的TypeScript支持等...',
                'tags': ['编程', '技术'],
                'categories': ['前端开发']
            },
            {
                'title': 'Flask Web开发最佳实践',
                'content': 'Flask是一个轻量级的Python Web框架，本文介绍一些开发最佳实践...',
                'tags': ['编程', '技术'],
                'categories': ['后端开发']
            }
        ]
        
        for post_data in sample_posts:
            post = Post(
                title=post_data['title'],
                slug=post_data['title'].lower().replace(' ', '-'),
                content=post_data['content'],
                summary=post_data['content'][:100],
                author_id=user1.id,
                status='published',
                published_at=datetime.now(timezone.utc)
            )
            db.session.add(post)
            
            for tag_name in post_data['tags']:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag:
                    post.tags.append(tag)
            
            for category_name in post_data['categories']:
                category = Category.query.filter_by(name=category_name).first()
                if category:
                    post.categories.append(category)
        
        db.session.commit()

# 运行应用
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        with app.app_context():
            init_db()
        sys.exit(0)
    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        create_sample_data()
    socketio.run(app, host='0.0.0.0', port=app.config['PORT'], debug=True)
