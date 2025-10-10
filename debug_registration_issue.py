#!/usr/bin/env python3
"""
深入诊断注册问题
"""

import os
import sys
import json
import time
import requests

# 添加账号池服务路径
sys.path.insert(0, 'account-pool-service')

def test_direct_firebase_api():
    """直接测试Firebase API"""
    print("=" * 80)
    print("1. 直接测试Firebase API（不使用API池）")
    print("=" * 80)
    
    # 获取API密钥
    firebase_keys = os.getenv("FIREBASE_API_KEYS")
    if not firebase_keys:
        print("❌ 未找到FIREBASE_API_KEYS环境变量")
        return False
    
    api_key = firebase_keys.split(",")[0].strip()
    print(f"🔑 使用API密钥: {api_key[:20]}...")
    
    # 测试不同的请求方式
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
    
    # 测试1: 最小化请求
    print("\n测试1: 最小化请求")
    payload_minimal = {
        "requestType": "EMAIL_SIGNIN",
        "email": "test@example.com"
    }
    
    headers_minimal = {
        'Content-Type': 'application/json'
    }
    
    try:
        session = requests.Session()
        session.verify = False
        response = session.post(url, json=payload_minimal, headers=headers_minimal, timeout=30)
        
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 最小化请求成功")
        else:
            print(f"   ❌ 最小化请求失败")
            try:
                error_data = response.json()
                print(f"   错误: {error_data.get('error', {}).get('message', 'Unknown')}")
            except:
                pass
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 测试2: 完整请求，不带特殊headers
    print("\n测试2: 完整请求，不带特殊headers")
    payload_full = {
        "requestType": "EMAIL_SIGNIN",
        "email": "test@example.com",
        "clientType": "CLIENT_TYPE_WEB",
        "continueUrl": "https://app.warp.dev/login",
        "canHandleCodeInApp": True
    }
    
    headers_full = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = session.post(url, json=payload_full, headers=headers_full, timeout=30)
        
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 完整请求成功")
        else:
            print(f"   ❌ 完整请求失败")
            try:
                error_data = response.json()
                print(f"   错误: {error_data.get('error', {}).get('message', 'Unknown')}")
            except:
                pass
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 测试3: 带Firebase特殊headers
    print("\n测试3: 带Firebase特殊headers")
    headers_firebase = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
        'x-firebase-gmpid': '1:13153726198:web:1cc16bca7287752f8e06d7'
    }
    
    try:
        response = session.post(url, json=payload_full, headers=headers_firebase, timeout=30)
        
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 带Firebase headers的请求成功")
            return True
        else:
            print(f"   ❌ 带Firebase headers的请求失败")
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown')
                print(f"   错误: {error_msg}")
                
                # 分析错误
                if "MISSING_CUSTOM_TOKEN" in error_msg:
                    print("\n💡 分析: MISSING_CUSTOM_TOKEN错误")
                    print("   这个错误通常表示:")
                    print("   1. API密钥无效或已过期")
                    print("   2. 请求参数不正确")
                    print("   3. Firebase API端点变更")
                    print("   4. 需要额外的认证参数")
            except:
                pass
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    return False

def test_api_pool():
    """测试API池"""
    print("\n" + "=" * 80)
    print("2. 测试API池")
    print("=" * 80)
    
    try:
        from account_pool.firebase_api_pool import make_firebase_request
        
        url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        payload = {
            "requestType": "EMAIL_SIGNIN",
            "email": "test@example.com",
            "clientType": "CLIENT_TYPE_WEB",
            "continueUrl": "https://app.warp.dev/login",
            "canHandleCodeInApp": True
        }
        
        # 使用API池的默认headers
        response = make_firebase_request(url, "POST", payload)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ API池请求成功")
            return True
        else:
            print(f"❌ API池请求失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误: {error_data.get('error', {}).get('message', 'Unknown')}")
            except:
                pass
            return False
            
    except Exception as e:
        print(f"❌ API池测试异常: {e}")
        return False

def test_complete_registration():
    """测试完整注册流程"""
    print("\n" + "=" * 80)
    print("3. 测试完整注册流程（仅第一步）")
    print("=" * 80)
    
    try:
        from account_pool.complete_registration import CompleteScriptRegistration
        
        reg = CompleteScriptRegistration()
        
        # 只测试创建邮箱和发送请求
        print("\n步骤1: 创建临时邮箱")
        email_info = reg.create_temp_email()
        
        if not email_info:
            print("❌ 创建邮箱失败")
            return False
        
        print(f"✅ 邮箱创建成功: {email_info['address']}")
        
        print("\n步骤2: 发送邮箱登录请求")
        result = reg.send_email_signin_request(email_info['address'])
        
        if result['success']:
            print("✅ 发送请求成功")
            return True
        else:
            print(f"❌ 发送请求失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 完整注册测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_firebase_key():
    """检查Firebase API密钥"""
    print("\n" + "=" * 80)
    print("4. 检查Firebase API密钥")
    print("=" * 80)
    
    firebase_keys = os.getenv("FIREBASE_API_KEYS")
    if not firebase_keys:
        print("❌ 未找到FIREBASE_API_KEYS环境变量")
        return False
    
    keys = [key.strip() for key in firebase_keys.split(",") if key.strip()]
    print(f"找到 {len(keys)} 个API密钥")
    
    for i, key in enumerate(keys):
        print(f"  密钥 {i+1}: {key[:20]}...")
    
    # 测试API密钥有效性
    print("\n测试API密钥有效性...")
    test_url = f"https://www.googleapis.com/identitytoolkit/v3/projects"
    headers = {'Authorization': f'Bearer {keys[0]}'}
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ API密钥有效")
        else:
            print(f"⚠️ API密钥可能无效 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 无法验证API密钥: {e}")
    
    return True

def main():
    print("🔍 深入诊断注册问题")
    print(f"⏰ 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查环境变量
    print(f"\n📋 环境变量检查:")
    print(f"  FIREBASE_API_KEYS: {'已设置' if os.getenv('FIREBASE_API_KEYS') else '未设置'}")
    print(f"  MOEMAIL_URL: {os.getenv('MOEMAIL_URL', '未设置')}")
    print(f"  MOEMAIL_API_KEY: {'已设置' if os.getenv('MOEMAIL_API_KEY') else '未设置'}")
    
    # 执行测试
    results = []
    
    # 1. 检查API密钥
    results.append(("Firebase API密钥", check_firebase_key()))
    
    # 2. 直接测试Firebase API
    results.append(("直接Firebase API", test_direct_firebase_api()))
    
    # 3. 测试API池
    results.append(("API池", test_api_pool()))
    
    # 4. 测试完整注册
    results.append(("完整注册流程", test_complete_registration()))
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 诊断结果总结")
    print("=" * 80)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    # 建议
    print("\n💡 建议和解决方案:")
    print("=" * 80)
    
    if not any(result[1] for result in results):
        print("1. Firebase API请求全部失败")
        print("   - 检查API密钥是否有效")
        print("   - 检查网络连接")
        print("   - 考虑使用新的Firebase项目")
    
    if not results[1][1] and results[2][1]:
        print("2. 直接API失败但API池成功")
        print("   - API池可能有特殊的处理逻辑")
        print("   - 检查API池的实现")
    
    if not results[2][1] and not results[3][1]:
        print("3. 所有测试都失败")
        print("   - 检查配置文件加载")
        print("   - 检查Python环境")
        print("   - 重新安装依赖")

if __name__ == "__main__":
    main()