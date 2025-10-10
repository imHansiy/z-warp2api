#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复服务环境变量加载问题
确保服务正确加载config/production.env中的配置
"""

import os
import sys

def fix_env_loading():
    """修复环境变量加载"""
    print("🔍 修复服务环境变量加载...")
    
    # 检查当前环境变量
    print("\n📋 检查当前环境变量...")
    firebase_keys = os.getenv("FIREBASE_API_KEYS")
    print(f"FIREBASE_API_KEYS: {firebase_keys}")
    
    if not firebase_keys:
        print("❌ FIREBASE_API_KEYS未设置，尝试从config/production.env加载...")
        
        # 尝试加载config/production.env
        env_file = "./config/production.env"
        if os.path.exists(env_file):
            print(f"✅ 找到配置文件: {env_file}")
            
            # 读取并解析环境变量
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 移除引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # 设置环境变量
                        os.environ[key] = value
                        
                        if key == "FIREBASE_API_KEYS":
                            print(f"✅ 设置FIREBASE_API_KEYS: {value[:20]}...")
            
            # 再次检查
            firebase_keys = os.getenv("FIREBASE_API_KEYS")
            if firebase_keys:
                print("✅ FIREBASE_API_KEYS已成功设置")
            else:
                print("❌ 仍然无法设置FIREBASE_API_KEYS")
        else:
            print(f"❌ 配置文件不存在: {env_file}")
    
    # 测试配置加载
    print("\n📋 测试配置加载...")
    try:
        # 添加路径
        sys.path.insert(0, './account-pool-service/account_pool')
        
        from simple_config import load_config
        config = load_config()
        
        print("✅ 配置加载成功")
        
        # 检查Firebase API密钥
        api_keys = config.get('firebase_api_keys', [])
        api_key = config.get('firebase_api_key')
        
        print(f"firebase_api_keys: {api_keys}")
        print(f"firebase_api_key: {api_key}")
        
        if api_key:
            print(f"✅ Firebase API密钥已加载: {api_key[:20]}...")
            return True
        else:
            print("❌ Firebase API密钥未加载")
            return False
            
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def create_fixed_start_script():
    """创建修复的启动脚本"""
    print("\n🔧 创建修复的启动脚本...")
    
    script_content = """#!/bin/bash
# 修复的账号池服务启动脚本
# 确保正确加载环境变量

echo "🔍 启动账号池服务（修复版）..."

# 设置工作目录
cd "$(dirname "$0")"

# 加载环境变量
if [ -f "./config/production.env" ]; then
    echo "📋 加载环境变量..."
    export $(grep -v '^#' ./config/production.env | xargs)
    echo "✅ 环境变量加载完成"
else
    echo "❌ 配置文件不存在: ./config/production.env"
    exit 1
fi

# 检查关键环境变量
if [ -z "$FIREBASE_API_KEYS" ]; then
    echo "❌ FIREBASE_API_KEYS未设置"
    exit 1
fi

echo "🔑 Firebase API密钥: ${FIREBASE_API_KEYS:0:20}..."

# 启动服务
cd account-pool-service
python main.py
"""
    
    with open("start_pool_service_fixed.sh", "w") as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod("start_pool_service_fixed.sh", 0o755)
    print("✅ 修复的启动脚本已创建: start_pool_service_fixed.sh")

def update_main_script():
    """更新主脚本以确保环境变量加载"""
    print("\n🔧 更新主脚本...")
    
    main_script_path = "./account-pool-service/main.py"
    
    if os.path.exists(main_script_path):
        # 读取原始脚本
        with open(main_script_path, 'r') as f:
            content = f.read()
        
        # 检查是否已经有环境变量加载代码
        if "load_dotenv" not in content and "production.env" not in content:
            # 在文件开头添加环境变量加载代码
            env_loading_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# 加载环境变量
def load_env_file(env_file):
    \"\"\"加载.env文件\"\"\"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 移除引号
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    os.environ[key] = value

# 加载环境变量
load_env_file('../config/production.env')

"""
            
            # 找到原始代码的开始位置
            lines = content.split('\n')
            start_index = 0
            for i, line in enumerate(lines):
                if line.startswith('#!/usr/bin/env python3') or line.startswith('# -*- coding:'):
                    start_index = i + 1
                    break
            
            # 插入环境变量加载代码
            lines = lines[:start_index] + env_loading_code.split('\n') + lines[start_index:]
            
            # 写回文件
            with open(main_script_path, 'w') as f:
                f.write('\n'.join(lines))
            
            print("✅ 主脚本已更新")
        else:
            print("✅ 主脚本已经包含环境变量加载代码")
    else:
        print(f"❌ 主脚本不存在: {main_script_path}")

if __name__ == "__main__":
    print("=" * 80)
    print("服务环境变量加载修复工具")
    print("=" * 80)
    
    # 修复环境变量加载
    success = fix_env_loading()
    
    # 创建修复的启动脚本
    create_fixed_start_script()
    
    # 更新主脚本
    update_main_script()
    
    if success:
        print("\n✅ 环境变量加载修复成功")
        print("可以尝试使用以下命令启动服务:")
        print("1. ./start_pool_service_fixed.sh")
        print("2. cd account-pool-service && python main.py")
    else:
        print("\n❌ 环境变量加载修复失败")
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)