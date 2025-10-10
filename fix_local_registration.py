#!/usr/bin/env python3
"""
修复本地注册问题
"""

import os
import sys

def fix_firebase_pool():
    """修复Firebase API池的冷却时间问题"""
    print("🔧 修复Firebase API池...")
    
    # 修改firebase_api_pool.py，移除冷却时间
    file_path = "account-pool-service/account_pool/firebase_api_pool.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # 找到并替换冷却时间设置
    old_line = "                cooldown_minutes = self._get_cooldown_time(error_type)"
    new_line = "                cooldown_minutes = 0  # 修复：强制不进入冷却期"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print("✅ 已修复Firebase API池冷却时间")
    else:
        print("⚠️ 未找到需要修复的代码行")

def test_firebase_request():
    """测试Firebase请求"""
    print("\n🧪 测试Firebase请求...")
    
    sys.path.insert(0, 'account-pool-service')
    
    try:
        from account_pool.firebase_api_pool import make_firebase_request
        import json
        
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
            'x-firebase-gmpid': '1:13153726198:web:1cc16bca7287752f8e06d7'
        }
        
        response = make_firebase_request(url, "POST", payload, headers)
        
        if response.status_code == 200:
            print("✅ Firebase请求成功！")
            print(f"响应: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Firebase请求失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    print("=" * 80)
    print("🔧 本地注册问题修复工具")
    print("=" * 80)
    
    # 1. 修复Firebase池
    fix_firebase_pool()
    
    # 2. 测试请求
    success = test_firebase_request()
    
    # 3. 给出建议
    print("\n" + "=" * 80)
    print("💡 修复建议")
    print("=" * 80)
    
    if success:
        print("✅ Firebase API已修复")
        print("\n📝 后续步骤：")
        print("1. 停止当前运行的账号池服务：")
        print("   ./stop_production.sh")
        print("\n2. 重新启动服务：")
        print("   ./start_production.sh")
        print("\n3. 查看注册日志：")
        print("   tail -f logs/pool-service.log")
    else:
        print("❌ 修复失败，请检查：")
        print("1. Firebase API密钥是否有效")
        print("2. 网络连接是否正常")
        print("3. 配置文件是否正确加载")

if __name__ == "__main__":
    main()