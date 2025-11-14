#!/usr/bin/env python3
"""
测试登录接口并获取详细的400错误信息
"""
import requests
import json

def test_login_with_details():
    """测试登录并获取详细错误信息"""
    
    base_url = "http://localhost:5000"
    
    # 测试数据
    test_cases = [
        {
            "username_or_email": "choco1",
            "password": "Choco094late!",
            "description": "使用用户名choco1登录"
        },
        {
            "username_or_email": "choco1@qq.com",
            "password": "Choco094late!",
            "description": "使用邮箱choco1@qq.com登录"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 测试: {test_case['description']}")
        
        try:
            # 发送请求
            response = requests.post(
                f"{base_url}/api/auth/login",
                json={
                    "username_or_email": test_case["username_or_email"],
                    "password": test_case["password"]
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"原始响应: {response.text}")
            elif response.status_code == 200:
                data = response.json()
                print(f"✅ 登录成功: {data.get('message', 'Success')}")
                print(f"用户: {data.get('user', {}).get('username')}")
            else:
                print(f"响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    test_login_with_details()