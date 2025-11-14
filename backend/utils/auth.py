#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证相关工具函数
包含JWT token生成、验证、邮件确认等功能
"""

import os
import secrets
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from models import User

def generate_confirmation_token(email, secret_key=None):
    """
    生成邮箱确认令牌
    
    Args:
        email (str): 用户邮箱地址
        secret_key (str, optional): 密钥，默认使用Flask的SECRET_KEY
        
    Returns:
        str: 加密后的确认令牌
    """
    if not secret_key:
        secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt='email-confirm')

def confirm_token(token, expiration=3600, secret_key=None):
    """
    验证邮箱确认令牌
    
    Args:
        token (str): 确认令牌
        expiration (int): 令牌有效期（秒）
        secret_key (str, optional): 密钥
        
    Returns:
        str or None: 如果验证成功返回邮箱地址，否则返回None
    """
    if not secret_key:
        secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(
            token,
            salt='email-confirm',
            max_age=expiration
        )
        return email
    except (BadSignature, SignatureExpired):
        return None

def generate_password_reset_token(email, secret_key=None):
    """
    生成密码重置令牌
    
    Args:
        email (str): 用户邮箱地址
        secret_key (str, optional): 密钥
        
    Returns:
        str: 加密后的重置令牌
    """
    if not secret_key:
        secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt='password-reset')

def confirm_password_reset_token(token, expiration=1800, secret_key=None):
    """
    验证密码重置令牌
    
    Args:
        token (str): 重置令牌
        expiration (int): 令牌有效期（秒）
        secret_key (str, optional): 密钥
        
    Returns:
        str or None: 如果验证成功返回邮箱地址，否则返回None
    """
    if not secret_key:
        secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(
            token,
            salt='password-reset',
            max_age=expiration
        )
        return email
    except (BadSignature, SignatureExpired):
        return None

def generate_api_key():
    """
    生成API密钥
    
    Returns:
        str: 32位随机API密钥
    """
    return secrets.token_urlsafe(32)

def hash_api_key(api_key):
    """
    哈希API密钥（用于存储）
    
    Args:
        api_key (str): 原始API密钥
        
    Returns:
        str: 哈希后的API密钥
    """
    from werkzeug.security import generate_password_hash
    return generate_password_hash(api_key, method='pbkdf2:sha256', salt_length=16)

def verify_api_key(api_key, hashed_key):
    """
    验证API密钥
    
    Args:
        api_key (str): 原始API密钥
        hashed_key (str): 哈希后的API密钥
        
    Returns:
        bool: 验证结果
    """
    from werkzeug.security import check_password_hash
    return check_password_hash(hashed_key, api_key)

def get_user_by_email(email):
    """
    通过邮箱获取用户
    
    Args:
        email (str): 用户邮箱
        
    Returns:
        User or None: 用户对象或None
    """
    return User.query.filter_by(email=email).first()

def get_user_by_username(username):
    """
    通过用户名获取用户
    
    Args:
        username (str): 用户名
        
    Returns:
        User or None: 用户对象或None
    """
    return User.query.filter_by(username=username).first()

def is_email_verified(user):
    """
    检查用户邮箱是否已验证
    
    Args:
        user (User): 用户对象
        
    Returns:
        bool: 验证状态
    """
    return user.is_verified if user else False

def can_user_post(user):
    """
    检查用户是否有权限发布文章
    
    Args:
        user (User): 用户对象
        
    Returns:
        bool: 权限状态
    """
    if not user:
        return False
    
    # 管理员总是有权限
    if user.is_admin:
        return True
    
    # 用户必须激活且已验证邮箱
    return user.is_active and user.is_verified

def get_user_permissions(user):
    """
    获取用户权限列表
    
    Args:
        user (User): 用户对象
        
    Returns:
        list: 权限列表
    """
    if not user:
        return []
    
    permissions = []
    
    # 基础权限
    if user.is_active:
        permissions.extend([
            'read_posts',
            'comment_posts',
            'like_posts',
            'favorite_posts',
            'follow_users'
        ])
    
    # 作者权限
    if user.is_active and user.is_verified:
        permissions.extend([
            'create_posts',
            'edit_own_posts',
            'delete_own_posts'
        ])
    
    # 管理员权限
    if user.is_admin:
        permissions.extend([
            'admin_access',
            'manage_users',
            'manage_posts',
            'manage_comments',
            'manage_settings'
        ])
    
    return permissions

def has_permission(user, permission):
    """
    检查用户是否有特定权限
    
    Args:
        user (User): 用户对象
        permission (str): 权限名称
        
    Returns:
        bool: 权限检查结果
    """
    if not user or not permission:
        return False
    
    permissions = get_user_permissions(user)
    return permission in permissions