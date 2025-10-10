#!/usr/bin/env python3
"""
最终验证脚本 - 测试所有修复的功能
"""

import os
import sys
import json
import time
import requests

def test_hardcoded_params():
    """测试硬编码参数是否已提取到配置文件"""
    print("=" * 80)
    print("1. 测试硬编码参数提取")
    print("=" * 80)
    
    # 检查config/production.env是否存在
    config_file = "/app/config/production.env"
    if os.path.exists(config_file):
        print("✅ config/production.env 存在")
        
        # 读取配置文件
        with open(config_file, 'r') as f:
            content = f.read()
        
        # 检查关键配置项
        required_configs = [
            "FIREBASE_API_KEYS",
            "MOEMAIL_URL",
            "MOEMAIL_API_KEY",
            "WARP_BASE_URL",
            "IDENTITY_TOOLKIT_BASE"
        ]
        
        missing_configs = []
        for config in required_configs:
            if config not in content:
                missing_configs.append(config)
        
        if missing_configs:
            print(f"⚠️ 缺少配置项: {', '.join(missing_configs)}")
            return False
        else:
            print("✅ 所有必需的配置项都存在")
            return True
    else:
        print("❌ config/production.env 不存在")
        return False

def test_firebase_api():
    """测试Firebase API是否正常工作"""
    print("\n" + "=" * 80)
    print("2. 测试Firebase API")
    print("=" * 80)
    
    # 添加账号池服务路径
    sys.path.insert(0, '/app/account-pool-service')
    
    try:
        from account_pool.firebase_api_pool import make_firebase_request
        
        url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        payload = {
            "requestType": "EMAIL_SIGNIN",
            "email": f"test{int(time.time())}@example.com",
            "clientType": "CLIENT_TYPE_WEB",
            "continueUrl": "https://app.warp.dev/login",
            "canHandleCodeInApp": True
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
            'x-firebase-gmpid': '1:13153726198:web:1cc16bca7287752f8e06d7'
        }
        
        response = make_firebase_request(url, "POST", payload, headers)
        
        if response.status_code == 200:
            print("✅ Firebase API请求成功")
            return True
        else:
            print(f"❌ Firebase API请求失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误: {error_data.get('error', {}).get('message', 'Unknown')}")
            except:
                pass
            return False
            
    except Exception as e:
        print(f"❌ Firebase API测试异常: {e}")
        return False

def test_services():
    """测试所有服务是否正常运行"""
    print("\n" + "=" * 80)
    print("3. 测试服务状态")
    print("=" * 80)
    
    services = {
        "账号池服务": "http://localhost:8019/health",
        "Warp2API服务": "http://localhost:8000/healthz",
        "OpenAI兼容服务": "http://localhost:8080/health"
    }
    
    all_ok = True
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}正常运行")
            else:
                print(f"⚠️ {name}响应异常: {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {name}无法访问: {e}")
            all_ok = False
    
    return all_ok

def test_docker_container():
    """测试Docker容器状态"""
    print("\n" + "=" * 80)
    print("4. 测试Docker容器状态")
    print("=" * 80)
    
    # 检查容器是否在运行
    container_name = "warp2api-production"
    
    try:
        # 使用docker ps检查容器
        import subprocess
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True
        )
        
        if container_name in result.stdout:
            print("✅ Docker容器正在运行")
            
            # 检查容器健康状态
            if "healthy" in result.stdout:
                print("✅ 容器健康状态良好")
                return True
            else:
                print("⚠️ 容器健康状态可能有问题")
                return False
        else:
            print("❌ Docker容器未运行")
            return False
            
    except Exception as e:
        print(f"❌ 检查Docker容器失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 最终验证脚本")
    print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行所有测试
    results = {
        "硬编码参数提取": test_hardcoded_params(),
        "Firebase API": test_firebase_api(),
        "服务状态": test_services(),
        "Docker容器": test_docker_container()
    }
    
    # 总结结果
    print("\n" + "=" * 80)
    print("📊 验证结果总结")
    print("=" * 80)
    
    success_count = 0
    total_count = len(results)
    
    for test_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n📈 总体通过率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("\n🎉 所有测试都通过了！")
        print("✅ 硬编码参数已成功提取到config/production.env")
        print("✅ Firebase API正常工作")
        print("✅ 所有服务正常运行")
        print("✅ Docker容器状态良好")
        print("\n💡 项目已成功部署并运行！")
    else:
        print("\n⚠️ 部分测试失败")
        failed_tests = [name for name, success in results.items() if not success]
        print(f"失败的测试: {', '.join(failed_tests)}")
        print("\n💡 请检查失败的测试项目并进行相应修复")

if __name__ == "__main__":
    main()