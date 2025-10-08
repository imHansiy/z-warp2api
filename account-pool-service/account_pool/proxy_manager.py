#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理池管理器
从代理池API获取代理IP，用于账号注册和API请求
"""

import os
import requests
import random
import time
from typing import Optional, Dict, Any
from utils.logger import logger


class ProxyManager:
    """代理池管理器"""
    
    def __init__(self):
        """初始化代理池管理器"""
        self.base_url = os.getenv("PROXY_POOL_URL", "https://proxy-pool.007666.xyz/")
        self.current_proxy = None
        self.proxy_fail_count = 0
        self.max_fail_count = int(os.getenv("PROXY_MAX_FAIL_COUNT", "3"))
        self.last_proxy_time = 0
        self.proxy_refresh_interval = int(os.getenv("PROXY_REFRESH_INTERVAL", "300"))  # 5分钟
        self.use_proxy = os.getenv("USE_PROXY", "false").lower() == "true"
        
        logger.info(f"代理池管理器初始化完成")
        logger.info(f"  代理池URL: {self.base_url}")
        logger.info(f"  使用代理: {self.use_proxy}")
        logger.info(f"  最大失败次数: {self.max_fail_count}")
        logger.info(f"  代理刷新间隔: {self.proxy_refresh_interval}秒")
    
    def get_proxy(self, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        获取一个代理
        
        Args:
            force_refresh: 是否强制刷新代理
            
        Returns:
            代理信息字典，包含proxy、https等字段
        """
        if not self.use_proxy:
            logger.debug("代理功能已禁用")
            return None
            
        # 检查是否需要刷新代理
        current_time = time.time()
        if (not force_refresh and 
            self.current_proxy and 
            self.proxy_fail_count < self.max_fail_count and
            current_time - self.last_proxy_time < self.proxy_refresh_interval):
            logger.debug(f"使用当前代理: {self.current_proxy.get('proxy', 'N/A')}")
            return self.current_proxy
        
        try:
            logger.info("从代理池获取新代理...")
            
            # 尝试获取HTTPS代理
            timeout = int(os.getenv("PROXY_REQUEST_TIMEOUT", "10"))
            response = requests.get(f"{self.base_url}/get/", params={"type": "https"}, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查是否成功获取代理
                if "proxy" in data:
                    self.current_proxy = data
                    self.proxy_fail_count = 0
                    self.last_proxy_time = current_time
                    
                    logger.info(f"获取到新代理: {data.get('proxy', 'N/A')}")
                    logger.info(f"  支持HTTPS: {data.get('https', False)}")
                    logger.info(f"  来源: {data.get('source', 'N/A')}")
                    logger.info(f"  地区: {data.get('region', 'N/A')}")
                    
                    return data
                else:
                    logger.warning(f"代理池返回无代理: {data}")
                    
                    # 尝试获取HTTP代理
                    timeout = int(os.getenv("PROXY_REQUEST_TIMEOUT", "10"))
                    response = requests.get(f"{self.base_url}/get/", timeout=timeout)
                    if response.status_code == 200:
                        data = response.json()
                        if "proxy" in data:
                            self.current_proxy = data
                            self.proxy_fail_count = 0
                            self.last_proxy_time = current_time
                            
                            logger.info(f"获取到HTTP代理: {data.get('proxy', 'N/A')}")
                            return data
                        else:
                            logger.warning(f"代理池返回无代理: {data}")
                    else:
                        logger.error(f"获取代理失败: HTTP {response.status_code}")
            else:
                logger.error(f"获取代理失败: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"获取代理异常: {e}")
        
        # 获取代理失败，返回当前代理（如果有的话）
        if self.current_proxy and self.proxy_fail_count < self.max_fail_count:
            logger.warning(f"获取新代理失败，使用当前代理: {self.current_proxy.get('proxy', 'N/A')}")
            return self.current_proxy
        
        logger.error("无可用代理")
        return None
    
    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """
        获取requests库使用的代理字典
        
        Returns:
            代理字典，格式为 {"http": "proxy", "https": "proxy"}
        """
        proxy_info = self.get_proxy()
        
        if not proxy_info:
            return None
            
        proxy = proxy_info.get("proxy")
        if not proxy:
            return None
            
        # 构建代理字典
        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        
        return proxy_dict
    
    def mark_proxy_failed(self):
        """标记当前代理失败"""
        if self.current_proxy:
            self.proxy_fail_count += 1
            logger.warning(f"代理失败次数: {self.proxy_fail_count}/{self.max_fail_count}")
            
            # 如果失败次数超过阈值，删除代理
            if self.proxy_fail_count >= self.max_fail_count:
                self.delete_current_proxy()
    
    def delete_current_proxy(self):
        """删除当前代理"""
        if not self.current_proxy:
            return
            
        try:
            proxy = self.current_proxy.get("proxy")
            if not proxy:
                return
                
            logger.info(f"删除失败代理: {proxy}")
            
            # 调用删除API
            timeout = int(os.getenv("PROXY_REQUEST_TIMEOUT", "10"))
            response = requests.get(f"{self.base_url}/delete/", params={"proxy": proxy}, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"删除代理响应: {data}")
            else:
                logger.error(f"删除代理失败: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"删除代理异常: {e}")
        finally:
            # 重置当前代理
            self.current_proxy = None
            self.proxy_fail_count = 0
    
    def get_proxy_stats(self) -> Dict[str, Any]:
        """
        获取代理池统计信息
        
        Returns:
            代理池统计信息
        """
        try:
            timeout = int(os.getenv("PROXY_REQUEST_TIMEOUT", "10"))
            response = requests.get(f"{self.base_url}/count/", timeout=timeout)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取代理统计失败: HTTP {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"获取代理统计异常: {e}")
            return {}
    
    def test_proxy(self, proxy_info: Dict[str, Any] = None) -> bool:
        """
        测试代理是否可用
        
        Args:
            proxy_info: 代理信息，如果为None则使用当前代理
            
        Returns:
            代理是否可用
        """
        if not proxy_info:
            proxy_info = self.current_proxy
            
        if not proxy_info:
            return False
            
        proxy = proxy_info.get("proxy")
        if not proxy:
            return False
            
        try:
            # 使用代理访问httpbin.org
            proxy_dict = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            
            proxy_test_url = os.getenv("PROXY_TEST_URL", "https://httpbin.org/ip")
            response = requests.get(
                proxy_test_url,
                proxies=proxy_dict,
                timeout=int(os.getenv("PROXY_TEST_TIMEOUT", "10"))
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"代理测试成功: {proxy} -> {data.get('origin', 'N/A')}")
                return True
            else:
                logger.warning(f"代理测试失败: {proxy} - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"代理测试异常: {proxy} - {e}")
            return False


# 全局代理管理器实例
_proxy_manager_instance = None


def get_proxy_manager() -> ProxyManager:
    """获取代理管理器实例（单例模式）"""
    global _proxy_manager_instance
    if _proxy_manager_instance is None:
        _proxy_manager_instance = ProxyManager()
    return _proxy_manager_instance


if __name__ == "__main__":
    # 测试代理管理器
    manager = ProxyManager()
    
    # 获取代理
    proxy = manager.get_proxy()
    if proxy:
        print(f"获取到代理: {proxy}")
        
        # 测试代理
        if manager.test_proxy():
            print("代理测试成功")
        else:
            print("代理测试失败")
            manager.mark_proxy_failed()
    else:
        print("无可用代理")
    
    # 获取统计信息
    stats = manager.get_proxy_stats()
    print(f"代理池统计: {stats}")