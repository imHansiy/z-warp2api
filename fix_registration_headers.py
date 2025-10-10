#!/usr/bin/env python3
"""
修复注册服务的headers问题
"""

import re

def fix_send_email_signin_request():
    """修复send_email_signin_request方法"""
    file_path = "account-pool-service/account_pool/complete_registration.py"
    
    print("🔧 修复send_email_signin_request方法...")
    
    try:
        # 读取文件
        with open(file_path, 'r') as f:
            content = f.read()
        
        # 找替换第239-240行
        pattern = r'(^\s*)# 使用Firebase API密钥池发起请求(\s*)response = make_firebase_request\(url, "POST", payload, max_retries=3\)$'
        
        replacement = '''# 使用Firebase API密钥池发起请求，传递自定义headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) AppleWebKit/537.36'),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': self.session.headers.get('Accept-Language', 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'),
                'Accept-Encoding': self.session.headers.get('Accept-Encoding', 'gzip, deflate'),
                'Connection': self.session.headers.get('Connection', 'keep-alive'),
                'Cache-Control': 'no-cache',
                'Origin': self.session.headers.get('Origin', 'https://app.warp.dev'),
                'Referer': self.session.headers.get('Referer', 'https://app.warp.dev/'),
                'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web',
                'x-firebase-gmpid': '1:13153726198:web:1cc16bca7287752f8e06d7'
            }
            response = make_firebase_request(url, "POST", payload, headers, max_retries=3)'''
        
        # 写回文件
        with open(file_path, 'w') as f:
            f.write(content)
        
        print("✅ 修复完成！")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def fix_complete_email_signin():
    """修复complete_email_signin方法"""
    file_path = "account-pool-service/account_pool/complete_registration.py"
    
    print("🔧 修复complete_email_signin方法...")
    
    try:
        # 读取文件
        with open(file_path, 'r') as f:
            content = f.read()
        
        # 找替换第340-343行
        pattern = r'(^\s*)# 使用Firebase API密钥池发起请求(\s*)response = make_firebase_request\(url, "POST", payload, max_retries=3\)$'
        
        replacement = '''# 使用Firebase API密钥池发起请求，传递自定义headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) AppleWebKit/537.36'),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': self.session.headers.get('Accept-Language', 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'),
                'Accept-Encoding': self.session.headers.get('Accept-Encoding', 'gzip, deflate'),
                'Connection': self.session.headers.get('Connection', 'keep-alive'),
                'Cache-Control': 'no-cache',
                'Origin': self.session.headers.get('Origin', 'https://app.warp.dev'),
                'Referer': self.session.headers.get('Referer', 'https://app.warp.dev/'),
                'x-client-version': 'Chrome/Client/JsCore/11.10.0/FirebaseCore-web',
                'x-firebase-gmpid': '1:13153726198:web:1cc16bca7287752f8e06d7'
            }
            response = make_firebase_request(url, "POST", payload, headers, max_retries=3)'''
        
        # 写回文件
        with open(file_path, 'w') as f:
            f.write(content)
        
        print("✅ 修复完成！")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def main():
    print("=" * 80)
    print("🔧 修复注册服务headers问题")
    print("=" * 80)
    
    # 修复send_email_signin_request
    success1 = fix_send_email_signin_request()
    
    # 修复complete_email_signin
    success2 = fix_complete_email_signin()
    
    if success1 and success2:
        print("\n✅ 所有修复都成功了！")
        print("\n💡 现在可以重新测试注册功能：")
        print("1. 停止服务：./stop_production.sh")
        print("2. 重新启动：./start_production.sh")
        print("3. 查看日志：tail -f logs/pool-service.log")
    else:
        print("\n❌ 部分修复失败")
        print("\n请检查错误信息并手动修复")

if __name__ == "__main__":
    main()