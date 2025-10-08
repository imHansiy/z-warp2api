#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MoeMail API 客户端
简单易用的临时邮箱服务客户端
"""

import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass


@dataclass
class TempEmail:
    """临时邮箱数据类"""
    id: str
    address: str
    created_at: str
    expires_at: str


@dataclass
class EmailMessage:
    """邮件消息数据类"""
    id: str
    from_address: str
    subject: str
    content: str
    html: str
    received_at: int


class MoeMailClient:
    """MoeMail API 客户端"""
    
    def __init__(self, base_url: str, api_key: str):
        """
        初始化客户端
        
        Args:
            base_url: MoeMail 服务器地址
            api_key: API 密钥
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # 获取代理管理器
        self.proxies = None
        try:
            from proxy_manager import get_proxy_manager
            proxy_manager = get_proxy_manager()
            self.proxies = proxy_manager.get_proxy_dict()
            proxy_info = proxy_manager.get_proxy()
            proxy_str = proxy_info.get("proxy", "N/A") if proxy_info else "无代理"
            if self.proxies:
                print(f"🌐 邮箱客户端使用代理: {proxy_str}")
        except ImportError:
            pass
        
        # 配置连接池和重试策略
        retry_strategy = Retry(
            total=3,  # 总重试次数
            backoff_factor=1,  # 重试间隔因子
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的HTTP状态码
            allowed_methods=["HEAD", "GET", "POST", "DELETE"]  # 允许重试的HTTP方法
        )
        
        adapter = HTTPAdapter(
            pool_connections=10,  # 连接池大小
            pool_maxsize=20,     # 连接池最大连接数
            max_retries=retry_strategy,
            pool_block=False     # 连接池满时不阻塞
        )
        
        # 为HTTP和HTTPS都设置适配器
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置请求头
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',  # 启用Keep-Alive
            'User-Agent': os.getenv("MOEMAIL_CLIENT_VERSION", "MoeMailClient/1.0")
        })
    
    def get_config(self) -> Dict[str, Any]:
        """获取系统配置"""
        try:
            response = self.session.get(f"{self.base_url}/api/config", proxies=self.proxies)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if self.proxies:
                try:
                    from proxy_manager import get_proxy_manager
                    proxy_manager = get_proxy_manager()
                    proxy_manager.mark_proxy_failed()
                except:
                    pass
            raise Exception(f"获取配置失败: {e}")
    
    def create_email(self, name: str = None, domain: str = None,
                    expiry_hours: int = 1) -> TempEmail:
        """
        创建临时邮箱
        
        Args:
            name: 邮箱前缀（可选）
            domain: 邮箱域名，默认从环境变量MOEMAIL_DOMAIN获取
            expiry_hours: 有效期（小时），支持 1, 24, 168（7天）, 0（永久），默认1小时
        
        Returns:
            TempEmail: 创建的邮箱信息
        """
        # 转换小时到毫秒
        expiry_map = {
            1: 3600000,      # 1小时
            24: 86400000,    # 1天  
            168: 604800000,  # 7天
            0: 0             # 永久
        }
        
        expiry_time = expiry_map.get(expiry_hours, 3600000)  # 默认1小时
        
        # 使用环境变量中的域名作为默认值
        if domain is None:
            domain = os.getenv("MOEMAIL_DOMAIN", "moemail.app")
            
        data = {
            "expiryTime": expiry_time,
            "domain": domain
        }
        
        if name:
            data["name"] = name
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/emails/generate",
                json=data,
                proxies=self.proxies
            )
            response.raise_for_status()
            result = response.json()
            
            return TempEmail(
                id=result["id"],
                address=result["email"],
                created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                expires_at=""  # API不直接返回过期时间
            )
        except requests.RequestException as e:
            if self.proxies:
                try:
                    from proxy_manager import get_proxy_manager
                    proxy_manager = get_proxy_manager()
                    proxy_manager.mark_proxy_failed()
                except:
                    pass
            raise Exception(f"创建邮箱失败: {e}")
    
    def get_emails(self) -> List[TempEmail]:
        """获取邮箱列表"""
        try:
            response = self.session.get(f"{self.base_url}/api/emails", proxies=self.proxies)
            response.raise_for_status()
            result = response.json()
            
            emails = []
            for email_data in result.get("emails", []):
                emails.append(TempEmail(
                    id=email_data["id"],
                    address=email_data["address"],
                    created_at=email_data.get("createdAt", ""),
                    expires_at=email_data.get("expiresAt", "")
                ))
            
            return emails
        except requests.RequestException as e:
            if self.proxies:
                try:
                    from proxy_manager import get_proxy_manager
                    proxy_manager = get_proxy_manager()
                    proxy_manager.mark_proxy_failed()
                except:
                    pass
            raise Exception(f"获取邮箱列表失败: {e}")
    
    def get_messages(self, email_id: str, limit: int = 10) -> List[EmailMessage]:
        """获取指定邮箱的邮件列表（优化版本）"""
        try:
            # 添加参数来获取最新邮件，忽略分页cursor
            params = {
                "limit": limit,
                "sort": "desc",  # 按时间倒序，获取最新邮件
            }
            
            response = self.session.get(
                f"{self.base_url}/api/emails/{email_id}/messages",
                params=params,
                proxies=self.proxies
            )
            
            # 如果上面的端点不存在，尝试原来的端点
            if response.status_code == 404:
                response = self.session.get(f"{self.base_url}/api/emails/{email_id}", proxies=self.proxies)
            
            response.raise_for_status()
            result = response.json()
            
            messages = []
            # 尝试不同的数据结构
            message_data = result.get("messages", result.get("data", []))
            
            for msg_data in message_data:
                messages.append(EmailMessage(
                    id=msg_data.get("id", msg_data.get("messageId", "")),
                    from_address=msg_data.get("from_address", msg_data.get("from", msg_data.get("sender", ""))),
                    subject=msg_data.get("subject", ""),
                    content=msg_data.get("content", msg_data.get("text", "")),
                    html=msg_data.get("html", msg_data.get("htmlContent", "")),
                    received_at=msg_data.get("received_at", msg_data.get("receivedAt", msg_data.get("timestamp", int(time.time() * 1000))))
                ))
            
            # 按接收时间排序，最新的在前面
            messages.sort(key=lambda x: x.received_at, reverse=True)
            
            return messages
        except requests.RequestException as e:
            raise Exception(f"获取邮件列表失败: {e}")
    
    def get_message_detail(self, email_id: str, message_id: str) -> EmailMessage:
        """获取邮件详细内容（优化版本）"""
        try:
            # 尝试不同的端点格式
            endpoints = [
                f"{self.base_url}/api/emails/{email_id}/messages/{message_id}",
                f"{self.base_url}/api/emails/{email_id}/{message_id}",
                f"{self.base_url}/api/messages/{message_id}"
            ]
            
            result = None
            for endpoint in endpoints:
                try:
                    response = self.session.get(endpoint, proxies=self.proxies)
                    if response.status_code == 200:
                        result = response.json()
                        break
                except:
                    continue
            
            if not result:
                # 如果所有端点都失败，抛出异常
                response = self.session.get(f"{self.base_url}/api/emails/{email_id}/{message_id}", proxies=self.proxies)
                response.raise_for_status()
                result = response.json()
            
            # 处理不同的响应格式
            msg_data = result.get("message", result.get("data", result))
            
            return EmailMessage(
                id=msg_data.get("id", msg_data.get("messageId", message_id)),
                from_address=msg_data.get("from_address", msg_data.get("from", msg_data.get("sender", ""))),
                subject=msg_data.get("subject", ""),
                content=msg_data.get("content", msg_data.get("text", "")),
                html=msg_data.get("html", msg_data.get("htmlContent", "")),
                received_at=msg_data.get("received_at", msg_data.get("receivedAt", msg_data.get("timestamp", int(time.time() * 1000))))
            )
        except requests.RequestException as e:
            raise Exception(f"获取邮件详情失败: {e}")
    
    def delete_email(self, email_id: str) -> bool:
        """删除邮箱"""
        try:
            response = self.session.delete(f"{self.base_url}/api/emails/{email_id}", proxies=self.proxies)
            response.raise_for_status()
            result = response.json()
            return result.get("success", False)
        except requests.RequestException as e:
            if self.proxies:
                try:
                    from proxy_manager import get_proxy_manager
                    proxy_manager = get_proxy_manager()
                    proxy_manager.mark_proxy_failed()
                except:
                    pass
            raise Exception(f"删除邮箱失败: {e}")
    
    def wait_for_email(self, email_id: str, timeout: int = None,
                      check_interval: int = None, progress_callback: Callable = None) -> Optional[EmailMessage]:
        """
        等待接收邮件（优化版本 - 忽略分页，直接获取最新邮件）
        
        Args:
            email_id: 邮箱ID
            timeout: 超时时间（秒），默认从环境变量EMAIL_TIMEOUT获取
            check_interval: 检查间隔（秒），默认从环境变量EMAIL_CHECK_INTERVAL获取
            progress_callback: 进度回调函数
            
        Returns:
            EmailMessage: 收到的第一封邮件，超时返回None
        """
        if progress_callback is None:
            progress_callback = print
            
        # 设置默认值
        if timeout is None:
            timeout = int(os.getenv("EMAIL_TIMEOUT", "300"))
        if check_interval is None:
            check_interval = int(os.getenv("EMAIL_CHECK_INTERVAL", "5"))
            
        start_time = time.time()
        attempt_count = 0
        
        while time.time() - start_time < timeout:
            attempt_count += 1
            try:
                # 获取邮件列表，限制为最新5封邮件
                messages = self.get_messages(email_id, limit=5)
                
                if messages:
                    # 获取最新邮件的详细内容
                    latest_message = self.get_message_detail(email_id, messages[0].id)
                    progress_callback(f"✅ 找到邮件: {latest_message.subject} (来自: {latest_message.from_address})")
                    return latest_message
                
                # 显示等待进度
                elapsed = int(time.time() - start_time)
                remaining = timeout - elapsed
                if attempt_count % 3 == 0:  # 每15秒显示一次进度
                    progress_callback(f"等待邮件中... 已等待{elapsed}秒，剩余{remaining}秒")
                
                time.sleep(check_interval)
                
            except Exception as e:
                progress_callback(f"检查邮件时出错: {e}")
                time.sleep(check_interval)
        
        progress_callback(f"⏰ 等待邮件超时 ({timeout}秒)")
        return None
    
    def get_latest_message(self, email_id: str) -> Optional[EmailMessage]:
        """
        直接获取最新的一封邮件（无需等待）
        
        Args:
            email_id: 邮箱ID
            
        Returns:
            EmailMessage: 最新邮件，如果没有邮件返回None
        """
        try:
            messages = self.get_messages(email_id, limit=1)
            if messages:
                return self.get_message_detail(email_id, messages[0].id)
            return None
        except Exception as e:
            print(f"获取最新邮件失败: {e}")
            return None


if __name__ == "__main__":
    # 测试代码
    client = MoeMailClient("https://moemail.app", "your-api-key")
    
    try:
        # 获取配置
        config = client.get_config()
        print("系统配置:", config)
        
        # 创建临时邮箱
        email = client.create_email("test", expiry_hours=1)
        print(f"创建邮箱成功: {email.address}")
        
        # 等待邮件
        print("等待接收邮件...")
        message = client.wait_for_email(email.id, timeout=60)
        
        if message:
            print(f"收到邮件: {message.subject}")
        else:
            print("未收到邮件")
            
    except Exception as e:
        print(f"错误: {e}")
