#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Warp API 配额检查器
通过GraphQL API查询账号的配额使用情况
"""

import os
import json
import time
import asyncio
import httpx
from typing import Dict, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass

from .pool_manager import get_pool_manager
from .database import Account
from utils.logger import logger


@dataclass
class QuotaInfo:
    """配额信息数据类"""
    is_unlimited: bool
    next_refresh_time: Optional[datetime]
    request_limit: int
    requests_used_since_last_refresh: int
    request_limit_refresh_duration: str
    remaining_requests: int
    usage_percentage: float
    
    # 其他配额信息
    is_unlimited_autosuggestions: bool
    accepted_autosuggestions_limit: int
    accepted_autosuggestions_since_last_refresh: int
    
    is_unlimited_voice: bool
    voice_request_limit: int
    voice_requests_used_since_last_refresh: int
    
    is_unlimited_codebase_indices: bool
    max_codebase_indices: int
    max_files_per_repo: int
    
    # 时间戳
    checked_at: datetime


class QuotaChecker:
    """配额检查器"""
    
    def __init__(self):
        self.graphql_url = os.getenv("WARP_GRAPHQL_URL", "https://app.warp.dev/graphql/v2")
        self.client_version = os.getenv("WARP_CLIENT_VERSION", "v0.2025.10.01.08.12.stable_02")
        
        # GraphQL查询模板
        self.query_template = """
        query GetRequestLimitInfo($requestContext: RequestContext!) {
          user(requestContext: $requestContext) {
            __typename
            ... on UserOutput {
              user {
                requestLimitInfo {
                  isUnlimited
                  nextRefreshTime
                  requestLimit
                  requestsUsedSinceLastRefresh
                  requestLimitRefreshDuration
                  isUnlimitedAutosuggestions
                  acceptedAutosuggestionsLimit
                  acceptedAutosuggestionsSinceLastRefresh
                  isUnlimitedVoice
                  voiceRequestLimit
                  voiceRequestsUsedSinceLastRefresh
                  voiceTokenLimit
                  voiceTokensUsedSinceLastRefresh
                  isUnlimitedCodebaseIndices
                  maxCodebaseIndices
                  maxFilesPerRepo
                  embeddingGenerationBatchSize
                }
              }
            }
            ... on UserFacingError {
              error {
                __typename
                ... on SharedObjectsLimitExceeded {
                  limit
                  objectType
                  message
                }
                ... on PersonalObjectsLimitExceeded {
                  limit
                  objectType
                  message
                }
                ... on AccountDelinquencyError {
                  message
                }
                ... on GenericStringObjectUniqueKeyConflict {
                  message
                }
              }
              responseContext {
                serverVersion
              }
            }
          }
        }
        """
    
    async def check_quota_for_token(self, access_token: str) -> Optional[QuotaInfo]:
        """
        检查指定Token的配额情况
        
        Args:
            access_token: Warp访问令牌
            
        Returns:
            QuotaInfo对象，如果查询失败返回None
        """
        # 检查是否启用模拟模式
        if os.getenv("QUOTA_MOCK_MODE", "false").lower() == "true":
            logger.info("使用模拟配额数据")
            from datetime import timedelta
            return QuotaInfo(
                is_unlimited=False,
                next_refresh_time=datetime.now(timezone.utc) + timedelta(days=7),
                request_limit=100,
                requests_used_since_last_refresh=25,
                request_limit_refresh_duration="WEEKLY",
                remaining_requests=75,
                usage_percentage=25.0,
                
                # 自动建议配额
                is_unlimited_autosuggestions=False,
                accepted_autosuggestions_limit=50,
                accepted_autosuggestions_since_last_refresh=10,
                
                # 语音配额
                is_unlimited_voice=False,
                voice_request_limit=30,
                voice_requests_used_since_last_refresh=5,
                
                # 代码库索引配额
                is_unlimited_codebase_indices=False,
                max_codebase_indices=5,
                max_files_per_repo=1000,
                
                checked_at=datetime.now(timezone.utc)
            )
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "authorization": f"Bearer {access_token}",
            "content-type": "application/json",
            "origin": "https://app.warp.dev",
            "x-warp-client-id": "warp-app",
            "x-warp-client-version": self.client_version,
            "x-warp-os-category": "Web",
            "x-warp-os-name": "Linux",
            "x-warp-os-version": "Ubuntu 22.04",
        }
        
        variables = {
            "requestContext": {
                "clientContext": {
                    "version": self.client_version
                },
                "osContext": {
                    "category": "Web",
                    "linuxKernelVersion": None,
                    "name": "Linux",
                    "version": "Ubuntu 22.04"
                }
            }
        }
        
        payload = {
            "query": self.query_template,
            "variables": variables,
            "operationName": "GetRequestLimitInfo"
        }
        
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                response = await client.post(
                    self.graphql_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"配额查询失败: HTTP {response.status_code}")
                    logger.error(f"响应内容: {response.text[:200]}")
                    return None
                
                data = response.json()
                
                # 检查GraphQL错误
                if "errors" in data:
                    logger.error(f"GraphQL查询错误: {data['errors']}")
                    return None
                
                # 解析配额信息
                user_data = data.get("data", {}).get("user", {})
                if user_data.get("__typename") != "UserOutput":
                    logger.error(f"用户数据类型错误: {user_data.get('__typename')}")
                    return None
                
                request_limit_info = user_data.get("user", {}).get("requestLimitInfo", {})
                if not request_limit_info:
                    logger.error("未找到配额信息")
                    return None
                
                return self._parse_quota_info(request_limit_info)
                
        except Exception as e:
            logger.error(f"配额查询异常: {e}")
            return None
    
    def _parse_quota_info(self, data: Dict[str, Any]) -> QuotaInfo:
        """
        解析配额信息数据
        
        Args:
            data: GraphQL返回的配额数据
            
        Returns:
            QuotaInfo对象
        """
        # 解析下次刷新时间
        next_refresh_time = None
        next_refresh_str = data.get("nextRefreshTime")
        if next_refresh_str:
            try:
                next_refresh_time = datetime.fromisoformat(next_refresh_str.replace('Z', '+00:00'))
            except:
                pass
        
        # 计算剩余请求数和使用百分比
        request_limit = data.get("requestLimit", 0)
        requests_used = data.get("requestsUsedSinceLastRefresh", 0)
        remaining_requests = max(0, request_limit - requests_used)
        usage_percentage = (requests_used / request_limit * 100) if request_limit > 0 else 0
        
        return QuotaInfo(
            is_unlimited=data.get("isUnlimited", False),
            next_refresh_time=next_refresh_time,
            request_limit=request_limit,
            requests_used_since_last_refresh=requests_used,
            request_limit_refresh_duration=data.get("requestLimitRefreshDuration", "UNKNOWN"),
            remaining_requests=remaining_requests,
            usage_percentage=usage_percentage,
            
            # 自动建议配额
            is_unlimited_autosuggestions=data.get("isUnlimitedAutosuggestions", False),
            accepted_autosuggestions_limit=data.get("acceptedAutosuggestionsLimit", 0),
            accepted_autosuggestions_since_last_refresh=data.get("acceptedAutosuggestionsSinceLastRefresh", 0),
            
            # 语音配额
            is_unlimited_voice=data.get("isUnlimitedVoice", False),
            voice_request_limit=data.get("voiceRequestLimit", 0),
            voice_requests_used_since_last_refresh=data.get("voiceRequestsUsedSinceLastRefresh", 0),
            
            # 代码库索引配额
            is_unlimited_codebase_indices=data.get("isUnlimitedCodebaseIndices", False),
            max_codebase_indices=data.get("maxCodebaseIndices", 0),
            max_files_per_repo=data.get("maxFilesPerRepo", 0),
            
            checked_at=datetime.now(timezone.utc)
        )
    
    async def check_quota_for_account(self, email: str) -> Optional[QuotaInfo]:
        """
        检查指定账号的配额情况
        
        Args:
            email: 账号邮箱
            
        Returns:
            QuotaInfo对象，如果查询失败返回None
        """
        from .database import Account
        
        # 获取账号信息
        pool_manager = get_pool_manager()
        account = pool_manager.db.get_account_by_email(email)
        
        if not account:
            logger.error(f"账号不存在: {email}")
            return None
        
        # 获取访问令牌
        access_token = await self._get_access_token_for_account(account)
        if not access_token:
            logger.error(f"无法获取账号 {email} 的访问令牌")
            return None
        
        # 查询配额
        quota_info = await self.check_quota_for_token(access_token)
        
        if quota_info:
            # 更新数据库中的配额信息
            await self._update_account_quota_info(email, quota_info)
        
        return quota_info
    
    async def _get_access_token_for_account(self, account: Account) -> Optional[str]:
        """
        获取账号的访问令牌
        
        Args:
            account: 账号对象
            
        Returns:
            访问令牌，如果获取失败返回None
        """
        # 如果有refresh_token，尝试刷新
        if account.refresh_token:
            try:
                # 使用环境变量中的配置
                refresh_url = os.getenv("WARP_REFRESH_URL", "https://api.warp.dev/v2/auth/refresh")
                client_version = os.getenv("WARP_CLIENT_VERSION", "v0.2025.10.01.08.12.stable_02")
                os_category = os.getenv("WARP_OS_CATEGORY", "Web")
                os_name = os.getenv("WARP_OS_NAME", "Linux")
                os_version = os.getenv("WARP_OS_VERSION", "Ubuntu 22.04")
                
                payload = f"grant_type=refresh_token&refresh_token={account.refresh_token}".encode("utf-8")
                headers = {
                    "x-warp-client-version": client_version,
                    "x-warp-os-category": os_category,
                    "x-warp-os-name": os_name,
                    "x-warp-os-version": os_version,
                    "content-type": "application/x-www-form-urlencoded",
                    "accept": "*/*",
                    "accept-encoding": "gzip, br",
                    "content-length": str(len(payload))
                }
                
                async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                    resp = await client.post(refresh_url, headers=headers, content=payload)
                    if resp.status_code == 200:
                        token_data = resp.json()
                        access_token = token_data.get("access_token")
                        if access_token:
                            return access_token
            except Exception as e:
                logger.warning(f"刷新令牌失败: {e}")
        
        # 使用id_token
        return account.id_token
    
    async def _update_account_quota_info(self, email: str, quota_info: QuotaInfo):
        """
        更新数据库中的配额信息
        
        Args:
            email: 账号邮箱
            quota_info: 配额信息
        """
        try:
            pool_manager = get_pool_manager()
            
            # 将配额信息序列化为JSON存储
            quota_data = {
                "is_unlimited": quota_info.is_unlimited,
                "next_refresh_time": quota_info.next_refresh_time.isoformat() if quota_info.next_refresh_time else None,
                "request_limit": quota_info.request_limit,
                "requests_used_since_last_refresh": quota_info.requests_used_since_last_refresh,
                "request_limit_refresh_duration": quota_info.request_limit_refresh_duration,
                "remaining_requests": quota_info.remaining_requests,
                "usage_percentage": quota_info.usage_percentage,
                "checked_at": quota_info.checked_at.isoformat()
            }
            
            # 更新数据库（这里可以扩展数据库schema来存储配额信息）
            # 目前只是记录日志
            logger.info(f"账号 {email} 配额信息已更新: {quota_info.remaining_requests}/{quota_info.request_limit} ({quota_info.usage_percentage:.1f}%)")
            
        except Exception as e:
            logger.error(f"更新账号配额信息失败: {e}")
    
    def format_quota_info(self, quota_info: QuotaInfo) -> str:
        """
        格式化配额信息为可读字符串
        
        Args:
            quota_info: 配额信息
            
        Returns:
            格式化的字符串
        """
        status = "无限制" if quota_info.is_unlimited else f"{quota_info.remaining_requests}/{quota_info.request_limit}"
        
        refresh_info = ""
        if quota_info.next_refresh_time:
            time_until_refresh = quota_info.next_refresh_time - datetime.now(timezone.utc)
            if time_until_refresh.total_seconds() > 0:
                days = time_until_refresh.days
                hours = time_until_refresh.seconds // 3600
                refresh_info = f", {days}天{hours}小时后刷新"
        
        return f"配额: {status} ({quota_info.usage_percentage:.1f}%已用){refresh_info}"


# 全局配额检查器实例
_quota_checker = None


def get_quota_checker() -> QuotaChecker:
    """获取配额检查器实例"""
    global _quota_checker
    if _quota_checker is None:
        _quota_checker = QuotaChecker()
    return _quota_checker


async def check_account_quota(email: str) -> Optional[QuotaInfo]:
    """
    检查账号配额的便捷函数
    
    Args:
        email: 账号邮箱
        
    Returns:
        QuotaInfo对象，如果查询失败返回None
    """
    checker = get_quota_checker()
    return await checker.check_quota_for_account(email)


async def check_token_quota(access_token: str) -> Optional[QuotaInfo]:
    """
    检查Token配额的便捷函数
    
    Args:
        access_token: 访问令牌
        
    Returns:
        QuotaInfo对象，如果查询失败返回None
    """
    checker = get_quota_checker()
    return await checker.check_quota_for_token(access_token)


if __name__ == "__main__":
    # 测试代码
    async def test_quota_checker():
        """测试配额检查器"""
        checker = get_quota_checker()
        
        # 测试Token配额检查
        test_token = "your_test_token_here"
        quota_info = await checker.check_quota_for_token(test_token)
        
        if quota_info:
            print(checker.format_quota_info(quota_info))
            print(f"详细配额信息: {json.dumps(quota_info.__dict__, default=str, indent=2)}")
        else:
            print("配额查询失败")
    
    # 运行测试
    asyncio.run(test_quota_checker())