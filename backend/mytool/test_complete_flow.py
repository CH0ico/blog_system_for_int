#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的注册-登录-登出流程
"""

import requests
import json
import sqlite3
from datetime import datetime

class BlogAuthTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        
    def test_registration(self, username, email, password, nickname):
        """测试用户注册"""
        print(f"🔄 正在注册用户: {username}")
        
        url = f"{self.base_url}/api/auth/register"
        data = {
            "username": username,
            "email": email,
            "password": password,
            "nickname": nickname
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            if response.status_code == 201:
                print("✅ 注册成功")
                return True
            else:
                print(f"❌ 注册失败: {result}")
                return False
                
        except Exception as e:
            print(f"❌ 注册异常: {e}")
            return False
    
    def test_login(self, username, password):
        """测试用户登录"""
        print(f"🔄 正在登录用户: {username}")
        
        url = f"{self.base_url}/api/auth/login"
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            if response.status_code == 200:
                self.access_token = result.get('access_token')
                self.refresh_token = result.get('refresh_token')
                print("✅ 登录成功")
                print(f"   访问令牌: {self.access_token[:50]}...")
                print(f"   用户ID: {result.get('user', {}).get('id')}")
                return True
            else:
                print(f"❌ 登录失败: {result}")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def test_logout(self):
        """测试用户登出"""
        print("🔄 正在测试登出")
        
        if not self.access_token:
            print("❌ 未登录，无法测试登出")
            return False
            
        url = f"{self.base_url}/api/auth/logout"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = self.session.post(url, headers=headers)
            if response.status_code == 200:
                print("✅ 登出成功")
                self.access_token = None
                self.refresh_token = None
                return True
            else:
                print(f"❌ 登出失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 登出异常: {e}")
            return False
    
    def check_user_in_db(self, username):
        """检查用户是否存在于数据库"""
        try:
            conn = sqlite3.connect('instance/blog.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, is_active, created_at 
                FROM users 
                WHERE username = ?
            """, (username,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                print(f"✅ 用户存在于数据库:")
                print(f"   ID: {user[0]}")
                print(f"   用户名: {user[1]}")
                print(f"   邮箱: {user[2]}")
                print(f"   激活状态: {'激活' if user[3] else '未激活'}")
                print(f"   创建时间: {user[4]}")
                return True
            else:
                print("❌ 用户不存在于数据库")
                return False
                
        except Exception as e:
            print(f"❌ 检查数据库时出错: {e}")
            return False

def main():
    """运行完整流程测试"""
    print("🚀 开始测试完整的注册-登录-登出流程")
    print("=" * 60)
    
    tester = BlogAuthTester()
    
    # 测试数据
    test_username = "testflow"
    test_email = "testflow@example.com"
    test_password = "TestFlow123!"
    test_nickname = "测试流程"
    
    success_count = 0
    total_tests = 4
    
    # 1. 测试注册
    print("\n📋 测试1: 用户注册")
    if tester.test_registration(test_username, test_email, test_password, test_nickname):
        success_count += 1
        
        # 验证数据库
        print("   🔍 验证数据库...")
        tester.check_user_in_db(test_username)
    
    # 2. 测试登录
    print("\n📋 测试2: 用户登录")
    if tester.test_login(test_username, test_password):
        success_count += 1
    
    # 3. 测试登出
    print("\n📋 测试3: 用户登出")
    if tester.test_logout():
        success_count += 1
    
    # 4. 重新登录验证
    print("\n📋 测试4: 重新登录验证")
    if tester.test_login(test_username, test_password):
        success_count += 1
    
    # 总结
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！完整的注册-登录-登出流程正常工作")
    else:
        print("❌ 部分测试失败，请检查日志")
    
    return success_count == total_tests

if __name__ == "__main__":
    main()