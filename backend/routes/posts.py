#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章相关路由
处理文章的CRUD操作、搜索、过滤等功能
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

from models import db, Post, Tag, Category, User, Like, Favorite, Comment
from utils.validators import (
    validate_post_title, validate_post_content, 
    validate_tag_name, validate_category_name,
    generate_excerpt, clean_search_query
)
from utils.auth import has_permission

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/', methods=['GET'])
def get_posts():
    """获取文章列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = clean_search_query(request.args.get('search', ''))
    tag = request.args.get('tag', '').strip()
    category = request.args.get('category', '').strip()
    author = request.args.get('author', '').strip()
    status = request.args.get('status', 'published')
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    
    # 检查是否有权限查看草稿
    current_user_id = get_jwt_identity() if request.headers.get('Authorization') else None
    show_drafts = False
    
    if status == 'draft' and current_user_id:
        user = User.query.get(current_user_id)
        if user and (has_permission(user, 'create_posts') or user.is_admin):
            show_drafts = True
    
    # 基础查询
    if show_drafts:
        query = Post.query.filter_by(author_id=current_user_id)
    else:
        query = Post.query.filter_by(status='published')
    
    # 搜索过滤
    if search:
        query = query.filter(
            or_(
                Post.title.contains(search),
                Post.content.contains(search),
                Post.summary.contains(search)
            )
        )
    
    # 标签过滤
    if tag:
        query = query.join(Post.tags).filter(Tag.slug == tag.lower())
    
    # 分类过滤
    if category:
        query = query.join(Post.categories).filter(Category.slug == category.lower())
    
    # 作者过滤
    if author:
        query = query.join(User).filter(User.username == author)
    
    # 排序
    if sort_by == 'view_count':
        sort_field = Post.view_count
    elif sort_by == 'like_count':
        sort_field = Post.like_count
    elif sort_by == 'comment_count':
        sort_field = Post.comment_count
    elif sort_by == 'published_at':
        sort_field = Post.published_at
    else:
        sort_field = Post.created_at
    
    if order == 'asc':
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items
    
    # 检查当前用户的点赞和收藏状态
    user_likes = set()
    user_favorites = set()
    
    if current_user_id:
        user_likes = {like.post_id for like in Like.query.filter_by(user_id=current_user_id).all()}
        user_favorites = {fav.post_id for fav in Favorite.query.filter_by(user_id=current_user_id).all()}
    
    posts_data = []
    for post in posts:
        post_dict = post.to_dict(include_content=False)
        post_dict['liked'] = post.id in user_likes
        post_dict['favorited'] = post.id in user_favorites
        posts_data.append(post_dict)
    
    return jsonify({
        'posts': posts_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    })

@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """获取单篇文章详情"""
    post = Post.query.get_or_404(post_id)
    
    # 检查权限
    if post.status != 'published':
        current_user_id = get_jwt_identity() if request.headers.get('Authorization') else None
        if not current_user_id or (post.author_id != current_user_id and not post.author.is_admin):
            return jsonify({
                'message': '文章不存在或无权限查看',
                'error': 'access_denied'
            }), 404
    
    # 增加浏览次数
    post.increment_view_count()
    
    # 记录浏览日志（简化版本，不记录详细日志）
    current_user_id = get_jwt_identity() if request.headers.get('Authorization') else None
    
    # 检查当前用户的点赞和收藏状态
    liked = False
    favorited = False
    
    if current_user_id:
        liked = Like.query.filter_by(user_id=current_user_id, post_id=post_id).first() is not None
        favorited = Favorite.query.filter_by(user_id=current_user_id, post_id=post_id).first() is not None
    
    post_dict = post.to_dict()
    post_dict['liked'] = liked
    post_dict['favorited'] = favorited
    
    return jsonify({
        'post': post_dict
    })

@posts_bp.route('/', methods=['POST'])
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
    is_featured = data.get('is_featured', False)
    allow_comments = data.get('allow_comments', True)
    
    # 验证必填字段
    if not title or not content:
        return jsonify({
            'message': '标题和内容不能为空',
            'error': 'missing_fields',
            'details': {
                'title': not title,
                'content': not content
            }
        }), 400
    
    # 验证字段格式
    if not validate_post_title(title):
        return jsonify({
            'message': '标题长度不能超过200个字符',
            'error': 'invalid_title'
        }), 400
    
    if not validate_post_content(content):
        return jsonify({
            'message': '内容长度不能少于10个字符',
            'error': 'invalid_content'
        }), 400
    
    # 验证状态
    if status not in ['draft', 'published', 'archived']:
        return jsonify({
            'message': '文章状态无效',
            'error': 'invalid_status'
        }), 400
    
    # 生成slug
    slug = data.get('slug', title.lower().replace(' ', '-'))
    if not validate_slug(slug):
        slug = title.lower().replace(' ', '-')
    
    # 检查slug是否已存在
    if Post.query.filter_by(slug=slug).first():
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
    
    current_user_id = get_jwt_identity()
    
    # 创建文章
    post = Post(
        title=title,
        slug=slug,
        content=content,
        summary=summary or generate_excerpt(content),
        status=status,
        is_featured=is_featured,
        allow_comments=allow_comments,
        author_id=current_user_id
    )
    
    if status == 'published':
        post.published_at = datetime.utcnow()
    
    # 处理标签
    if tags:
        for tag_name in tags:
            if not validate_tag_name(tag_name):
                continue
            
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(
                    name=tag_name,
                    slug=tag_name.lower().replace(' ', '-')
                )
                db.session.add(tag)
            post.tags.append(tag)
    
    # 处理分类
    if categories:
        for category_name in categories:
            if not validate_category_name(category_name):
                continue
            
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(
                    name=category_name,
                    slug=category_name.lower().replace(' ', '-')
                )
                db.session.add(category)
            post.categories.append(category)
    
    db.session.add(post)
    
    # 更新用户的文章计数
    user = User.query.get(current_user_id)
    user.posts_count += 1
    
    db.session.commit()
    
    # 通知关注者（如果是发布文章）
    if status == 'published':
        followers = user.followers.all()
        for follower in followers:
            from app import create_notification
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

@posts_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """更新文章"""
    post = Post.query.get_or_404(post_id)
    current_user_id = get_jwt_identity()
    
    # 检查权限
    if post.author_id != current_user_id:
        return jsonify({
            'message': '无权限编辑此文章',
            'error': 'access_denied'
        }), 403
    
    data = request.get_json()
    
    # 更新字段
    if 'title' in data:
        title = data['title'].strip()
        if not validate_post_title(title):
            return jsonify({
                'message': '标题长度不能超过200个字符',
                'error': 'invalid_title'
            }), 400
        post.title = title
    
    if 'content' in data:
        content = data['content'].strip()
        if not validate_post_content(content):
            return jsonify({
                'message': '内容长度不能少于10个字符',
                'error': 'invalid_content'
            }), 400
        post.content = content
        post.summary = generate_excerpt(content)
    
    if 'summary' in data:
        post.summary = data['summary'].strip()
    
    if 'status' in data:
        new_status = data['status']
        if new_status not in ['draft', 'published', 'archived']:
            return jsonify({
                'message': '文章状态无效',
                'error': 'invalid_status'
            }), 400
        
        post.status = new_status
        if new_status == 'published' and not post.published_at:
            post.published_at = datetime.utcnow()
    
    if 'is_featured' in data:
        post.is_featured = bool(data['is_featured'])
    
    if 'allow_comments' in data:
        post.allow_comments = bool(data['allow_comments'])
    
    # 处理标签
    if 'tags' in data:
        tags = data['tags']
        post.tags.clear()
        
        for tag_name in tags:
            if not validate_tag_name(tag_name):
                continue
            
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(
                    name=tag_name,
                    slug=tag_name.lower().replace(' ', '-')
                )
                db.session.add(tag)
            post.tags.append(tag)
    
    # 处理分类
    if 'categories' in data:
        categories = data['categories']
        post.categories.clear()
        
        for category_name in categories:
            if not validate_category_name(category_name):
                continue
            
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(
                    name=category_name,
                    slug=category_name.lower().replace(' ', '-')
                )
                db.session.add(category)
            post.categories.append(category)
    
    post.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': '文章更新成功',
        'post': post.to_dict()
    })

@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """删除文章"""
    post = Post.query.get_or_404(post_id)
    current_user_id = get_jwt_identity()
    
    # 检查权限
    if post.author_id != current_user_id:
        return jsonify({
            'message': '无权限删除此文章',
            'error': 'access_denied'
        }), 403
    
    db.session.delete(post)
    
    # 更新用户的文章计数
    user = User.query.get(current_user_id)
    user.posts_count -= 1
    
    db.session.commit()
    
    return jsonify({'message': '文章删除成功'})

@posts_bp.route('/<int:post_id>/like', methods=['POST'])
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
            from app import create_notification
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

@posts_bp.route('/<int:post_id>/favorite', methods=['POST'])
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

@posts_bp.route('/tags', methods=['GET'])
def get_tags():
    """获取所有标签"""
    tags = Tag.query.all()
    return jsonify({
        'tags': [tag.to_dict() for tag in tags]
    })

@posts_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    categories = Category.query.all()
    return jsonify({
        'categories': [category.to_dict() for category in categories]
    })

@posts_bp.route('/popular', methods=['GET'])
def get_popular_posts():
    """获取热门文章"""
    limit = request.args.get('limit', 10, type=int)
    period = request.args.get('period', 'week')  # week, month, all
    
    try:
        query = Post.query.filter_by(status='published')
        
        # 根据时间段过滤
        if period == 'week':
            week_ago = datetime.utcnow() - timedelta(days=7)
            query = query.filter(Post.published_at >= week_ago)
        elif period == 'month':
            month_ago = datetime.utcnow() - timedelta(days=30)
            query = query.filter(Post.published_at >= month_ago)
        
        # 按浏览量排序
        posts = query.order_by(Post.view_count.desc()).limit(limit).all()
        
        # 如果没有热门文章，返回最新的已发布文章作为备选
        if not posts:
            posts = Post.query.filter_by(
                status='published'
            ).order_by(Post.published_at.desc()).limit(limit).all()
        
        return jsonify({
            'posts': [post.to_dict(include_content=False) for post in posts]
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching popular posts: {str(e)}")
        return jsonify({
            'posts': [],
            'message': '获取热门文章失败',
            'error': str(e)
        }), 500

@posts_bp.route('/featured', methods=['GET'])
def get_featured_posts():
    """获取推荐文章"""
    limit = request.args.get('limit', 10, type=int)
    
    try:
        posts = Post.query.filter_by(
            status='published',
            is_featured=True
        ).order_by(Post.published_at.desc()).limit(limit).all()
        
        # 如果没有推荐文章，返回最新的已发布文章作为备选
        if not posts:
            posts = Post.query.filter_by(
                status='published'
            ).order_by(Post.published_at.desc()).limit(limit).all()
        
        return jsonify({
            'posts': [post.to_dict(include_content=False) for post in posts]
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching featured posts: {str(e)}")
        return jsonify({
            'posts': [],
            'message': '获取推荐文章失败',
            'error': str(e)
        }), 500

@posts_bp.route('/archives', methods=['GET'])
def get_archives():
    """获取文章归档"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 获取已发布的文章，按发布时间倒序排列
        posts = Post.query.filter_by(status='published').order_by(Post.published_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 格式化文章数据以匹配前端期望的格式
        posts_data = []
        for post in posts.items:
            # 获取作者信息
            author = post.author.username if post.author else '未知作者'
            
            # 创建文章摘要（前200字符）
            excerpt = post.content[:200] + '...' if len(post.content) > 200 else post.content
            
            posts_data.append({
                'id': post.id,
                'title': post.title,
                'excerpt': excerpt,
                'author': author,
                'view_count': post.view_count,
                'date': post.published_at.isoformat()
            })
        
        return jsonify({
            'posts': posts_data,
            'total': posts.total,
            'page': page,
            'per_page': per_page,
            'has_next': posts.has_next
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching archives: {str(e)}")
        return jsonify({
            'posts': [],
            'total': 0,
            'page': 1,
            'per_page': 10,
            'has_next': False,
            'message': '获取归档文章失败',
            'error': str(e)
        }), 500

@posts_bp.route('/search/suggestions', methods=['GET'])
def get_search_suggestions():
    """获取搜索建议"""
    query = clean_search_query(request.args.get('q', ''))
    limit = request.args.get('limit', 5, type=int)
    
    if not query:
        return jsonify({'suggestions': []})
    
    # 搜索文章标题
    posts = Post.query.filter(
        Post.title.contains(query),
        Post.status == 'published'
    ).limit(limit).all()
    
    # 搜索标签
    tags = Tag.query.filter(Tag.name.contains(query)).limit(limit).all()
    
    suggestions = []
    
    # 添加文章建议
    for post in posts:
        suggestions.append({
            'type': 'post',
            'text': post.title,
            'slug': post.slug,
            'id': post.id
        })
    
    # 添加标签建议
    for tag in tags:
        suggestions.append({
            'type': 'tag',
            'text': tag.name,
            'slug': tag.slug,
            'id': tag.id
        })
    
    return jsonify({'suggestions': suggestions})