#!/usr/bin/env python3
"""
数据库数据检查脚本
用于检查博客系统中的数据状态
"""

import os
import sys
from datetime import datetime

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app import app, db
from models import User, Post, Category, Tag, Comment

def check_database():
    """检查数据库中的数据状态"""
    print("=== 数据库数据检查 ===")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    with app.app_context():
        try:
            # 检查用户数据
            users = User.query.all()
            print(f"用户总数: {len(users)}")
            if users:
                print("用户列表:")
                for user in users[:5]:  # 只显示前5个用户
                    print(f"  - ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}")
                if len(users) > 5:
                    print(f"  ... 还有 {len(users) - 5} 个用户")
            print()
            
            # 检查分类数据
            categories = Category.query.all()
            print(f"分类总数: {len(categories)}")
            if categories:
                print("分类列表:")
                for category in categories:
                    print(f"  - ID: {category.id}, 名称: {category.name}, 文章数: {len(category.posts)}")
            print()
            
            # 检查标签数据
            tags = Tag.query.all()
            print(f"标签总数: {len(tags)}")
            if tags:
                print("标签列表:")
                for tag in tags[:10]:  # 只显示前10个标签
                    print(f"  - ID: {tag.id}, 名称: {tag.name}, 文章数: {len(tag.posts)}")
                if len(tags) > 10:
                    print(f"  ... 还有 {len(tags) - 10} 个标签")
            print()
            
            # 检查文章数据
            posts = Post.query.all()
            published_posts = Post.query.filter_by(status='published').all()
            print(f"文章总数: {len(posts)}")
            print(f"已发布文章: {len(published_posts)}")
            
            if published_posts:
                print("最新发布的5篇文章:")
                for post in published_posts[:5]:
                    print(f"  - ID: {post.id}, 标题: {post.title}")
                    print(f"    状态: {post.status}, 发布时间: {post.published_at}")
                    print(f"    作者: {post.author.username if post.author else '无作者'}")
                    # 修复分类显示 - 使用多对多关系
                    categories = [cat.name for cat in post.categories]
                    print(f"    分类: {', '.join(categories) if categories else '无分类'}")
                    print(f"    标签: {', '.join([tag.name for tag in post.tags])}")
                    print(f"    浏览量: {post.view_count}, 点赞: {post.like_count}, 收藏: {post.favorite_count}")
                    print()
            
            # 检查推荐文章
            featured_posts = Post.query.filter_by(status='published', is_featured=True).all()
            print(f"推荐文章数: {len(featured_posts)}")
            if featured_posts:
                print("推荐文章列表:")
                for post in featured_posts:
                    print(f"  - {post.title} (ID: {post.id})")
            print()
            
            # 检查热门文章（按浏览量排序）
            popular_posts = Post.query.filter_by(status='published').order_by(Post.view_count.desc()).limit(5).all()
            print(f"热门文章TOP5:")
            for post in popular_posts:
                print(f"  - {post.title} (浏览量: {post.view_count})")
            print()
            
            # 检查评论数据
            comments = Comment.query.all()
            print(f"评论总数: {len(comments)}")
            
        except Exception as e:
            print(f"数据库查询错误: {str(e)}")
            return False
    
    print("=" * 50)
    return True

def create_sample_data():
    """创建示例数据"""
    print("\n=== 创建示例数据 ===")
    
    with app.app_context():
        try:
            # 检查是否已有数据
            if User.query.first():
                print("数据库中已有数据，跳过示例数据创建")
                return
            
            print("创建示例用户...")
            # 创建管理员用户
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash='pbkdf2:sha256:260000$kH6VJiCmRzQoWdO$8c7ac9e2e46e9a8b94f6d8a7c5f3e0d1c2b3a4f5e6d7c8b9a0f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6b7a8f9e0d1c2b3a4f5e6d7c8b9a0f1e2d3',
                is_admin=True,
                is_verified=True
            )
            
            # 创建普通用户
            user1 = User(username='张三', email='zhangsan@example.com', is_verified=True)
            user2 = User(username='李四', email='lisi@example.com', is_verified=True)
            user3 = User(username='王五', email='wangwu@example.com', is_verified=True)
            
            db.session.add_all([admin, user1, user2, user3])
            db.session.commit()
            print("用户创建完成")
            
            print("创建示例分类...")
            # 创建分类
            categories = [
                Category(name='技术', slug='tech', description='技术相关文章'),
                Category(name='生活', slug='life', description='生活感悟'),
                Category(name='学习', slug='learning', description='学习笔记'),
                Category(name='工作', slug='work', description='工作经验'),
            ]
            db.session.add_all(categories)
            db.session.commit()
            print("分类创建完成")
            
            print("创建示例标签...")
            # 创建标签
            tags = [
                Tag(name='Python', slug='python'),
                Tag(name='JavaScript', slug='javascript'),
                Tag(name='Vue.js', slug='vue-js'),
                Tag(name='Flask', slug='flask'),
                Tag(name='Web开发', slug='web-development'),
                Tag(name='数据库', slug='database'),
                Tag(name='前端', slug='frontend'),
                Tag(name='后端', slug='backend'),
                Tag(name='AI', slug='ai'),
                Tag(name='机器学习', slug='machine-learning'),
            ]
            db.session.add_all(tags)
            db.session.commit()
            print("标签创建完成")
            
            print("创建示例文章...")
            # 创建文章
            sample_posts = [
                {
                    'title': 'Python Flask Web开发入门指南',
                    'content': 'Flask是一个轻量级的Python Web框架，非常适合快速开发Web应用。本文将介绍Flask的基础知识和使用方法。',
                    'excerpt': 'Flask是一个轻量级的Python Web框架...',
                    'category': '技术',
                    'tags': ['Python', 'Flask', 'Web开发'],
                    'author': admin,
                    'is_featured': True,
                    'view_count': 150
                },
                {
                    'title': 'Vue.js 3.0 新特性详解',
                    'content': 'Vue.js 3.0带来了许多激动人心的新特性，包括Composition API、更好的TypeScript支持等。',
                    'excerpt': 'Vue.js 3.0带来了许多激动人心的新特性...',
                    'category': '技术',
                    'tags': ['Vue.js', 'JavaScript', '前端'],
                    'author': user1,
                    'is_featured': True,
                    'view_count': 200
                },
                {
                    'title': '我的2024年学习计划',
                    'content': '新的一年，我制定了一些学习计划，包括深入学习Python、学习前端框架等。',
                    'excerpt': '新的一年，我制定了一些学习计划...',
                    'category': '学习',
                    'tags': ['学习', 'Python'],
                    'author': user2,
                    'view_count': 80
                },
                {
                    'title': '远程工作一年的感悟',
                    'content': '远程工作已经一年了，分享一些我的感悟和经验。',
                    'excerpt': '远程工作已经一年了...',
                    'category': '工作',
                    'tags': ['工作'],
                    'author': user3,
                    'view_count': 120
                },
                {
                    'title': 'JavaScript异步编程详解',
                    'content': '异步编程是JavaScript中的重要概念，本文将详细介绍Promise、async/await等概念。',
                    'excerpt': '异步编程是JavaScript中的重要概念...',
                    'category': '技术',
                    'tags': ['JavaScript', '前端'],
                    'author': admin,
                    'view_count': 180
                },
            ]
            
            for post_data in sample_posts:
                # 获取分类
                category = Category.query.filter_by(name=post_data['category']).first()
                
                # 创建文章
                post = Post(
                    title=post_data['title'],
                    content=post_data['content'],
                    summary=post_data['excerpt'],
                    slug=post_data['title'].lower().replace(' ', '-'),
                    author=post_data['author'],
                    status='published',
                    is_featured=post_data.get('is_featured', False),
                    view_count=post_data.get('view_count', 0),
                    published_at=datetime.utcnow()
                )
                
                # 添加分类（多对多关系）
                if category:
                    post.categories.append(category)
                
                # 添加标签
                for tag_name in post_data['tags']:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if tag:
                        post.tags.append(tag)
                
                db.session.add(post)
            
            db.session.commit()
            print("文章创建完成")
            
            print("\n示例数据创建成功！")
            
        except Exception as e:
            print(f"创建示例数据失败: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    # 首先检查数据库
    check_database()
    
    # 如果没有数据，创建示例数据
    with app.app_context():
        if not User.query.first():
            create_sample_data()
            # 再次检查数据
            check_database()
        else:
            print("\n数据库中已有数据，无需创建示例数据")