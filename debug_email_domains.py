#!/usr/bin/env python3
"""
测试不同邮箱域名的Firebase API请求
"""

import os
import sys
import json
import requests

# 添加账号池服务路径
sys.path.insert(0, '/app/account-pool-service')

# 导入Firebase API池
from account_pool.firebase_api_pool import make_firebase_request

def test_email_domains():
    """测试不同邮箱域名的Firebase API请求"""
    print("=" * 80)
    print("🔍 测试不同邮箱域名的Firebase API请求")
    print("=" * 80)
    
    # 测试不同类型的邮箱地址
    test_emails = [
        "test@example.com",           # 通用测试邮箱
        "user@gmail.com",             # Gmail
        "user@yahoo.com",             # Yahoo
        "test@outlook.com",           # Outlook
        "random123@007666.xyz",       # 项目使用的域名
        "test@test.com",              # 通用测试域名
    ]
    
    # 自定义headers
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
    
    results = []
    
    for email in test_emails:
        print(f"\n{'='*60}")
        print(f"📧 测试邮箱: {email}")
        print(f"{'='*60}")
        
        url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        
        payload = {
            "requestType": "EMAIL_SIGNIN",
            "email": email,
            "clientType": "CLIENT_TYPE_WEB",
            "continueUrl": "https://app.warp.dev/login",
            "canHandleCodeInApp": True
        }
        
        try:
            response = make_firebase_request(url, "POST", payload, custom_headers)
            
            print(f"📥 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 请求成功")
                response_data = response.json()
                print(f"📋 响应: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                results.append({"email": email, "status": "success", "error": None})
            else:
                print("❌ 请求失败")
                try:
                    error_data = response.json()
                    print(f"📋 错误响应: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                except:
                    error_message = response.text[:200]
                results.append({"email": email, "status": "failed", "error": error_message})
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            results.append({"email": email, "status": "error", "error": str(e)})
    
    # 总结结果
    print(f"\n{'='*80}")
    print("📊 测试结果总结")
    print(f"{'='*80}")
    
    success_count = 0
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {result['email']}: {result['status']}")
        if result["error"]:
            print(f"   错误: {result['error']}")
        if result["status"] == "success":
            success_count += 1
    
    print(f"\n📈 成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    # 分析失败的邮箱
    failed_emails = [r for r in results if r["status"] != "success"]
    if failed_emails:
        print(f"\n⚠️ 失败的邮箱:")
        for result in failed_emails:
            print(f"  - {result['email']}: {result['error']}")
            
        # 检查是否所有007666.xyz域名都失败
        xyz_failures = [r for r in failed_emails if "007666.xyz" in r["email"]]
        if xyz_failures:
            print(f"\n🔍 发现问题: 所有007666.xyz域名的邮箱都失败了")
            print("   建议: 使用其他邮箱域名或联系Firebase支持")
    
    return results

def test_without_special_headers():
    """测试不使用特殊headers的请求"""
    print(f"\n{'='*80}")
    print("🔍 测试不使用特殊headers的请求")
    print(f"{'='*80}")
    
    url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
    
    payload = {
        "requestType": "EMAIL_SIGNIN",
        "email": "test@example.com",
        "clientType": "CLIENT_TYPE_WEB",
        "continueUrl": "https://app.warp.dev/login",
        "canHandleCodeInApp": True
    }
    
    # 使用基本的headers
    basic_headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        print("📤 发送请求（仅使用基本headers）...")
        response = make_firebase_request(url, "POST", payload, basic_headers)
        
        print(f"📥 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 请求成功")
            response_data = response.json()
            print(f"📋 响应: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print("❌ 请求失败")
            try:
                error_data = response.json()
                print(f"📋 错误响应: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📋 错误文本: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🐳 Docker容器内邮箱域名测试")
    print(f"📍 当前工作目录: {os.getcwd()}")
    
    # 测试1: 不同邮箱域名
    print("\n" + "=" * 80)
    print("测试1: 不同邮箱域名")
    results = test_email_domains()
    
    # 测试2: 不使用特殊headers
    print("\n" + "=" * 80)
    print("测试2: 不使用特殊headers")
    success_without_headers = test_without_special_headers()
    
    # 最终建议
    print(f"\n{'='*80}")
    print("💡 建议和结论")
    print(f"{'='*80}")
    
    if any("007666.xyz" in r["email"] and r["status"] == "success" for r in results):
        print("✅ 007666.xyz域名可以正常使用")
    else:
        print("⚠️ 007666.xyz域名可能被Firebase限制")
        print("   建议: 使用其他邮箱域名（如gmail.com、outlook.com等）")
    
    if success_without_headers:
        print("✅ 即使不使用特殊headers也能成功")
        print("   问题可能不在于headers缺失")
    else:
        print("⚠️ 不使用特殊headers时请求失败")
        print("   建议保留Firebase必要的headers")