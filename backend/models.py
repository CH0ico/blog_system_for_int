#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模型定义
包含用户、文章、评论、标签等核心数据模型
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(100), default='')
    avatar = db.Column(db.String(255), default='')
    bio = db.Column(db.Text, default='')
    website = db.Column(db.String(255), default='')
    location = db.Column(db.String(100), default='')
    
    # 社交统计
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    posts_count = db.Column(db.Integer, default=0)
    
    # 状态管理
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = db.Column(db.DateTime)
    
    # 关系定义
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # 关注关系
    following = db.relationship(
        'Follow', 
        foreign_keys='Follow.follower_id',
        backref='follower',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    followers = db.relationship(
        'Follow',
        foreign_keys='Follow.followed_id',
        backref='followed',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # 通知
    # notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship(
    'Notification',
    foreign_keys='Notification.user_id',
    backref='user',
    lazy='dynamic',
    cascade='all, delete-orphan'
    )

    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_following(self, user):
        """检查是否关注某用户"""
        return self.following.filter_by(followed_id=user.id).first() is not None
    
    def follow(self, user):
        """关注用户"""
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)
            self.following_count += 1
            user.followers_count += 1
    
    def unfollow(self, user):
        """取消关注"""
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            self.following_count -= 1
            user.followers_count -= 1
    
    def to_dict(self, include_email=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname or self.username,
            'avatar': self.avatar,
            'bio': self.bio,
            'website': self.website,
            'location': self.location,
            'followers_count': self.followers_count,
            'following_count': self.following_count,
            'posts_count': self.posts_count,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_email:
            data['email'] = self.email
        return data

class Post(db.Model):
    """文章模型"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    summary = db.Column(db.Text, default='')
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text, default='')
    
    # 文章状态
    status = db.Column(db.String(20), default='published')  # draft, published, archived
    is_featured = db.Column(db.Boolean, default=False)
    allow_comments = db.Column(db.Boolean, default=True)
    
    # 统计信息
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    favorite_count = db.Column(db.Integer, default=0)
    
    # 作者信息
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    published_at = db.Column(db.DateTime)
    
    # 关系定义
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    # 多对多关系
    tags = db.relationship('Tag', secondary='post_tags', backref='posts', lazy='dynamic')
    categories = db.relationship('Category', secondary='post_categories', backref='posts', lazy='dynamic')
    
    def increment_view_count(self):
        self.view_count += 1
        db.session.add(self)
        db.session.commit()
    
    def to_dict(self, include_content=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'summary': self.summary,
            'status': self.status,
            'is_featured': self.is_featured,
            'allow_comments': self.allow_comments,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'favorite_count': self.favorite_count,
            'author': self.author.to_dict(),
            'tags': [tag.to_dict() for tag in self.tags],
            'categories': [category.to_dict() for category in self.categories],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
        if include_content:
            data['content'] = self.content
            data['content_html'] = self.content_html
        return data

class Comment(db.Model):
    """评论模型"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text, default='')
    
    # 评论状态
    status = db.Column(db.String(20), default='approved')  # pending, approved, rejected, spam
    
    # 统计信息
    like_count = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)
    
    # 关联关系
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 自引用关系 - 回复
    replies = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # 点赞关系
    likes = db.relationship('Like', backref='comment', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_replies=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'content': self.content,
            'content_html': self.content_html,
            'status': self.status,
            'like_count': self.like_count,
            'reply_count': self.reply_count,
            'author': self.author.to_dict(),
            'post_id': self.post_id,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_replies and self.replies:
            data['replies'] = [reply.to_dict(include_replies=False) for reply in self.replies.limit(5)]
        return data

class Tag(db.Model):
    """标签模型"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default='')
    
    # 统计信息
    post_count = db.Column(db.Integer, default=0)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'post_count': self.post_count,
            'created_at': self.created_at.isoformat()
        }

class Category(db.Model):
    """分类模型"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default='')
    
    # 统计信息
    post_count = db.Column(db.Integer, default=0)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'post_count': self.post_count,
            'created_at': self.created_at.isoformat()
        }

# 多对多关联表
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc))
)

post_categories = db.Table('post_categories',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc))
)

class Like(db.Model):
    """点赞模型"""
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 确保一个用户对同一内容只能点赞一次
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),
        db.UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_like'),
        db.CheckConstraint(
            '(post_id IS NOT NULL AND comment_id IS NULL) OR (post_id IS NULL AND comment_id IS NOT NULL)',
            name='check_like_target'
        )
    )

class Favorite(db.Model):
    """收藏模型"""
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 确保一个用户对同一文章只能收藏一次
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_favorite'),
    )

class Follow(db.Model):
    """关注模型"""
    __tablename__ = 'follows'
    
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 确保不能重复关注
    __table_args__ = (
        db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),
        db.CheckConstraint('follower_id != followed_id', name='check_self_follow')
    )

class Notification(db.Model):
    """通知模型"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # like, comment, follow, etc.
    
    # 关联内容
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    
    # 通知内容
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, default='')
    data = db.Column(db.Text, default='')  # JSON格式的额外数据
    
    # 状态
    is_read = db.Column(db.Boolean, default=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关系
    actor = db.relationship('User', foreign_keys=[actor_id])
    post = db.relationship('Post')
    comment = db.relationship('Comment')
    
    def to_dict(self):
        """转换为字典"""
        data = {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }
        
        if self.actor:
            data['actor'] = self.actor.to_dict()
        if self.post:
            data['post'] = {'id': self.post.id, 'title': self.post.title}
        if self.comment:
            data['comment'] = {'id': self.comment.id, 'content': self.comment.content[:100]}
        if self.data:
            try:
                data['extra_data'] = json.loads(self.data)
            except:
                pass
        
        return data

class ViewLog(db.Model):
    """浏览记录模型"""
    __tablename__ = 'view_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 匿名用户可为空
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    
    # 客户端信息
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    referer = db.Column(db.String(500), nullable=True)
    
    # 时间戳
    viewed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关系
    user = db.relationship('User')
    post = db.relationship('Post')

# 创建索引以提高查询性能
db.Index('idx_posts_status_created_at', Post.status, Post.created_at)
db.Index('idx_posts_author_id', Post.author_id)
db.Index('idx_comments_post_id', Comment.post_id)
db.Index('idx_comments_author_id', Comment.author_id)
db.Index('idx_view_logs_post_id_viewed_at', ViewLog.post_id, ViewLog.viewed_at)
