#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
比较直接API调用与服务中API调用的差异
"""

import os
import json
import requests
import urllib3
from datetime import datetime

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def direct_api_call():
    """直接API调用"""
    print("🔍 直接API调用测试...")
    
    api_key = "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"
    print(f"🔑 使用API密钥: {api_key[:20]}...")
    
    url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
    
    payload = {
        "requestType": "EMAIL_SIGNIN",
        "email": "test@example.com",
        "clientType": "CLIENT_TYPE_WEB",
        "continueUrl": "https://app.warp.dev/login",
        "canHandleCodeInApp": True
    }
    
    headers = {
        'Content-Type': 'application/json',
        'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
        'x-firebase-gmpid': '1:13153726198:web:1cc16bca7287752f8e06d7'
    }
    
    # 构建完整URL
    separator = '&' if '?' in url else '?'
    full_url = f"{url}{separator}key={api_key}"
    
    print(f"URL: {full_url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    session = requests.Session()
    session.verify = False
    
    try:
        response = session.post(full_url, json=payload, headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 直接API调用成功")
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print("❌ 直接API调用失败")
            print(f"错误响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 直接API调用异常: {e}")
        return False

def service_api_call():
    """模拟服务中的API调用"""
    print("\n🔍 模拟服务中的API调用...")
    
    # 模拟从firebase_api_pool.py中的make_firebase_request方法
    try:
        # 导入firebase_api_pool模块
        import sys
        sys.path.append('./account-pool-service')
        from account_pool.firebase_api_pool import get_firebase_pool
        
        pool = get_firebase_pool()
        print("✅ 成功导入firebase_api_pool")
        
        url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        
        payload = {
            "requestType": "EMAIL_SIGNIN",
            "email": "test@example.com",
            "clientType": "CLIENT_TYPE_WEB",
            "continueUrl": "https://app.warp.dev/login",
            "canHandleCodeInApp": True
        }
        
        headers = {
            'Content-Type': 'application/json',
            'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
            'x-firebase-gmpid': '1:13153726198:web:1cc16bca7287752f8e06d7'
        }
        
        print(f"URL: {url}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # 使用服务中的方法调用
        response = pool.make_firebase_request(url, "POST", payload, headers, max_retries=3)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 服务API调用成功")
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print("❌ 服务API调用失败")
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 服务API调用异常: {e}")
        return False

def manual_service_call():
    """手动模拟服务中的API调用逻辑"""
    print("\n🔍 手动模拟服务中的API调用...")
    
    api_key = "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"
    print(f"🔑 使用API密钥: {api_key[:20]}...")
    
    url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
    
    payload = {
        "requestType": "EMAIL_SIGNIN",
        "email": "test@example.com",
        "clientType": "CLIENT_TYPE_WEB",
        "continueUrl": "https://app.warp.dev/login",
        "canHandleCodeInApp": True
    }
    
    # 模拟服务中的headers
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
    
    # 构建完整URL
    separator = '&' if '?' in url else '?'
    full_url = f"{url}{separator}key={api_key}"
    
    print(f"URL: {full_url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    # 设置SSL安全的请求配置
    session = requests.Session()
    session.verify = False  # 禁用SSL验证
    
    try:
        print("🌐 发起请求...")
        response = session.post(full_url, json=payload, headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 手动模拟服务API调用成功")
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print("❌ 手动模拟服务API调用失败")
            print(f"错误响应: {response.text}")
            
            # 检查是否是MISSING_CUSTOM_TOKEN错误
            try:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message')
                if error_message == "MISSING_CUSTOM_TOKEN":
                    print("\n🔍 发现MISSING_CUSTOM_TOKEN错误，尝试分析原因...")
                    
                    # 尝试不同的请求方式
                    print("\n尝试1: 使用GET方法...")
                    try:
                        get_response = session.get(full_url, headers=headers, timeout=30)
                        print(f"GET请求状态码: {get_response.status_code}")
                        print(f"GET响应: {get_response.text[:200]}...")
                    except Exception as e:
                        print(f"GET请求异常: {e}")
                    
                    print("\n尝试2: 修改Content-Type...")
                    headers2 = headers.copy()
                    headers2['Content-Type'] = 'application/x-www-form-urlencoded'
                    try:
                        form_response = session.post(full_url, data=json.dumps(payload), headers=headers2, timeout=30)
                        print(f"表单请求状态码: {form_response.status_code}")
                        print(f"表单响应: {form_response.text[:200]}...")
                    except Exception as e:
                        print(f"表单请求异常: {e}")
                    
                    print("\n尝试3: 添加Authorization头...")
                    headers3 = headers.copy()
                    headers3['Authorization'] = f'Bearer {api_key}'
                    try:
                        auth_response = session.post(full_url, json=payload, headers=headers3, timeout=30)
                        print(f"授权请求状态码: {auth_response.status_code}")
                        print(f"授权响应: {auth_response.text[:200]}...")
                    except Exception as e:
                        print(f"授权请求异常: {e}")
                    
            except json.JSONDecodeError:
                print("无法解析错误响应为JSON")
            
            return False
    except Exception as e:
        print(f"❌ 手动模拟服务API调用异常: {e}")
        return False

def compare_results(direct_result, service_result, manual_result):
    """比较结果"""
    print("\n" + "=" * 80)
    print("结果比较")
    print("=" * 80)
    
    print(f"直接API调用: {'✅ 成功' if direct_result else '❌ 失败'}")
    print(f"服务API调用: {'✅ 成功' if service_result else '❌ 失败'}")
    print(f"手动模拟调用: {'✅ 成功' if manual_result else '❌ 失败'}")
    
    if direct_result and not service_result:
        print("\n🔍 分析:")
        print("- 直接API调用成功，但服务API调用失败")
        print("- 可能是服务中的API调用逻辑有问题")
        print("- 建议检查服务中的请求参数和headers")
    
    if direct_result and not manual_result:
        print("\n🔍 分析:")
        print("- 直接API调用成功，但手动模拟服务API调用失败")
        print("- 可能是服务中使用的headers或参数有问题")
        print("- 建议仔细比较两者的差异")

if __name__ == "__main__":
    print("=" * 80)
    print("API调用比较工具")
    print("=" * 80)
    
    # 执行三种不同的API调用
    direct_result = direct_api_call()
    service_result = service_api_call()
    manual_result = manual_service_call()
    
    # 比较结果
    compare_results(direct_result, service_result, manual_result)
    
    print("\n" + "=" * 80)
    print("比较完成")
    print("=" * 80)