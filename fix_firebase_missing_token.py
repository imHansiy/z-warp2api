#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复Firebase MISSING_CUSTOM_TOKEN错误
分析请求参数并添加缺失的参数
"""

import os
import json
import requests
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def analyze_missing_token_error():
    """分析MISSING_CUSTOM_TOKEN错误"""
    print("🔍 分析MISSING_CUSTOM_TOKEN错误...")
    
    # 检查Firebase API文档
    print("\n📋 检查Firebase API文档...")
    print("根据Firebase文档，EMAIL_SIGNIN请求可能需要以下参数:")
    print("- requestType: EMAIL_SIGNIN")
    print("- email: 用户邮箱")
    print("- clientType: CLIENT_TYPE_WEB")
    print("- continueUrl: 登录后重定向URL")
    print("- canHandleCodeInApp: 是否在应用中处理代码")
    print("- 如果是现有用户，可能需要idToken或customToken")
    
    # 尝试不同的请求参数组合
    test_cases = [
        {
            "name": "基本请求（当前使用）",
            "payload": {
                "requestType": "EMAIL_SIGNIN",
                "email": "test@example.com",
                "clientType": "CLIENT_TYPE_WEB",
                "continueUrl": "https://app.warp.dev/login",
                "canHandleCodeInApp": True
            }
        },
        {
            "name": "添加returnSecureToken",
            "payload": {
                "requestType": "EMAIL_SIGNIN",
                "email": "test@example.com",
                "clientType": "CLIENT_TYPE_WEB",
                "continueUrl": "https://app.warp.dev/login",
                "canHandleCodeInApp": True,
                "returnSecureToken": True
            }
        },
        {
            "name": "使用不同的请求类型",
            "payload": {
                "requestType": "PASSWORD_RESET",
                "email": "test@example.com",
                "clientType": "CLIENT_TYPE_WEB"
            }
        },
        {
            "name": "尝试使用EMAIL_PASSWORD_SIGNIN",
            "payload": {
                "requestType": "EMAIL_PASSWORD_SIGNIN",
                "email": "test@example.com",
                "password": "dummy_password",
                "clientType": "CLIENT_TYPE_WEB",
                "returnSecureToken": True
            }
        }
    ]
    
    api_key = "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"
    url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
    
    headers = {
        'Content-Type': 'application/json',
        'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
        'x-firebase-gmpid': '1:13153726198:web:1cc16bca7287752f8e06d7'
    }
    
    session = requests.Session()
    session.verify = False
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试 {i}: {test_case['name']}")
        print(f"请求参数: {json.dumps(test_case['payload'], indent=2)}")
        
        # 构建完整URL
        separator = '&' if '?' in url else '?'
        full_url = f"{url}{separator}key={api_key}"
        
        try:
            response = session.post(full_url, json=test_case['payload'], headers=headers, timeout=30)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 请求成功")
                try:
                    data = response.json()
                    print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"响应文本: {response.text}")
            else:
                print("❌ 请求失败")
                print(f"错误响应: {response.text}")
                
                # 分析错误
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message')
                    print(f"错误消息: {error_message}")
                    
                    if error_message == "MISSING_CUSTOM_TOKEN":
                        print("\n🔍 分析MISSING_CUSTOM_TOKEN错误:")
                        print("可能的原因:")
                        print("1. Firebase项目配置要求使用自定义令牌")
                        print("2. 需要先创建匿名用户或使用其他认证方式")
                        print("3. 请求类型不正确")
                        
                        # 尝试先创建匿名用户
                        print("\n🔧 尝试先创建匿名用户...")
                        anon_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
                        anon_payload = {
                            "returnSecureToken": True
                        }
                        
                        try:
                            anon_response = session.post(
                                f"{anon_url}?key={api_key}", 
                                json=anon_payload, 
                                headers=headers, 
                                timeout=30
                            )
                            
                            if anon_response.status_code == 200:
                                print("✅ 匿名用户创建成功")
                                anon_data = anon_response.json()
                                id_token = anon_data.get('idToken')
                                
                                if id_token:
                                    print(f"🔑 获取到ID Token: {id_token[:50]}...")
                                    
                                    # 尝试使用ID Token
                                    print("\n🔧 尝试使用ID Token进行邮箱登录...")
                                    email_payload = test_case['payload'].copy()
                                    email_payload['idToken'] = id_token
                                    
                                    email_response = session.post(
                                        full_url, 
                                        json=email_payload, 
                                        headers=headers, 
                                        timeout=30
                                    )
                                    
                                    print(f"邮箱登录状态码: {email_response.status_code}")
                                    if email_response.status_code == 200:
                                        print("✅ 使用ID Token的邮箱登录成功")
                                        email_data = email_response.json()
                                        print(f"邮箱登录响应: {json.dumps(email_data, indent=2, ensure_ascii=False)}")
                                    else:
                                        print(f"❌ 使用ID Token的邮箱登录失败: {email_response.text}")
                            else:
                                print(f"❌ 匿名用户创建失败: {anon_response.text}")
                                
                        except Exception as e:
                            print(f"❌ 匿名用户创建异常: {e}")
                    
                except json.JSONDecodeError:
                    print("无法解析错误响应为JSON")
        
        except Exception as e:
            print(f"❌ 请求异常: {e}")

def test_different_endpoints():
    """测试不同的API端点"""
    print("\n🔍 测试不同的API端点...")
    
    api_key = "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"
    
    endpoints = [
        {
            "name": "发送邮箱登录链接",
            "url": "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode",
            "method": "POST",
            "payload": {
                "requestType": "EMAIL_SIGNIN",
                "email": "test@example.com",
                "clientType": "CLIENT_TYPE_WEB",
                "continueUrl": "https://app.warp.dev/login",
                "canHandleCodeInApp": True
            }
        },
        {
            "name": "使用邮箱链接登录",
            "url": "https://identitytoolkit.googleapis.com/v1/accounts:signInWithEmailLink",
            "method": "POST",
            "payload": {
                "email": "test@example.com",
                "oobCode": "dummy_oob_code"
            }
        },
        {
            "name": "创建匿名用户",
            "url": "https://identitytoolkit.googleapis.com/v1/accounts:signUp",
            "method": "POST",
            "payload": {
                "returnSecureToken": True
            }
        }
    ]
    
    headers = {
        'Content-Type': 'application/json',
        'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
        'x-firebase-gmpid': '1:13153726198:web:1cc16bca7287752f8e06d7'
    }
    
    session = requests.Session()
    session.verify = False
    
    for endpoint in endpoints:
        print(f"\n📋 测试端点: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        print(f"方法: {endpoint['method']}")
        print(f"请求参数: {json.dumps(endpoint['payload'], indent=2)}")
        
        # 构建完整URL
        separator = '&' if '?' in endpoint['url'] else '?'
        full_url = f"{endpoint['url']}{separator}key={api_key}"
        
        try:
            if endpoint['method'] == "POST":
                response = session.post(full_url, json=endpoint['payload'], headers=headers, timeout=30)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 请求成功")
                try:
                    data = response.json()
                    print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"响应文本: {response.text}")
            else:
                print("❌ 请求失败")
                print(f"错误响应: {response.text}")
        
        except Exception as e:
            print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    print("=" * 80)
    print("Firebase MISSING_CUSTOM_TOKEN 错误修复工具")
    print("=" * 80)
    
    # 分析错误
    analyze_missing_token_error()
    
    # 测试不同端点
    test_different_endpoints()
    
    print("\n" + "=" * 80)
    print("分析完成")
    print("=" * 80)