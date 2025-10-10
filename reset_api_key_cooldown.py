#!/usr/bin/env python3
"""
重置Firebase API密钥的冷却状态
"""

import os
import sys

# 添加账号池服务路径
sys.path.insert(0, '/app/account-pool-service')

# 导入Firebase API池
from account_pool.firebase_api_pool import get_firebase_pool

def reset_cooldown_and_test():
    """重置冷却状态并测试"""
    print("=" * 80)
    print("🔍 重置Firebase API密钥冷却状态并测试")
    print("=" * 80)
    
    # 获取API密钥池
    pool = get_firebase_pool()
    
    # 显示当前状态
    print("\n📊 当前API密钥池状态:")
    status = pool.get_pool_status()
    for key_status in status['keys_status']:
        key_preview = key_status['key_preview']
        total_requests = key_status['total_requests']
        failed_requests = key_status['failed_requests']
        success_rate = key_status['success_rate']
        in_cooldown = key_status['in_cooldown']
        cooldown_until = key_status['cooldown_until']
        
        print(f"\n🔑 密钥: {key_preview}")
        print(f"   总请求: {total_requests}")
        print(f"   失败请求: {failed_requests}")
        print(f"   成功率: {success_rate}")
        print(f"   冷却中: {'是' if in_cooldown else '否'}")
        if cooldown_until:
            print(f"   冷却至: {cooldown_until}")
    
    # 重置所有密钥的冷却状态
    print(f"\n🔄 重置所有密钥的冷却状态...")
    with pool.lock:
        for key in pool.api_keys:
            pool.key_cooldowns[key] = None
            print(f"   ✅ 重置密钥: {key[:20]}...")
    
    # 测试API请求
    print(f"\n🧪 测试API请求...")
    import json
    
    url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
    payload = {
        "requestType": "EMAIL_SIGNIN",
        "email": f"test{int(time.time())}@example.com",
        "clientType": "CLIENT_TYPE_WEB",
        "continueUrl": "https://app.warp.dev/login",
        "canHandleCodeInApp": True
    }
    
    try:
        response = pool.make_firebase_request(url, "POST", payload)
        
        if response.status_code == 200:
            print("✅ API请求成功！")
            response_data = response.json()
            print(f"📋 响应: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ API请求失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 错误: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📋 错误文本: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ API请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import time
    
    print("🐳 Docker容器内API密钥冷却状态重置")
    print(f"📍 当前工作目录: {os.getcwd()}")
    print(f"⏰ 当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 重置并测试
    success = reset_cooldown_and_test()
    
    if success:
        print(f"\n✅ 成功！API密钥已恢复正常工作状态")
        print("💡 建议: 现在可以重新运行账号注册流程")
    else:
        print(f"\n❌ 仍然失败，可能需要检查其他因素")
        print("💡 建议: 检查网络连接、API密钥有效性或其他配置")