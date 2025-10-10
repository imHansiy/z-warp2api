#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试服务配置问题
"""

import os
import sys
import json

def debug_config_loading():
    """调试配置加载"""
    print("🔍 调试配置加载...")
    
    # 尝试从不同路径导入配置
    paths_to_try = [
        "./account-pool-service",
        "./account-pool-service/account_pool",
        "."
    ]
    
    for path in paths_to_try:
        print(f"\n尝试路径: {path}")
        if path not in sys.path:
            sys.path.insert(0, path)
        
        try:
            # 尝试导入simple_config
            print("  尝试导入simple_config...")
            from simple_config import load_config
            config = load_config()
            print(f"  ✅ 成功导入simple_config，配置类型: {type(config)}")
            
            if config:
                print(f"  配置内容: {json.dumps(config, indent=2, ensure_ascii=False)[:500]}...")
                
                # 检查Firebase API密钥
                api_key = config.get('firebase_api_key')
                if api_key:
                    print(f"  🔑 找到Firebase API密钥: {api_key[:20]}...")
                else:
                    print("  ❌ 未找到firebase_api_key")
                
                return config
            else:
                print("  ❌ 配置为空")
                
        except ImportError as e:
            print(f"  ❌ 导入simple_config失败: {e}")
            
            try:
                # 尝试导入config_manager
                print("  尝试导入config_manager...")
                from config_manager import load_config
                config = load_config()
                print(f"  ✅ 成功导入config_manager，配置类型: {type(config)}")
                
                if config:
                    print(f"  配置内容: {json.dumps(config, indent=2, ensure_ascii=False)[:500]}...")
                    
                    # 检查Firebase API密钥
                    api_key = config.get('firebase_api_key')
                    if api_key:
                        print(f"  🔑 找到Firebase API密钥: {api_key[:20]}...")
                    else:
                        print("  ❌ 未找到firebase_api_key")
                    
                    return config
                else:
                    print("  ❌ 配置为空")
                    
            except ImportError as e2:
                print(f"  ❌ 导入config_manager失败: {e2}")
                
                try:
                    # 尝试导入src.modules.config_manager
                    print("  尝试导入src.modules.config_manager...")
                    from src.modules.config_manager import load_config
                    config = load_config()
                    print(f"  ✅ 成功导入src.modules.config_manager，配置类型: {type(config)}")
                    
                    if config:
                        print(f"  配置内容: {json.dumps(config, indent=2, ensure_ascii=False)[:500]}...")
                        
                        # 检查Firebase API密钥
                        api_key = config.get('firebase_api_key')
                        if api_key:
                            print(f"  🔑 找到Firebase API密钥: {api_key[:20]}...")
                        else:
                            print("  ❌ 未找到firebase_api_key")
                        
                        return config
                    else:
                        print("  ❌ 配置为空")
                        
                except ImportError as e3:
                    print(f"  ❌ 导入src.modules.config_manager失败: {e3}")
        
        except Exception as e:
            print(f"  ❌ 加载配置异常: {e}")
    
    print("\n🔍 所有导入尝试失败，尝试直接从环境变量读取...")
    
    # 尝试从环境变量读取
    firebase_keys = os.getenv("FIREBASE_API_KEYS")
    if firebase_keys:
        print(f"  🔑 从环境变量找到FIREBASE_API_KEYS: {firebase_keys[:20]}...")
        config = {'firebase_api_keys': [key.strip() for key in firebase_keys.split(",") if key.strip()]}
        return config
    else:
        print("  ❌ 环境变量中未找到FIREBASE_API_KEYS")
    
    # 使用默认配置
    print("  🔧 使用默认配置...")
    default_key = "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"
    config = {'firebase_api_key': default_key}
    print(f"  🔑 使用默认API密钥: {default_key[:20]}...")
    return config

def debug_firebase_pool():
    """调试Firebase API池"""
    print("\n🔍 调试Firebase API池...")
    
    # 尝试导入firebase_api_pool
    paths_to_try = [
        "./account-pool-service",
        "./account-pool-service/account_pool",
        "."
    ]
    
    for path in paths_to_try:
        print(f"\n尝试路径: {path}")
        if path not in sys.path:
            sys.path.insert(0, path)
        
        try:
            print("  尝试导入firebase_api_pool...")
            from firebase_api_pool import get_firebase_pool, make_firebase_request
            
            print("  ✅ 成功导入firebase_api_pool")
            
            # 尝试获取池实例
            print("  尝试获取Firebase池实例...")
            pool = get_firebase_pool()
            print(f"  ✅ 成功获取池实例: {type(pool)}")
            
            # 获取池状态
            print("  获取池状态...")
            status = pool.get_pool_status()
            print(f"  池状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
            
            # 尝试获取API密钥
            print("  尝试获取API密钥...")
            api_key = pool.get_next_api_key()
            print(f"  🔑 获取到API密钥: {api_key[:20]}...")
            
            return pool
            
        except ImportError as e:
            print(f"  ❌ 导入firebase_api_pool失败: {e}")
        except Exception as e:
            print(f"  ❌ 获取Firebase池异常: {e}")
    
    return None

def test_service_call_with_pool(pool):
    """使用池测试服务调用"""
    print("\n🔍 使用池测试服务调用...")
    
    if not pool:
        print("  ❌ 池为空，无法测试")
        return False
    
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
    
    print(f"  URL: {url}")
    print(f"  Headers: {json.dumps(headers, indent=2)}")
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    try:
        print("  发起请求...")
        response = pool.make_firebase_request(url, "POST", payload, headers, max_retries=3)
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("  ✅ 池API调用成功")
            data = response.json()
            print(f"  响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print("  ❌ 池API调用失败")
            print(f"  错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ 池API调用异常: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("服务配置调试工具")
    print("=" * 80)
    
    # 调试配置加载
    config = debug_config_loading()
    
    # 调试Firebase池
    pool = debug_firebase_pool()
    
    # 测试服务调用
    if pool:
        test_service_call_with_pool(pool)
    
    print("\n" + "=" * 80)
    print("调试完成")
    print("=" * 80)