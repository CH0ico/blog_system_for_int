#!/usr/bin/env python3
"""
检查choco1用户是否存在
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import User
from app import app

def check_user():
    with app.app_context():
        user = User.query.filter_by(username='choco1').first()
        if user:
            print(f"✅ 用户choco1存在:")
            print(f"   ID: {user.id}")
            print(f"   用户名: {user.username}")
            print(f"   邮箱: {user.email}")
            print(f"   激活状态: {user.is_active}")
            print(f"   创建时间: {user.created_at}")
        else:
            print("❌ 用户choco1不存在")
        
        # 列出所有用户
        print("\n📋 所有用户:")
        users = User.query.all()
        for u in users:
            print(f"   {u.id}: {u.username} ({u.email}) - 激活: {u.is_active}")

if __name__ == "__main__":
    check_user()