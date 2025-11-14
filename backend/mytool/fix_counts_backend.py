#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复博客系统数据脚本 - 直接在backend目录运行
修复标签和分类的计数问题
"""

import os
import sys

# 添加到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models import Tag, Category, Post

def fix_tag_counts():
    """修复标签的post_count计数"""
    try:
        tags = Tag.query.all()
        fixed_count = 0
        
        for tag in tags:
            # 计算关联的已发布文章数量
            published_posts = Post.query.join(Post.tags).filter(
                Tag.id == tag.id,
                Post.status == 'published'
            ).count()
            
            # 如果计数不匹配，则更新
            if tag.post_count != published_posts:
                print(f"修复标签 '{tag.name}': {tag.post_count} -> {published_posts}")
                tag.post_count = published_posts
                fixed_count += 1
        
        db.session.commit()
        return fixed_count
        
    except Exception as e:
        db.session.rollback()
        print(f"修复标签计数时出错: {e}")
        return 0

def fix_category_counts():
    """修复分类的post_count计数"""
    try:
        categories = Category.query.all()
        fixed_count = 0
        
        for category in categories:
            # 计算关联的已发布文章数量
            published_posts = Post.query.join(Post.categories).filter(
                Category.id == category.id,
                Post.status == 'published'
            ).count()
            
            # 如果计数不匹配，则更新
            if category.post_count != published_posts:
                print(f"修复分类 '{category.name}': {category.post_count} -> {published_posts}")
                category.post_count = published_posts
                fixed_count += 1
        
        db.session.commit()
        return fixed_count
        
    except Exception as e:
        db.session.rollback()
        print(f"修复分类计数时出错: {e}")
        return 0

def verify_view_counts():
    """验证阅读量数据"""
    try:
        posts = Post.query.filter_by(status='published').all()
        
        print("\n=== 已发布文章的阅读量统计 ===")
        for post in posts:
            print(f"文章: {post.title}")
            print(f"  阅读量: {post.view_count}")
            
        total_views = sum(post.view_count for post in posts)
        print(f"\n总阅读量: {total_views}")
        
    except Exception as e:
        print(f"验证阅读量时出错: {e}")

def main():
    """主函数：执行所有修复操作"""
    
    with app.app_context():
        print("=== 开始修复博客系统数据 ===")
        
        # 修复标签计数
        fixed_tags = fix_tag_counts()
        print(f"修复了 {fixed_tags} 个标签的计数")
        
        # 修复分类计数
        fixed_categories = fix_category_counts()
        print(f"修复了 {fixed_categories} 个分类的计数")
        
        # 验证阅读量
        verify_view_counts()
        
        print("=== 修复完成 ===")

if __name__ == "__main__":
    main()