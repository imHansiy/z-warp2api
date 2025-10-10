#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试Firebase API端点问题
"""

import os
import json
import requests
from datetime import datetime

# 加载环境变量
from dotenv import load_dotenv
load_dotenv('config/production.env')

def test_firebase_endpoints():
    """测试不同的Firebase API端点"""
    
    # 获取配置
    api_key = os.getenv("FIREBASE_API_KEYS", "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs")
    project_id = os.getenv("FIREBASE_PROJECT_ID", "astral-field-294621")
    app_id = os.getenv("FIREBASE_APP_ID", "1:13153726198:web:1cc16bca7287752f8e06d7")
    
    print(f"🔧 Firebase配置:")
    print(f"  API密钥: {api_key[:20]}...")
    print(f"  项目ID: {project_id}")
    print(f"  应用ID: {app_id}")
    
    # 测试邮箱
    test_email = "test@example.com"
    
    # 测试不同的端点
    endpoints = [
        {
            "name": "sendOobCode (EMAIL_SIGNIN)",
            "url": "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode",
            "payload": {
                "requestType": "EMAIL_SIGNIN",
                "email": test_email,
                "clientType": "CLIENT_TYPE_WEB",
                "continueUrl": "https://app.warp.dev/login",
                "canHandleCodeInApp": True
            }
        },
        {
            "name": "sendOobCode (PASSWORD_RESET)",
            "url": "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode",
            "payload": {
                "requestType": "PASSWORD_RESET",
                "email": test_email,
                "clientType": "CLIENT_TYPE_WEB"
            }
        },
        {
            "name": "sendVerificationCode",
            "url": "https://identitytoolkit.googleapis.com/v1/accounts:sendVerificationCode",
            "payload": {
                "phoneNumber": "+1234567890",
                "recaptchaToken": "dummy"
            }
        }
    ]
    
    # 测试不同的headers组合
    headers_combinations = [
        {
            "name": "基础headers",
            "headers": {
                'Content-Type': 'application/json'
            }
        },
        {
            "name": "带Firebase客户端版本",
            "headers": {
                'Content-Type': 'application/json',
                'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web'
            }
        },
        {
            "name": "完整Firebase headers",
            "headers": {
                'Content-Type': 'application/json',
                'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
                'x-firebase-gmpid': app_id
            }
        },
        {
            "name": "浏览器模拟headers",
            "headers": {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://app.warp.dev/',
                'Origin': 'https://app.warp.dev',
                'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
                'x-firebase-gmpid': app_id
            }
        }
    ]
    
    print("\n" + "="*80)
    print("🔍 开始测试Firebase API端点")
    print("="*80)
    
    success_count = 0
    total_tests = len(endpoints) * len(headers_combinations)
    
    for endpoint in endpoints:
        print(f"\n📡 测试端点: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        
        for headers_config in headers_combinations:
            print(f"\n  🔧 Headers配置: {headers_config['name']}")
            
            # 构建完整URL
            separator = '&' if '?' in endpoint['url'] else '?'
            full_url = f"{endpoint['url']}{separator}key={api_key}"
            
            try:
                # 发起请求
                response = requests.post(
                    full_url, 
                    json=endpoint['payload'], 
                    headers=headers_config['headers'],
                    timeout=30
                )
                
                print(f"    响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"    ✅ 成功!")
                    success_count += 1
                    try:
                        response_data = response.json()
                        print(f"    响应数据: {json.dumps(response_data, indent=6)}")
                    except:
                        print(f"    响应文本: {response.text[:200]}...")
                else:
                    print(f"    ❌ 失败!")
                    try:
                        error_data = response.json()
                        print(f"    错误信息: {json.dumps(error_data, indent=6)}")
                    except:
                        print(f"    错误文本: {response.text[:200]}...")
                        
            except Exception as e:
                print(f"    ❌ 异常: {e}")
    
    print("\n" + "="*80)
    print(f"📊 测试结果: {success_count}/{total_tests} 成功")
    print("="*80)
    
    # 分析结果
    if success_count == 0:
        print("\n❌ 所有测试都失败了，可能的问题:")
        print("  1. API密钥无效或已过期")
        print("  2. 项目配置不正确")
        print("  3. Firebase服务未启用")
        print("  4. 网络连接问题")
    elif success_count < total_tests:
        print(f"\n⚠️ 部分测试成功 ({success_count}/{total_tests})")
        print("  可能是特定headers或端点配置问题")
    else:
        print(f"\n✅ 所有测试都成功!")
    
    return success_count > 0

def test_anonymous_user_creation():
    """测试匿名用户创建"""
    print("\n" + "="*80)
    print("🔍 测试匿名用户创建")
    print("="*80)
    
    api_key = os.getenv("FIREBASE_API_KEYS", "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs")
    app_id = os.getenv("FIREBASE_APP_ID", "1:13153726198:web:1cc16bca7287752f8e06d7")
    
    url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
    separator = '?' if '?' not in url else '&'
    full_url = f"{url}{separator}key={api_key}"
    
    payload = {
        "returnSecureToken": True
    }
    
    headers = {
        'Content-Type': 'application/json',
        'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
        'x-firebase-gmpid': app_id
    }
    
    try:
        response = requests.post(full_url, json=payload, headers=headers, timeout=30)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 匿名用户创建成功!")
            response_data = response.json()
            print(f"用户ID: {response_data.get('localId')}")
            print(f"ID Token: {response_data.get('idToken', '')[:50]}...")
            return True
        else:
            print("❌ 匿名用户创建失败!")
            try:
                error_data = response.json()
                print(f"错误信息: {json.dumps(error_data, indent=2)}")
            except:
                print(f"错误文本: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Firebase API端点调试工具")
    print(f"⏰ 时间: {datetime.now().isoformat()}")
    
    # 测试基本端点
    endpoint_success = test_firebase_endpoints()
    
    # 测试匿名用户创建
    anonymous_success = test_anonymous_user_creation()
    
    print("\n" + "="*80)
    print("📋 总结")
    print("="*80)
    print(f"基本端点测试: {'✅ 成功' if endpoint_success else '❌ 失败'}")
    print(f"匿名用户创建: {'✅ 成功' if anonymous_success else '❌ 失败'}")
    
    if endpoint_success and anonymous_success:
        print("\n✅ Firebase API配置正常，问题可能在其他地方")
    elif anonymous_success:
        print("\n⚠️ 匿名用户创建成功，但邮箱登录失败，可能是邮箱服务配置问题")
    else:
        print("\n❌ Firebase API配置有问题，需要检查API密钥和项目设置")

if __name__ == "__main__":
    main()