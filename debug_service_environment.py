#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试服务环境变量加载问题
"""

import os
import sys
import json
from datetime import datetime

def check_environment_loading():
    """检查环境变量加载"""
    
    print("🔍 检查环境变量加载")
    print("="*80)
    
    # 检查当前工作目录
    print(f"📁 当前工作目录: {os.getcwd()}")
    
    # 检查Python路径
    print(f"🐍 Python路径: {sys.path[:3]}...")
    
    # 检查环境变量文件
    env_files = [
        "config/production.env",
        "./config/production.env",
        "../config/production.env",
        "production.env",
        ".env"
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"✅ 找到环境文件: {env_file}")
            try:
                with open(env_file, 'r') as f:
                    lines = f.readlines()[:10]  # 只读取前10行
                    print(f"   文件内容预览:")
                    for line in lines:
                        print(f"     {line.strip()}")
            except Exception as e:
                print(f"   ❌ 读取文件失败: {e}")
        else:
            print(f"❌ 环境文件不存在: {env_file}")
    
    # 尝试加载环境变量
    print("\n🔧 尝试加载环境变量")
    
    try:
        from dotenv import load_dotenv
        result = load_dotenv('config/production.env')
        print(f"   load_dotenv结果: {result}")
    except ImportError:
        print("   ❌ dotenv模块未安装")
        return False
    except Exception as e:
        print(f"   ❌ 加载失败: {e}")
        return False
    
    # 检查关键环境变量
    print("\n🔑 检查关键环境变量")
    
    key_vars = [
        "FIREBASE_API_KEYS",
        "FIREBASE_PROJECT_ID",
        "FIREBASE_APP_ID",
        "FIREBASE_AUTH_URL",
        "IDENTITY_TOOLKIT_BASE",
        "MOEMAIL_URL",
        "MOEMAIL_API_KEY"
    ]
    
    loaded_count = 0
    for var in key_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value[:30]}..." if len(value) > 30 else f"   ✅ {var}: {value}")
            loaded_count += 1
        else:
            print(f"   ❌ {var}: 未设置")
    
    print(f"\n📊 环境变量加载结果: {loaded_count}/{len(key_vars)} 成功")
    
    return loaded_count > 0

def check_service_module_loading():
    """检查服务模块加载"""
    
    print("\n🔍 检查服务模块加载")
    print("="*80)
    
    # 尝试导入服务模块
    modules = [
        "account_pool.firebase_api_pool",
        "account_pool.complete_registration",
        "account_pool.simple_config",
        "account_pool.config_manager"
    ]
    
    loaded_modules = []
    
    for module in modules:
        try:
            # 尝试导入模块
            if module in sys.modules:
                print(f"   ✅ {module}: 已加载")
                loaded_modules.append(module)
            else:
                # 尝试导入
                __import__(module)
                print(f"   ✅ {module}: 导入成功")
                loaded_modules.append(module)
        except ImportError as e:
            print(f"   ❌ {module}: 导入失败 - {e}")
        except Exception as e:
            print(f"   ❌ {module}: 其他错误 - {e}")
    
    # 检查模块中的函数
    if "account_pool.firebase_api_pool" in loaded_modules:
        print("\n🔧 检查firebase_api_pool模块")
        try:
            from account_pool.firebase_api_pool import get_firebase_pool, make_firebase_request
            print("   ✅ get_firebase_pool函数: 可用")
            print("   ✅ make_firebase_request函数: 可用")
            
            # 尝试获取池实例
            pool = get_firebase_pool()
            print(f"   ✅ Firebase池实例: 已创建")
            
            # 检查池状态
            status = pool.get_pool_status()
            print(f"   📊 池状态: {status['total_keys']} 个密钥")
            
        except Exception as e:
            print(f"   ❌ 检查失败: {e}")
    
    if "account_pool.complete_registration" in loaded_modules:
        print("\n🔧 检查complete_registration模块")
        try:
            from account_pool.complete_registration import CompleteScriptRegistration
            print("   ✅ CompleteScriptRegistration类: 可用")
            
            # 尝试创建实例
            registrar = CompleteScriptRegistration()
            print("   ✅ 注册器实例: 已创建")
            
        except Exception as e:
            print(f"   ❌ 检查失败: {e}")
    
    return len(loaded_modules) > 0

def simulate_service_request():
    """模拟服务请求"""
    
    print("\n🔍 模拟服务请求")
    print("="*80)
    
    try:
        # 确保环境变量已加载
        from dotenv import load_dotenv
        load_dotenv('config/production.env')
        
        # 导入服务模块
        from account_pool.firebase_api_pool import make_firebase_request
        
        # 模拟请求
        print("📡 模拟Firebase请求")
        
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
            'x-firebase-gmpid': os.getenv("FIREBASE_APP_ID", "1:13153726198:web:1cc16bca7287752f8e06d7")
        }
        
        print(f"   URL: {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        print(f"   Headers: {json.dumps(headers, indent=2)}")
        
        # 发起请求
        response = make_firebase_request(url, "POST", payload, headers, max_retries=1)
        
        print(f"\n   响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 请求成功!")
            response_data = response.json()
            print(f"   响应数据: {json.dumps(response_data, indent=6)}")
            return True
        else:
            print("   ❌ 请求失败!")
            try:
                error_data = response.json()
                print(f"   错误信息: {json.dumps(error_data, indent=6)}")
            except:
                print(f"   错误文本: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 模拟失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_running_service():
    """检查运行中的服务"""
    
    print("\n🔍 检查运行中的服务")
    print("="*80)
    
    # 检查端口
    import socket
    
    ports = [8019, 8000, 8080]
    
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        if result == 0:
            print(f"   ✅ 端口 {port}: 开放")
        else:
            print(f"   ❌ 端口 {port}: 关闭")
        sock.close()
    
    # 检查服务健康状态
    print("\n🏥 检查服务健康状态")
    
    import requests
    
    health_endpoints = [
        ("账号池服务", "http://localhost:8019/health"),
        ("Warp2API服务", "http://localhost:8000/health"),
        ("OpenAI兼容服务", "http://localhost:8080/health")
    ]
    
    for name, url in health_endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name}: 健康")
            else:
                print(f"   ⚠️ {name}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: 不可用 - {e}")

def main():
    """主函数"""
    print("🚀 服务环境调试工具")
    print(f"⏰ 时间: {datetime.now().isoformat()}")
    
    # 检查环境变量加载
    env_success = check_environment_loading()
    
    # 检查服务模块加载
    module_success = check_service_module_loading()
    
    # 模拟服务请求
    request_success = simulate_service_request()
    
    # 检查运行中的服务
    check_running_service()
    
    print("\n" + "="*80)
    print("📋 调试总结")
    print("="*80)
    print(f"环境变量加载: {'✅ 成功' if env_success else '❌ 失败'}")
    print(f"服务模块加载: {'✅ 成功' if module_success else '❌ 失败'}")
    print(f"服务请求模拟: {'✅ 成功' if request_success else '❌ 失败'}")
    
    if env_success and module_success and request_success:
        print("\n✅ 所有检查都通过，服务环境正常")
        print("💡 如果服务中仍然失败，可能是:")
        print("   1. 服务启动时的环境变量不同")
        print("   2. 服务运行时的上下文差异")
        print("   3. 多进程/多线程环境变量共享问题")
        print("   4. 服务代码中的其他逻辑错误")
    else:
        print("\n❌ 部分检查失败，需要修复环境问题")
        if not env_success:
            print("💡 环境变量加载失败，请检查配置文件")
        if not module_success:
            print("💡 服务模块加载失败，请检查代码和依赖")
        if not request_success:
            print("💡 服务请求模拟失败，请检查API配置")

if __name__ == "__main__":
    main()