#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的脚本注册流程
包括验证链接的处理和最终的token获取
"""

import os
import json
import time
import requests
import re
import html
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

# 修复导入路径
try:
    from moemail_client import MoeMailClient
    from firebase_api_pool import FirebaseAPIPool, make_firebase_request, get_firebase_pool
    from simple_domain_selector import get_random_email_domain
except ImportError:
    from .moemail_client import MoeMailClient
    from .firebase_api_pool import FirebaseAPIPool, make_firebase_request, get_firebase_pool
    from .simple_domain_selector import get_random_email_domain

class CompleteScriptRegistration:
    """完整脚本注册器"""
    
    def __init__(self):
        """初始化注册器"""
        print("🤖 初始化完整脚本注册器...")
        
        # 从配置服务加载配置
        try:
            from simple_config import load_config
        except ImportError:
            try:
                from config_manager import load_config
            except ImportError:
                from src.modules.config_manager import load_config
        self.config = load_config()
        if not self.config:
            raise Exception("无法加载远程配置")
        
        # 初始化Firebase API密钥池
        self.firebase_pool = get_firebase_pool()

        # 保持向后兼容性
        self.firebase_api_key = self.config.get('firebase_api_key')

        self.moemail_client = MoeMailClient(
            self.config.get('moemail_url'),
            self.config.get('api_key')
        )

        # 设置请求会话
        self.session = requests.Session()
        # 使用动态生成的headers
        dynamic_headers = self._generate_random_headers()
        self.session.headers.update(dynamic_headers)

        print(f"🔧 使用动态User-Agent: {dynamic_headers['User-Agent'][:50]}...")
        
        print("✅ 完整脚本注册器初始化完成")

    def _generate_random_headers(self) -> Dict[str, str]:
        """生成随机浏览器headers"""
        import random

        # 随机Chrome版本 (120-131)
        chrome_major = random.randint(120, 131)
        chrome_minor = random.randint(0, 9)
        chrome_build = random.randint(6000, 6999)
        chrome_patch = random.randint(100, 999)
        chrome_version = f"{chrome_major}.{chrome_minor}.{chrome_build}.{chrome_patch}"

        # 随机WebKit版本
        webkit_version = f"537.{random.randint(30, 40)}"

        # 随机操作系统版本
        os_versions = [
            "10_15_7",  # macOS Big Sur
            "11_0_1",   # macOS Big Sur
            "12_0_1",   # macOS Monterey
            "13_0_1",   # macOS Ventura
            "14_0_0",   # macOS Sonoma
        ]
        os_version = random.choice(os_versions)

        # 随机语言偏好
        languages = [
            "en-US,en;q=0.9",
            "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "en-US,en;q=0.9,fr;q=0.8",
            "en-US,en;q=0.9,es;q=0.8",
            "en-US,en;q=0.9,de;q=0.8",
        ]
        accept_language = random.choice(languages)

        # 生成User-Agent
        user_agent = f"Mozilla/5.0 (Macintosh; Intel Mac OS X {os_version}) AppleWebKit/{webkit_version} (KHTML, like Gecko) Chrome/{chrome_version} Safari/{webkit_version}"

        return {
            'Content-Type': 'application/json',
            'User-Agent': user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': accept_language,
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Origin': os.getenv("WARP_BASE_URL", "https://app.warp.dev"),
            'Referer': os.getenv("WARP_BASE_URL", "https://app.warp.dev/") + "/",
            'Sec-Ch-Ua': f'"Chromium";v="{chrome_major}", "Google Chrome";v="{chrome_major}", "Not=A?Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web'
        }

    def _generate_random_email_prefix(self) -> str:
        """生成随机邮箱前缀"""
        import random
        import string

        # 随机单词列表
        words = [
            'alpha', 'beta', 'gamma', 'delta', 'omega', 'sigma', 'theta',
            'nova', 'star', 'moon', 'sun', 'sky', 'cloud', 'wind', 'fire',
            'water', 'earth', 'light', 'dark', 'swift', 'quick', 'fast',
            'blue', 'red', 'green', 'gold', 'silver', 'crystal', 'diamond',
            'magic', 'power', 'force', 'energy', 'spark', 'flash', 'bolt',
            'wave', 'flow', 'stream', 'river', 'ocean', 'lake', 'forest',
            'mountain', 'valley', 'peak', 'edge', 'core', 'prime', 'ultra',
            'mega', 'super', 'hyper', 'turbo', 'boost', 'rush', 'dash',
            'zoom', 'speed', 'rapid', 'sonic', 'echo', 'pulse', 'vibe'
        ]

        # 选择随机单词
        word = random.choice(words)

        # 生成随机字符串（6-8位）
        length = random.randint(6, 8)
        chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

        return f"{word}{chars}"

    def _generate_browser_headers(self) -> Dict[str, str]:
        """生成浏览器访问headers（用于模拟浏览器访问）"""
        import random

        # 随机Chrome版本
        chrome_major = random.randint(120, 131)
        chrome_minor = random.randint(0, 9)
        chrome_build = random.randint(6000, 6999)
        chrome_patch = random.randint(100, 999)
        chrome_version = f"{chrome_major}.{chrome_minor}.{chrome_build}.{chrome_patch}"

        # 随机WebKit版本
        webkit_version = f"537.{random.randint(30, 40)}"

        # 随机操作系统版本
        os_versions = [
            "10_15_7", "11_0_1", "12_0_1", "13_0_1", "14_0_0"
        ]
        os_version = random.choice(os_versions)

        # 随机语言偏好
        languages = [
            "en-US,en;q=0.9",
            "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "en-US,en;q=0.9,fr;q=0.8",
            "en-US,en;q=0.9,es;q=0.8"
        ]
        accept_language = random.choice(languages)

        user_agent = f"Mozilla/5.0 (Macintosh; Intel Mac OS X {os_version}) AppleWebKit/{webkit_version} (KHTML, like Gecko) Chrome/{chrome_version} Safari/{webkit_version}"

        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': accept_language,
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-Ch-Ua': f'"Chromium";v="{chrome_major}", "Google Chrome";v="{chrome_major}", "Not=A?Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"'
        }

    def create_temp_email(self, prefix: str = None) -> Optional[Dict[str, str]]:
        """创建临时邮箱"""
        try:
            if not prefix:
                # 生成随机前缀：随机单词 + 随机字符
                prefix = self._generate_random_email_prefix()

            # 使用简单随机域名选择器获取域名（第一次会获取配置，后续会复用缓存）
            random_domain = get_random_email_domain(self.moemail_client)
            
            # 从配置文件读取邮箱过期时间
            config = self.config  # 使用已加载的配置
            expiry_hours = config.get('email_expiry_hours', 1) if config else 1
            
            print(f"📧 创建临时邮箱: {prefix}@{random_domain} (过期: {expiry_hours}小时)")
            email = self.moemail_client.create_email(prefix, random_domain, expiry_hours)
            
            return {
                "address": email.address,
                "id": email.id,
                "prefix": prefix
            }
        except Exception as e:
            print(f"❌ 创建邮箱失败: {e}")
            return None
    
    def send_email_signin_request(self, email_address: str) -> Dict[str, Any]:
        """发送邮箱登录请求"""
        print(f"📤 发送邮箱登录请求: {email_address}")

        try:
            url = os.getenv("IDENTITY_TOOLKIT_BASE", "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode")

            payload = {
                "requestType": "EMAIL_SIGNIN",
                "email": email_address,
                "clientType": "CLIENT_TYPE_WEB",
                "continueUrl": os.getenv("WARP_BASE_URL", "https://app.warp.dev") + "/login",
                "canHandleCodeInApp": True
            }

            # 使用Firebase API密钥池发起请求，传递必要的headers
            headers = {
                'Content-Type': 'application/json',
                'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web'
            }
            response = make_firebase_request(url, "POST", payload, headers, max_retries=3)
            
            if response.status_code == 200:
                response_data = response.json()
                print("✅ 邮箱登录请求发送成功")
                return {
                    "success": True,
                    "response": response_data
                }
            else:
                error_text = response.text
                print(f"❌ 请求失败: {error_text}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_text
                }
                
        except Exception as e:
            print(f"❌ 发送请求异常: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def wait_for_verification_email(self, email_id: str, timeout: int = 120) -> Optional[Dict[str, Any]]:
        """等待验证邮件"""
        print(f"📬 等待验证邮件 (超时: {timeout}秒)...")
        
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < timeout:
            check_count += 1
            print(f"  第 {check_count} 次检查...")
            
            try:
                messages = self.moemail_client.get_messages(email_id)
                
                if messages:
                    for msg in messages:
                        if 'warp' in msg.subject.lower() or 'sign' in msg.subject.lower():
                            # 提取验证链接
                            link_pattern = r'href=["\']([^"\']+)["\']'
                            matches = re.findall(link_pattern, msg.html)
                            
                            verification_link = None
                            for link in matches:
                                if 'firebaseapp.com' in link and 'auth/action' in link:
                                    verification_link = html.unescape(link)
                                    break
                            
                            if verification_link:
                                print(f"✅ 找到验证邮件并提取链接")
                                return {
                                    "subject": msg.subject,
                                    "verification_link": verification_link,
                                    "received_at": msg.received_at
                                }
                
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ 检查邮件时出错: {e}")
                time.sleep(5)
        
        print("❌ 等待验证邮件超时")
        return None
    
    def process_verification_link(self, verification_link: str) -> Dict[str, Any]:
        """处理验证链接，提取参数"""
        print("🔍 处理验证链接...")
        
        try:
            parsed = urlparse(verification_link)
            params = parse_qs(parsed.query)
            
            result = {
                "api_key": params.get('apiKey', [None])[0],
                "mode": params.get('mode', [None])[0],
                "oob_code": params.get('oobCode', [None])[0],
                "continue_url": params.get('continueUrl', [None])[0],
                "lang": params.get('lang', [None])[0]
            }
            
            print(f"✅ 验证链接参数提取成功")
            print(f"  OOB Code: {result['oob_code'][:20]}..." if result['oob_code'] else "None")
            
            return result
            
        except Exception as e:
            print(f"❌ 处理验证链接失败: {e}")
            return {"error": str(e)}
    
    def complete_email_signin(self, email_address: str, oob_code: str) -> Dict[str, Any]:
        """完成邮箱登录流程"""
        print(f"🔐 完成邮箱登录: {email_address}")

        try:
            url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithEmailLink"

            payload = {
                "email": email_address,
                "oobCode": oob_code
            }
            
            print(f"  请求URL: {url}")
            print(f"  邮箱: {email_address}")
            print(f"  OOB Code: {oob_code[:20]}...")
            
            # 添加随机延迟模拟真实用户行为
            import time
            import random
            delay = random.uniform(1.5, 3.5)
            time.sleep(delay)

            # 使用Firebase API密钥池发起请求，传递必要的headers
            headers = {
                'Content-Type': 'application/json',
                'x-client-version': 'Chrome/JsCore/11.10.0/FirebaseCore-web'
            }
            response = make_firebase_request(url, "POST", payload, headers, max_retries=3)

            print(f"  响应状态码: {response.status_code}")

            if response.status_code == 200:
                response_data = response.json()
                print("✅ 邮箱登录完成")
                
                # 提取关键信息
                is_new_user = response_data.get("isNewUser", True)
                result = {
                    "success": True,
                    "id_token": response_data.get("idToken"),
                    "refresh_token": response_data.get("refreshToken"),
                    "expires_in": response_data.get("expiresIn"),
                    "local_id": response_data.get("localId"),
                    "email": response_data.get("email"),
                    "is_new_user": is_new_user,
                    "registered": not is_new_user,  # 兼容旧字段
                    "raw_response": response_data
                }

                print(f"  用户ID: {result['local_id']}")
                print(f"  邮箱: {result['email']}")
                print(f"  是否新用户: {result['is_new_user']}")
                print(f"  已注册: {result['registered']}")
                print(f"  Token过期时间: {result['expires_in']}秒")
                
                return result
            else:
                error_text = response.text
                print(f"❌ 登录失败: {error_text}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_text
                }
                
        except Exception as e:
            print(f"❌ 完成登录异常: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def simulate_browser_confirmation(self, email_address: str, oob_code: str) -> Dict[str, Any]:
        """模拟浏览器确认流程"""
        print("🌐 模拟浏览器确认流程...")

        try:
            # 模拟访问验证链接的浏览器行为
            # 获取当前可用的API密钥
            current_api_key = self.firebase_pool.get_next_api_key()
            verification_url = f"{os.getenv('FIREBASE_AUTH_URL', 'https://astral-field-294621.firebaseapp.com')}/__/auth/action?apiKey={current_api_key}&mode=signIn&oobCode={oob_code}&continueUrl={os.getenv('WARP_BASE_URL', 'https://app.warp.dev')}/login&lang=en"

            # 设置浏览器headers（动态生成）
            browser_headers = self._generate_browser_headers()

            browser_session = requests.Session()
            browser_session.headers.update(browser_headers)

            print(f"  访问验证链接: {verification_url[:80]}...")

            # 第一步：访问验证链接
            response1 = browser_session.get(verification_url, timeout=30, allow_redirects=True)
            print(f"  第一步响应: {response1.status_code}, 最终URL: {response1.url}")

            # 如果重定向到登录页面，模拟邮箱确认
            if f"{os.getenv('WARP_BASE_URL', 'https://app.warp.dev')}/login" in response1.url and "Re-enter your email" in response1.text:
                print("  检测到需要邮箱确认，模拟确认流程...")

                # 模拟邮箱确认请求
                confirm_url = f"{os.getenv('WARP_BASE_URL', 'https://app.warp.dev')}/api/auth/confirm"  # 假设的确认端点
                confirm_data = {
                    "email": email_address,
                    "oobCode": oob_code,
                    "apiKey": current_api_key
                }

                response2 = browser_session.post(confirm_url, json=confirm_data, timeout=30)
                print(f"  确认响应: {response2.status_code}")

                if response2.status_code == 200:
                    print("✅ 浏览器确认流程完成")
                    return {"success": True, "confirmed": True}
                else:
                    print("⚠️ 确认请求失败，但继续执行")
                    return {"success": True, "confirmed": False}
            else:
                print("✅ 验证链接直接成功，无需额外确认")
                return {"success": True, "confirmed": True}

        except Exception as e:
            print(f"⚠️ 浏览器确认模拟失败: {e}")
            return {"success": False, "error": str(e)}

    def run_complete_registration(self, custom_email: str = None) -> Dict[str, Any]:
        """运行完整的注册流程

        Args:
            custom_email: 可选的自定义邮箱地址，如果提供则使用此邮箱而不创建临时邮箱
        """
        print("🚀 开始完整的脚本注册流程")
        print("=" * 80)

        result = {
            "success": False,
            "email_info": {},
            "signin_result": {},
            "browser_confirmation": {},
            "final_tokens": {}
        }

        # 1. 获取邮箱地址（创建临时邮箱或使用自定义邮箱）
        if custom_email:
            print(f"\n步骤1: 使用自定义邮箱: {custom_email}")
            # 提取邮箱前缀和域名
            email_prefix = custom_email.split("@")[0]
            email_domain = custom_email.split("@")[1]

            # 尝试创建对应的邮箱以便接收邮件
            try:
                # 对于自定义邮箱，优先使用指定域名，如果失败则使用随机域名
                # 从配置文件读取邮箱过期时间
                try:
                    from simple_config import load_config
                except ImportError:
                    try:
                        from config_manager import load_config
                    except ImportError:
                        from src.modules.config_manager import load_config
                config = load_config()
                expiry_hours = config.get('email_expiry_hours', 1) if config else 1
                
                print(f"📧 创建邮箱接收器: {email_prefix}@{email_domain} (过期: {expiry_hours}小时)")
                try:
                    temp_email = self.moemail_client.create_email(email_prefix, email_domain, expiry_hours)
                except Exception as domain_error:
                    print(f"⚠️ 使用指定域名失败: {domain_error}")
                    # 使用随机域名作为备选（跳过配置更新，复用已缓存的域名）
                    fallback_domain = get_random_email_domain(self.moemail_client, skip_config_update=True)
                    print(f"🔄 使用备选域名: {email_prefix}@{fallback_domain} (过期: {expiry_hours}小时)")
                    temp_email = self.moemail_client.create_email(email_prefix, fallback_domain, expiry_hours)
                email_info = {
                    "address": custom_email,
                    "id": temp_email.id,
                    "prefix": email_prefix
                }
                print(f"✅ 邮箱接收器创建成功: {email_info['id']}")
            except Exception as e:
                print(f"⚠️ 创建邮箱接收器失败: {e}")
                # 如果创建失败，使用前缀作为ID
                email_info = {
                    "address": custom_email,
                    "id": email_prefix,
                    "prefix": email_prefix
                }
        else:
            print("\n步骤1: 创建临时邮箱")
            email_info = self.create_temp_email()

            if not email_info:
                result["error"] = "创建邮箱失败"
                return result

        result["email_info"] = email_info
        email_address = email_info["address"]

        # 2. 发送邮箱登录请求
        print("\n步骤2: 发送邮箱登录请求")
        request_result = self.send_email_signin_request(email_address)

        if not request_result["success"]:
            result["error"] = f"发送请求失败: {request_result.get('error')}"
            return result

        # 3. 等待验证邮件
        print("\n步骤3: 等待验证邮件")
        print(f"📧 等待邮箱 {email_address} 的验证邮件...")

        email_result = self.wait_for_verification_email(email_info["id"])

        if not email_result:
            result["error"] = "未收到验证邮件"
            return result

        # 4. 处理验证链接
        print("\n步骤4: 处理验证链接")
        link_params = self.process_verification_link(email_result["verification_link"])

        if "error" in link_params:
            result["error"] = f"处理验证链接失败: {link_params['error']}"
            return result

        # 5. 模拟浏览器确认流程
        print("\n步骤5: 模拟浏览器确认流程")
        browser_result = self.simulate_browser_confirmation(email_address, link_params["oob_code"])
        result["browser_confirmation"] = browser_result

        # 6. 完成邮箱登录
        print("\n步骤6: 完成邮箱登录")
        signin_result = self.complete_email_signin(email_address, link_params["oob_code"])
        result["signin_result"] = signin_result

        if not signin_result["success"]:
            result["error"] = f"完成登录失败: {signin_result.get('error')}"
            return result

        # 7. 整理最终结果
        result["final_tokens"] = {
            "email": signin_result["email"],
            "local_id": signin_result["local_id"],
            "id_token": signin_result["id_token"],
            "refresh_token": signin_result["refresh_token"],
            "expires_in": signin_result["expires_in"],
            "is_new_user": signin_result["is_new_user"],
            "registered": signin_result["registered"],
            "browser_confirmed": browser_result.get("confirmed", False)
        }

        result["success"] = True

        print("\n" + "=" * 80)
        print("🎯 完整脚本注册流程成功完成")
        print("=" * 80)
        print(f"✅ 邮箱: {result['final_tokens']['email']}")
        print(f"✅ 用户ID: {result['final_tokens']['local_id']}")
        print(f"✅ 是否新用户: {result['final_tokens']['is_new_user']}")
        print(f"✅ 已注册: {result['final_tokens']['registered']}")
        print(f"✅ 浏览器确认: {result['final_tokens']['browser_confirmed']}")
        print(f"✅ ID Token: {result['final_tokens']['id_token'][:50]}...")
        print(f"✅ Refresh Token: {result['final_tokens']['refresh_token'][:50]}...")

        print("\n🎉 现在可以使用这些token信息进行Warp用户切换了！")

        return result


def main():
    """主函数"""
    registrar = CompleteScriptRegistration()
    
    try:
        result = registrar.run_complete_registration()
        
        # 保存结果
        with open("complete_script_registration_result.json", "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 完整注册结果已保存到: complete_script_registration_result.json")
        
        if result["success"]:
            print("\n✅ 完整脚本注册成功！可以直接使用token进行用户切换。")
            
            # 显示用于切换的关键信息
            tokens = result["final_tokens"]
            print("\n📋 用户切换所需信息:")
            print(f"邮箱: {tokens['email']}")
            print(f"用户ID: {tokens['local_id']}")
            print(f"ID Token: {tokens['id_token']}")
            print(f"Refresh Token: {tokens['refresh_token']}")
        else:
            print(f"\n❌ 完整脚本注册失败: {result.get('error')}")
        
    except KeyboardInterrupt:
        print("\n⚠️ 注册被用户中断")
    except Exception as e:
        print(f"\n❌ 注册异常: {e}")


if __name__ == "__main__":
    main()
