#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证工具函数
包含各种输入验证和格式化功能
"""

import re
import os
from urllib.parse import urlparse

def validate_username(username):
    """
    验证用户名格式
    
    Args:
        username (str): 用户名
        
    Returns:
        bool: 验证结果
    """
    if not username:
        return False
    
    # 用户名长度：3-20个字符
    if len(username) < 3 or len(username) > 20:
        return False
    
    # 用户名只能包含字母、数字、下划线
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    
    # 不能以数字开头
    if username[0].isdigit():
        return False
    
    return True

def validate_email(email):
    """
    验证邮箱格式
    
    Args:
        email (str): 邮箱地址
        
    Returns:
        bool: 验证结果
    """
    if not email:
        return False
    
    # 邮箱正则表达式
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """
    验证密码强度
    
    Args:
        password (str): 密码
        
    Returns:
        bool: 验证结果
    """
    if not password:
        return False
    
    # 密码长度：至少8个字符
    if len(password) < 8:
        return False
    
    # 至少包含一个大写字母
    if not re.search(r'[A-Z]', password):
        return False
    
    # 至少包含一个小写字母
    if not re.search(r'[a-z]', password):
        return False
    
    # 至少包含一个数字
    if not re.search(r'\d', password):
        return False
    
    # 至少包含一个特殊字符
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

def validate_url(url):
    """
    验证URL格式
    
    Args:
        url (str): URL地址
        
    Returns:
        bool: 验证结果
    """
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def validate_slug(slug):
    """
    验证slug格式
    
    Args:
        slug (str): URL slug
        
    Returns:
        bool: 验证结果
    """
    if not slug:
        return False
    
    # slug只能包含小写字母、数字、连字符
    if not re.match(r'^[a-z0-9-]+$', slug):
        return False
    
    # 不能以连字符开头或结尾
    if slug.startswith('-') or slug.endswith('-'):
        return False
    
    # 不能包含连续连字符
    if '--' in slug:
        return False
    
    return True

def sanitize_html(html):
    """
    清理HTML内容，移除危险标签和属性
    
    Args:
        html (str): HTML内容
        
    Returns:
        str: 清理后的HTML内容
    """
    if not html:
        return ''
    
    # 移除script标签
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
    
    # 移除on事件属性
    html = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # 移除javascript:协议链接
    html = re.sub(r'href\s*=\s*["\']javascript:[^"\']*["\']', 'href="#"', html, flags=re.IGNORECASE)
    
    return html

def sanitize_filename(filename):
    """
    清理文件名，移除危险字符
    
    Args:
        filename (str): 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    if not filename:
        return ''
    
    # 移除路径分隔符和特殊字符
    filename = re.sub(r'[\\/:*?"<>|]', '', filename)
    
    # 限制长度
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:100-len(ext)] + ext
    
    return filename

def validate_image_file(file):
    """
    验证图片文件
    
    Args:
        file: 文件对象
        
    Returns:
        bool: 验证结果
    """
    if not file:
        return False
    
    # 检查文件扩展名
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'}
    filename = file.filename.lower()
    
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1]
    if ext not in allowed_extensions:
        return False
    
    # 检查文件大小（最大5MB）
    file.seek(0, 2)  # 移动到文件末尾
    file_size = file.tell()
    file.seek(0)  # 移动回文件开头
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        return False
    
    return True

def format_datetime(dt):
    """
    格式化日期时间
    
    Args:
        dt (datetime): 日期时间对象
        
    Returns:
        str: 格式化后的字符串
    """
    if not dt:
        return ''
    
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def format_date(dt):
    """
    格式化日期
    
    Args:
        dt (date): 日期对象
        
    Returns:
        str: 格式化后的字符串
    """
    if not dt:
        return ''
    
    return dt.strftime('%Y-%m-%d')

def truncate_text(text, max_length=100, suffix='...'):
    """
    截断文本
    
    Args:
        text (str): 原始文本
        max_length (int): 最大长度
        suffix (str): 后缀字符串
        
    Returns:
        str: 截断后的文本
    """
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def generate_excerpt(content, max_length=200):
    """
    从文章内容生成摘要
    
    Args:
        content (str): 文章内容
        max_length (int): 最大长度
        
    Returns:
        str: 文章摘要
    """
    if not content:
        return ''
    
    # 移除HTML标签
    import re
    text = re.sub(r'<[^>]+>', '', content)
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text).strip()
    
    return truncate_text(text, max_length)

def validate_tag_name(name):
    """
    验证标签名称
    
    Args:
        name (str): 标签名称
        
    Returns:
        bool: 验证结果
    """
    if not name:
        return False
    
    # 标签长度：1-20个字符
    if len(name) < 1 or len(name) > 20:
        return False
    
    # 标签只能包含字母、数字、中文、连字符
    if not re.match(r'^[a-zA-Z0-9\u4e00-\u9fa5-]+$', name):
        return False
    
    return True

def validate_category_name(name):
    """
    验证分类名称
    
    Args:
        name (str): 分类名称
        
    Returns:
        bool: 验证结果
    """
    if not name:
        return False
    
    # 分类长度：1-30个字符
    if len(name) < 1 or len(name) > 30:
        return False
    
    # 分类只能包含字母、数字、中文、空格
    if not re.match(r'^[a-zA-Z0-9\u4e00-\u9fa5\s]+$', name):
        return False
    
    return True

def validate_comment_content(content):
    """
    验证评论内容
    
    Args:
        content (str): 评论内容
        
    Returns:
        bool: 验证结果
    """
    if not content:
        return False
    
    # 评论长度：1-1000个字符
    if len(content) < 1 or len(content) > 1000:
        return False
    
    return True

def validate_post_title(title):
    """
    验证文章标题
    
    Args:
        title (str): 文章标题
        
    Returns:
        bool: 验证结果
    """
    if not title:
        return False
    
    # 标题长度：1-200个字符
    if len(title) < 1 or len(title) > 200:
        return False
    
    return True

def validate_post_content(content):
    """
    验证文章内容
    
    Args:
        content (str): 文章内容
        
    Returns:
        bool: 验证结果
    """
    if not content:
        return False
    
    # 内容长度：至少10个字符
    if len(content) < 10:
        return False
    
    return True

def clean_search_query(query):
    """
    清理搜索查询
    
    Args:
        query (str): 搜索查询
        
    Returns:
        str: 清理后的查询
    """
    if not query:
        return ''
    
    # 移除特殊字符，保留字母、数字、中文、空格
    query = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5\s]', '', query)
    
    # 移除多余空格
    query = re.sub(r'\s+', ' ', query).strip()
    
    return query

def is_safe_url(target):
    """
    检查URL是否安全（防止开放重定向）
    
    Args:
        target (str): 目标URL
        
    Returns:
        bool: 安全检查结果
    """
    if not target:
        return False
    
    # 只允许相对路径或同域名URL
    if target.startswith('/'):
        return True
    
    # 检查是否是绝对URL
    if target.startswith('http://') or target.startswith('https://'):
        # 这里可以添加域名白名单检查
        return True
    
    return False