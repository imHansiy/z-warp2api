#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分析Firebase MISSING_CUSTOM_TOKEN错误
"""

import os
import json
import requests
from datetime import datetime

# 加载环境变量
from dotenv import load_dotenv
load_dotenv('config/production.env')

def analyze_missing_custom_token():
    """分析MISSING_CUSTOM_TOKEN错误的原因"""
    
    print("🔍 分析Firebase MISSING_CUSTOM_TOKEN错误")
    print("="*80)
    
    # 获取配置
    api_key = os.getenv("FIREBASE_API_KEYS", "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs")
    app_id = os.getenv("FIREBASE_APP_ID", "1:13153726198:web:1cc16bca7287752f8e06d7")
    
    print(f"🔧 Firebase配置:")
    print(f"  API密钥: {api_key[:20]}...")
    print(f"  应用ID: {app_id}")
    
    # 测试邮箱
    test_email = "test@example.com"
    
    # 测试不同的请求方式
    test_cases = [
        {
            "name": "直接POST请求（当前方式）",
            "url": "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode",
            "method": "POST",
            "params": {"key": api_key},
            "json": {
                "requestType": "EMAIL_SIGNIN",
                "email": test_email,
                "clientType": "CLIENT_TYPE_WEB",
                "continueUrl": "https://app.warp.dev/login",
                "canHandleCodeInApp": True
            },
            "headers": {
                'Content-Type': 'application/json',
                'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
                'x-firebase-gmpid': app_id
            }
        },
        {
            "name": "GET请求（URL参数）",
            "url": "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode",
            "method": "GET",
            "params": {
                "key": api_key,
                "requestType": "EMAIL_SIGNIN",
                "email": test_email,
                "clientType": "CLIENT_TYPE_WEB",
                "continueUrl": "https://app.warp.dev/login",
                "canHandleCodeInApp": "true"
            },
            "json": None,
            "headers": {
                'Accept': 'application/json',
                'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
                'x-firebase-gmpid': app_id
            }
        },
        {
            "name": "POST请求（URL参数+JSON）",
            "url": "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode",
            "method": "POST",
            "params": {"key": api_key},
            "json": {
                "requestType": "EMAIL_SIGNIN",
                "email": test_email,
                "clientType": "CLIENT_TYPE_WEB",
                "continueUrl": "https://app.warp.dev/login",
                "canHandleCodeInApp": True
            },
            "headers": {
                'Content-Type': 'application/x-www-form-urlencoded',
                'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
                'x-firebase-gmpid': app_id
            },
            "data": "requestType=EMAIL_SIGNIN&email=test@example.com&clientType=CLIENT_TYPE_WEB&continueUrl=https://app.warp.dev/login&canHandleCodeInApp=true"
        }
    ]
    
    success_count = 0
    
    for test_case in test_cases:
        print(f"\n📡 测试: {test_case['name']}")
        print(f"   方法: {test_case['method']}")
        print(f"   URL: {test_case['url']}")
        
        try:
            # 准备请求参数
            kwargs = {
                "url": test_case['url'],
                "method": test_case['method'],
                "params": test_case['params'],
                "headers": test_case['headers'],
                "timeout": 30
            }
            
            if test_case['method'].upper() == 'POST':
                if 'json' in test_case and test_case['json']:
                    kwargs['json'] = test_case['json']
                elif 'data' in test_case and test_case['data']:
                    kwargs['data'] = test_case['data']
            
            # 发起请求
            response = requests.request(**kwargs)
            
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
                    
                    # 分析错误类型
                    error_message = error_data.get('error', {}).get('message', '')
                    if 'MISSING_CUSTOM_TOKEN' in error_message:
                        print(f"    🔍 发现MISSING_CUSTOM_TOKEN错误!")
                        print(f"    💡 可能原因:")
                        print(f"       1. 请求参数格式不正确")
                        print(f"       2. API密钥权限不足")
                        print(f"       3. Firebase项目配置问题")
                        print(f"       4. 请求方法不匹配")
                except:
                    print(f"    错误文本: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"    ❌ 异常: {e}")
    
    print("\n" + "="*80)
    print(f"📊 测试结果: {success_count}/{len(test_cases)} 成功")
    print("="*80)
    
    return success_count > 0

def test_with_different_endpoints():
    """测试不同的端点"""
    
    print("\n🔍 测试不同的Firebase端点")
    print("="*80)
    
    api_key = os.getenv("FIREBASE_API_KEYS", "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs")
    app_id = os.getenv("FIREBASE_APP_ID", "1:13153726198:web:1cc16bca7287752f8e06d7")
    test_email = "test@example.com"
    
    # 测试不同的端点
    endpoints = [
        {
            "name": "identitytoolkit.googleapis.com/v1/accounts:sendOobCode",
            "url": "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        },
        {
            "name": "www.googleapis.com/identitytoolkit/v3/relyingparty/sendOobCode",
            "url": "https://www.googleapis.com/identitytoolkit/v3/relyingparty/sendOobCode"
        },
        {
            "name": "identitytoolkit.googleapis.com/v2/accounts:sendOobCode",
            "url": "https://identitytoolkit.googleapis.com/v2/accounts:sendOobCode"
        }
    ]
    
    success_count = 0
    
    for endpoint in endpoints:
        print(f"\n📡 测试端点: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        
        try:
            response = requests.post(
                f"{endpoint['url']}?key={api_key}",
                json={
                    "requestType": "EMAIL_SIGNIN",
                    "email": test_email,
                    "clientType": "CLIENT_TYPE_WEB",
                    "continueUrl": "https://app.warp.dev/login",
                    "canHandleCodeInApp": True
                },
                headers={
                    'Content-Type': 'application/json',
                    'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
                    'x-firebase-gmpid': app_id
                },
                timeout=30
            )
            
            print(f"    响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"    ✅ 成功!")
                success_count += 1
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
    print(f"📊 端点测试结果: {success_count}/{len(endpoints)} 成功")
    print("="*80)
    
    return success_count > 0

def analyze_service_request():
    """分析服务中的请求"""
    
    print("\n🔍 分析服务中的请求方式")
    print("="*80)
    
    # 从日志中提取实际的请求
    print("📋 从日志中观察到的请求模式:")
    print("  1. 使用POST方法")
    print("  2. URL: https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode")
    print("  3. 参数通过JSON传递")
    print("  4. API密钥作为URL参数")
    print("  5. 包含Firebase特定的headers")
    
    # 模拟服务中的请求
    api_key = os.getenv("FIREBASE_API_KEYS", "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs")
    app_id = os.getenv("FIREBASE_APP_ID", "1:13153726198:web:1cc16bca7287752f8e06d7")
    test_email = "test@example.com"
    
    print("\n📡 模拟服务中的请求")
    
    try:
        # 完全模拟服务中的请求方式
        url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        
        # 构建完整URL（与服务中一致）
        separator = '&' if '?' in url else '?'
        full_url = f"{url}{separator}key={api_key}"
        
        payload = {
            "requestType": "EMAIL_SIGNIN",
            "email": test_email,
            "clientType": "CLIENT_TYPE_WEB",
            "continueUrl": "https://app.warp.dev/login",
            "canHandleCodeInApp": True
        }
        
        headers = {
            'Content-Type': 'application/json',
            'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
            'x-firebase-gmpid': app_id
        }
        
        print(f"  URL: {full_url}")
        print(f"  方法: POST")
        print(f"  Payload: {json.dumps(payload, indent=2)}")
        print(f"  Headers: {json.dumps(headers, indent=2)}")
        
        response = requests.post(full_url, json=payload, headers=headers, timeout=30)
        
        print(f"\n  响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("  ✅ 成功!")
            response_data = response.json()
            print(f"  响应数据: {json.dumps(response_data, indent=6)}")
            return True
        else:
            print("  ❌ 失败!")
            try:
                error_data = response.json()
                print(f"  错误信息: {json.dumps(error_data, indent=6)}")
            except:
                print(f"  错误文本: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Firebase MISSING_CUSTOM_TOKEN错误分析工具")
    print(f"⏰ 时间: {datetime.now().isoformat()}")
    
    # 测试不同的请求方式
    request_success = analyze_missing_custom_token()
    
    # 测试不同的端点
    endpoint_success = test_with_different_endpoints()
    
    # 分析服务中的请求
    service_success = analyze_service_request()
    
    print("\n" + "="*80)
    print("📋 分析总结")
    print("="*80)
    print(f"请求方式测试: {'✅ 成功' if request_success else '❌ 失败'}")
    print(f"端点测试: {'✅ 成功' if endpoint_success else '❌ 失败'}")
    print(f"服务请求模拟: {'✅ 成功' if service_success else '❌ 失败'}")
    
    if request_success and endpoint_success and service_success:
        print("\n✅ 所有测试都成功，Firebase API配置正常")
        print("💡 如果服务中仍然失败，可能是:")
        print("   1. 环境变量加载问题")
        print("   2. 请求拦截或修改")
        print("   3. 网络代理问题")
        print("   4. 代码中的其他错误")
    else:
        print("\n❌ 部分测试失败，需要进一步调查")
        if not service_success:
            print("💡 服务请求模拟失败，这可能是问题所在")

if __name__ == "__main__":
    main()