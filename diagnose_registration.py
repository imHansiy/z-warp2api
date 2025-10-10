#!/usr/bin/env python3
"""
诊断注册问题
"""

import sys
import os
import json
import requests

# 添加账号池服务路径
sys.path.insert(0, '/app/account-pool-service')

def diagnose():
    print("=" * 80)
    print("🔍 诊断注册问题")
    print("=" * 80)
    
    # 1. 检查配置
    print("\n1. 检查配置...")
    config_file = "/app/config/production.env"
    if os.path.exists(config_file):
        print("✅ 配置文件存在")
        with open(config_file, 'r') as f:
            content = f.read()
            if "FIREBASE_API_KEYS" in content:
                print("✅ Firebase API密钥已配置")
            else:
                print("❌ Firebase API密钥未配置")
    else:
        print("❌ 配置文件不存在")
    
    # 2. 测试原始请求
    print("\n2. 测试原始Firebase请求...")
    firebase_keys = os.getenv("FIREBASE_API_KEYS")
    if firebase_keys:
        api_key = firebase_keys.split(",")[0].strip()
        print(f"🔑 使用API密钥: {api_key[:20]}...")
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        payload = {
            "requestType": "EMAIL_SIGNIN",
            "email": "test@example.com",
            "clientType": "CLIENT_TYPE_WEB",
            "continueUrl": "https://app.warp.dev/login",
            "canHandleCodeInApp": True
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        try:
            session = requests.Session()
            session.verify = False
            response = session.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print("✅ 原始请求成功")
            else:
                print(f"❌ 原始请求失败: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   错误: {error_data.get('error', {}).get('message', 'Unknown')}")
                except:
                    pass
        except Exception as e:
            print(f"❌ 原始请求异常: {e}")
    
    # 3. 测试带特殊headers的请求
    print("\n3. 测试带Firebase特殊headers的请求...")
    headers_with_firebase = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
        'x-firebase-gmpid': '1:13153726198:web:1cc16bca7287752f8e06d7'
    }
    
    try:
        response = session.post(url, json=payload, headers=headers_with_firebase, timeout=30)
        
        if response.status_code == 200:
            print("✅ 带特殊headers的请求成功")
        else:
            print(f"❌ 带特殊headers的请求失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误: {error_data.get('error', {}).get('message', 'Unknown')}")
            except:
                pass
    except Exception as e:
        print(f"❌ 带特殊headers的请求异常: {e}")
    
    # 4. 测试API池请求
    print("\n4. 测试API池请求...")
    try:
        from account_pool.firebase_api_pool import make_firebase_request
        
        response = make_firebase_request(url.replace("?key=" + api_key, ""), "POST", payload)
        
        if response.status_code == 200:
            print("✅ API池请求成功")
        else:
            print(f"❌ API池请求失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误: {error_data.get('error', {}).get('message', 'Unknown')}")
            except:
                pass
    except Exception as e:
        print(f"❌ API池请求异常: {e}")
    
    # 5. 检查API密钥状态
    print("\n5. 检查API密钥状态...")
    try:
        from account_pool.firebase_api_pool import get_firebase_pool
        pool = get_firebase_pool()
        status = pool.get_pool_status()
        
        print(f"   总密钥数: {status['total_keys']}")
        for key_status in status['keys_status']:
            print(f"   密钥: {key_status['key_preview']}")
            print(f"   成功率: {key_status['success_rate']}")
            print(f"   冷却中: {key_status['in_cooldown']}")
            if key_status['in_cooldown']:
                print(f"   冷却至: {key_status['cooldown_until']}")
    except Exception as e:
        print(f"❌ 检查API密钥状态失败: {e}")
    
    # 6. 结论
    print("\n" + "=" * 80)
    print("💡 诊断结论")
    print("=" * 80)
    print("如果原始请求成功但API池请求失败，问题可能在于：")
    print("1. API池的实现有问题")
    print("2. API池使用的headers或参数不正确")
    print("3. API密钥池的缓存或状态问题")
    print("\n建议：")
    print("- 检查API池的默认headers设置")
    print("- 确保API池使用正确的请求参数")
    print("- 考虑重置API密钥池的状态")

if __name__ == "__main__":
    diagnose()