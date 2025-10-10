#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试服务中的Firebase请求
"""

import os
import json
import requests
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def debug_service_request():
    """调试服务中的Firebase请求"""
    
    # 从环境变量获取配置
    identity_toolkit_base = os.getenv("IDENTITY_TOOLKIT_BASE", "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode")
    warp_base_url = os.getenv("WARP_BASE_URL", "https://app.warp.dev")
    
    print(f"🔍 调试服务中的Firebase请求...")
    print(f"IDENTITY_TOOLKIT_BASE: {identity_toolkit_base}")
    print(f"WARP_BASE_URL: {warp_base_url}")
    
    # 模拟服务中的请求
    api_key = "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"
    test_email = "test789@example.com"
    
    # 构建URL，与服务中一致
    separator = '&' if '?' in identity_toolkit_base else '?'
    full_url = f"{identity_toolkit_base}{separator}key={api_key}"
    
    print(f"\n📡 完整URL: {full_url}")
    
    # 与服务中一致的payload
    payload = {
        "requestType": "EMAIL_SIGNIN",
        "email": test_email,
        "clientType": "CLIENT_TYPE_WEB",
        "continueUrl": f"{warp_base_url}/login",
        "canHandleCodeInApp": True
    }
    
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    # 与服务中一致的headers
    headers = {
        'Content-Type': 'application/json',
        'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web'
    }
    
    print(f"📋 Headers: {json.dumps(headers, indent=2)}")
    
    try:
        # 发起请求
        response = requests.post(full_url, json=payload, headers=headers, timeout=30, verify=False)
        
        print(f"\n📊 响应状态码: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"📄 响应体: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"📄 响应体 (原始): {response.text}")
        
        if response.status_code == 200:
            print("\n✅ 服务中的请求格式成功！")
        else:
            print(f"\n❌ 服务中的请求格式失败: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")

def test_url_construction():
    """测试不同的URL构造方式"""
    
    base_url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
    api_key = "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"
    
    print("\n🔧 测试不同的URL构造方式...")
    
    # 方式1：使用params参数
    print("\n--- 方式1：使用params参数 ---")
    try:
        payload = {
            "requestType": "EMAIL_SIGNIN",
            "email": "test1@example.com",
            "clientType": "CLIENT_TYPE_WEB",
            "continueUrl": "https://app.warp.dev/login",
            "canHandleCodeInApp": True
        }
        
        headers = {'Content-Type': 'application/json'}
        params = {"key": api_key}
        
        response = requests.post(base_url, params=params, json=payload, headers=headers, timeout=30, verify=False)
        print(f"状态码: {response.status_code}")
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"错误: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误: {response.text}")
        else:
            print("✅ 成功")
            
    except Exception as e:
        print(f"异常: {e}")
    
    # 方式2：直接构造URL
    print("\n--- 方式2：直接构造URL ---")
    try:
        payload = {
            "requestType": "EMAIL_SIGNIN",
            "email": "test2@example.com",
            "clientType": "CLIENT_TYPE_WEB",
            "continueUrl": "https://app.warp.dev/login",
            "canHandleCodeInApp": True
        }
        
        headers = {'Content-Type': 'application/json'}
        full_url = f"{base_url}?key={api_key}"
        
        response = requests.post(full_url, json=payload, headers=headers, timeout=30, verify=False)
        print(f"状态码: {response.status_code}")
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"错误: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误: {response.text}")
        else:
            print("✅ 成功")
            
    except Exception as e:
        print(f"异常: {e}")

if __name__ == "__main__":
    debug_service_request()
    test_url_construction()