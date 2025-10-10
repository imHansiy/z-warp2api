#!/usr/bin/env python3
"""
在Docker容器内调试Firebase API请求
"""

import os
import sys
import json
import requests

# 添加账号池服务路径
sys.path.insert(0, '/app/account-pool-service')

# 导入Firebase API池
from account_pool.firebase_api_pool import make_firebase_request

def test_firebase_request():
    """测试Firebase API请求"""
    print("=" * 80)
    print("🔍 测试Firebase API请求（Docker容器内）")
    print("=" * 80)
    
    # 测试发送邮箱登录请求
    url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
    
    payload = {
        "requestType": "EMAIL_SIGNIN",
        "email": "test@example.com",
        "clientType": "CLIENT_TYPE_WEB",
        "continueUrl": "https://app.warp.dev/login",
        "canHandleCodeInApp": True
    }
    
    # 自定义headers，确保包含所有必要的字段
    custom_headers = {
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
    
    print(f"📤 发送请求到: {url}")
    print(f"📋 请求参数: {json.dumps(payload, indent=2)}")
    print(f"📋 请求Headers:")
    for k, v in custom_headers.items():
        print(f"  {k}: {v}")
    
    try:
        # 使用自定义headers发起请求
        response = make_firebase_request(url, "POST", payload, custom_headers)
        
        print(f"\n📥 响应状态码: {response.status_code}")
        print(f"📋 响应Headers:")
        for k, v in response.headers.items():
            print(f"  {k}: {v}")
        
        print(f"\n📄 响应内容:")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(response.text)
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_raw_request():
    """测试原始请求（不使用API池）"""
    print("\n" + "=" * 80)
    print("🔍 测试原始Firebase API请求（不使用API池）")
    print("=" * 80)
    
    # 获取API密钥
    firebase_keys = os.getenv("FIREBASE_API_KEYS")
    if not firebase_keys:
        print("❌ 未找到FIREBASE_API_KEYS环境变量")
        return False
    
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
    
    print(f"📤 发送请求到: {url}")
    print(f"📋 请求参数: {json.dumps(payload, indent=2)}")
    
    try:
        session = requests.Session()
        session.verify = False  # 禁用SSL验证
        
        response = session.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"\n📥 响应状态码: {response.status_code}")
        print(f"📄 响应内容:")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(response.text)
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🐳 Docker容器内Firebase API调试")
    print(f"📍 当前工作目录: {os.getcwd()}")
    
    # 检查环境变量
    print(f"\n📋 环境变量:")
    print(f"  FIREBASE_API_KEYS: {os.getenv('FIREBASE_API_KEYS', 'NOT SET')[:50]}...")
    
    # 测试1: 使用API池
    print("\n" + "=" * 80)
    print("测试1: 使用API池")
    success1 = test_firebase_request()
    
    # 测试2: 使用原始请求
    print("\n" + "=" * 80)
    print("测试2: 使用原始请求")
    success2 = test_raw_request()
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 测试结果总结")
    print("=" * 80)
    print(f"  API池请求: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"  原始请求: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if not success1 and not success2:
        print("\n❌ 所有测试都失败了，问题可能在于:")
        print("  1. API密钥无效")
        print("  2. 网络连接问题")
        print("  3. Firebase API端点变更")
        print("  4. 请求参数不正确")
    elif success1 and not success2:
        print("\n⚠️ API池请求成功，但原始请求失败")
        print("  这表明API池可能有特殊的处理逻辑")
    elif not success1 and success2:
        print("\n⚠️ 原始请求成功，但API池请求失败")
        print("  这表明API池的实现可能有问题")
    else:
        print("\n✅ 所有测试都成功了，问题可能在于:")
        print("  1. 实际使用的邮箱地址")
        print("  2. 其他请求参数")
        print("  3. 时序问题")