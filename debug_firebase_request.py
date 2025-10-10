#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Firebase请求差异
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('config/production.env')

# 添加account-pool-service到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'account-pool-service'))

def debug_direct_request():
    """调试直接请求"""
    print("=" * 80)
    print("🔍 调试直接Firebase请求")
    print("=" * 80)
    
    try:
        from account_pool.firebase_api_pool import make_firebase_request
        
        # 测试邮箱
        test_email = "debug123456@007666.xyz"
        
        # 构建请求URL
        url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        
        # 构建请求参数
        payload = {
            "requestType": "EMAIL_SIGNIN",
            "email": test_email,
            "clientType": "CLIENT_TYPE_WEB",
            "continueUrl": "https://app.warp.dev/login",
            "canHandleCodeInApp": True
        }
        
        print(f"📧 测试邮箱: {test_email}")
        print(f"🔗 请求URL: {url}")
        print(f"📦 请求参数: {json.dumps(payload, indent=2)}")
        
        # 手动构建请求进行调试
        firebase_key = "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"
        full_url = f"{url}?key={firebase_key}"
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Origin': 'https://app.warp.dev',
            'Referer': 'https://app.warp.dev/',
            'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
            'x-firebase-gmpid': '1:13153726198:web:1cc16bca7287752f8e06d7'
        }
        
        print(f"🔧 请求Headers: {json.dumps(headers, indent=2)}")
        print(f"🌐 完整URL: {full_url}")
        
        # 发起请求
        response = requests.post(full_url, json=payload, headers=headers)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        return response.status_code == 200
            
    except Exception as e:
        print(f"❌ 调试异常: {e}")
        return False

def debug_complete_registration():
    """调试完整注册流程"""
    print("\n" + "=" * 80)
    print("🔍 调试完整注册流程请求")
    print("=" * 80)
    
    try:
        from account_pool.complete_registration import CompleteScriptRegistration
        
        # 创建注册器实例
        registrar = CompleteScriptRegistration()
        
        # 创建临时邮箱
        email_info = registrar.create_temp_email()
        
        if not email_info:
            print("❌ 创建临时邮箱失败")
            return False
            
        print(f"✅ 临时邮箱创建成功: {email_info['address']}")
        
        # 获取注册器的session信息
        try:
            headers_dict = dict(registrar.session.headers)
            print(f"🔧 注册器Headers: {json.dumps(headers_dict, indent=2)}")
        except Exception as e:
            print(f"🔧 注册器Headers: {registrar.session.headers}")
        
        # 手动构建请求进行调试
        url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        firebase_key = "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"
        full_url = f"{url}?key={firebase_key}"
        
        payload = {
            "requestType": "EMAIL_SIGNIN",
            "email": email_info['address'],
            "clientType": "CLIENT_TYPE_WEB",
            "continueUrl": "https://app.warp.dev/login",
            "canHandleCodeInApp": True
        }
        
        print(f"📧 测试邮箱: {email_info['address']}")
        print(f"🔗 请求URL: {url}")
        print(f"📦 请求参数: {json.dumps(payload, indent=2)}")
        print(f"🌐 完整URL: {full_url}")
        
        # 使用注册器的session发起请求
        response = registrar.session.post(full_url, json=payload)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        return response.status_code == 200
            
    except Exception as e:
        print(f"❌ 调试异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始调试Firebase请求...")
    
    # 调试1: 直接请求
    debug1_result = debug_direct_request()
    
    # 调试2: 完整注册流程
    debug2_result = debug_complete_registration()
    
    print("\n" + "=" * 80)
    print("📊 调试结果汇总")
    print("=" * 80)
    print(f"调试1 - 直接请求: {'✅ 成功' if debug1_result else '❌ 失败'}")
    print(f"调试2 - 完整注册流程: {'✅ 成功' if debug2_result else '❌ 失败'}")
    
    if debug1_result and debug2_result:
        print("\n🎉 所有调试成功!")
        return True
    else:
        print("\n❌ 部分调试失败!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)