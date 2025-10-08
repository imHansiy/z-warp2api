#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证硬编码参数是否已成功提取到配置文件
"""

import os
import re
from pathlib import Path

def check_file_for_hardcoded_params(file_path, patterns):
    """检查文件中是否还有硬编码参数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        issues = []
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                issues.append({
                    'pattern': pattern_name,
                    'matches': matches[:3]  # 只显示前3个匹配
                })
        
        return issues
    except Exception as e:
        return [{'error': str(e)}]

def main():
    """主函数"""
    print("=" * 60)
    print("验证硬编码参数提取情况")
    print("=" * 60)
    
    # 定义要检查的硬编码模式
    patterns_to_check = {
        '硬编码端口号': r':\s*(8000|8019|8080|9090)(?!\w)',
        '硬编码URL': r'https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})+(?:/[^\s"]*)?',
        '硬编码API密钥': r'AIzaSy[A-Za-z0-9_-]{33}',
        '硬编码User-Agent': r'Mozilla/5\.0[^"\']*',
        '硬编码超时时间': r'timeout\s*=\s*\d+',
        '硬编码分钟数': r'minutes\s*=\s*\d+',
        '硬编码秒数': r'seconds\s*=\s*\d+',
    }
    
    # 要检查的文件列表
    files_to_check = [
        'account-pool-service/config.py',
        'account-pool-service/main.py',
        'account-pool-service/account_pool/firebase_api_pool.py',
        'account-pool-service/account_pool/moemail_client.py',
        'account-pool-service/account_pool/proxy_manager.py',
        'account-pool-service/account_pool/pool_manager.py',
        'warp2api-main/server.py',
        'warp2api-main/start.py',
        'warp2api-main/warp2protobuf/core/auth.py',
        'warp2api-main/warp2protobuf/warp/api_client.py',
        'warp2api-main/protobuf2openai/config.py',
    ]
    
    # 检查配置文件是否存在
    config_file = Path('config/production.env')
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        return
    
    print(f"✅ 配置文件存在: {config_file}")
    
    # 检查配置文件中是否包含新增的配置项
    with open(config_file, 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    new_config_items = [
        'POOL_SERVICE_HOST',
        'BATCH_REGISTER_SIZE',
        'WARP_URL',
        'WARP_JWT',
        'FIREBASE_DEFAULT_API_KEY',
        'PROXY_TEST_URL',
        'USER_AGENT_1',
        'MOEMAIL_DOMAIN',
        'SESSION_TIMEOUT_MINUTES',
        'HTTP_KEEPALIVE',
    ]
    
    print("\n检查新增配置项:")
    for item in new_config_items:
        if item in config_content:
            print(f"✅ {item}")
        else:
            print(f"❌ {item} - 未找到")
    
    # 检查文件中的硬编码参数
    print("\n检查文件中的硬编码参数:")
    total_issues = 0
    
    for file_path in files_to_check:
        if not Path(file_path).exists():
            print(f"⚠️ 文件不存在: {file_path}")
            continue
            
        issues = check_file_for_hardcoded_params(file_path, patterns_to_check)
        
        if issues:
            print(f"\n📁 {file_path}:")
            for issue in issues:
                if 'error' in issue:
                    print(f"  ❌ 错误: {issue['error']}")
                else:
                    print(f"  ⚠️ 发现硬编码参数 ({issue['pattern']}):")
                    for match in issue['matches']:
                        print(f"    - {match}")
                    total_issues += 1
        else:
            print(f"✅ {file_path} - 未发现硬编码参数")
    
    print("\n" + "=" * 60)
    if total_issues == 0:
        print("✅ 所有检查通过！硬编码参数已成功提取到配置文件。")
    else:
        print(f"⚠️ 发现 {total_issues} 个潜在问题，请检查上述文件。")
    print("=" * 60)

if __name__ == "__main__":
    main()