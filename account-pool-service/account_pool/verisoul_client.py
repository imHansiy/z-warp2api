#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verisoul客户端模块
模拟Verisoul反欺诈系统的会话，以解决Warp账号激活问题
"""

import os
import json
import time
import uuid
import random
import requests
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime
import websocket
import logging

# 设置日志
logger = logging.getLogger(__name__)


class VerisoulClient:
    """Verisoul客户端"""
    
    def __init__(self):
        """初始化Verisoul客户端"""
        self.project_id = "27fcb93a-7693-486d-b969-a9d96f799f91"
        self.session_id = str(uuid.uuid4())
        self.base_url = "https://ingest.prod.verisoul.ai"
        self.ws_url = "wss://ingest.prod.verisoul.ai/ws"
        
        # 会话状态
        self.session_active = False
        self.ws_thread = None
        self.ws = None
        
        # 事件计数器
        self.event_counter = 0
        
        # 浏览器指纹信息
        self.browser_fingerprint = self._generate_browser_fingerprint()
        
        logger.info(f"🔧 Verisoul客户端初始化完成，会话ID: {self.session_id}")
    
    def _generate_browser_fingerprint(self) -> Dict[str, Any]:
        """生成浏览器指纹信息"""
        return {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
            "screen_resolution": "1920x1080",
            "color_depth": 24,
            "timezone": "UTC",
            "language": "zh-CN,zh;q=0.9,en;q=0.8",
            "platform": "Win32",
            "cookies_enabled": True,
            "do_not_track": "1",
            "plugins": [
                "Chrome PDF Plugin",
                "Chrome PDF Viewer",
                "Native Client",
                "Microsoft Edge PDF Plugin"
            ],
            "webgl_vendor": "Google Inc.",
            "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "canvas_fingerprint": self._generate_canvas_fingerprint()
        }
    
    def _generate_canvas_fingerprint(self) -> str:
        """生成Canvas指纹"""
        # 简化的Canvas指纹生成
        return f"canvas_{random.randint(100000, 999999)}_{int(time.time())}"
    
    def _generate_headers(self) -> Dict[str, str]:
        """生成请求头"""
        return {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://app.warp.dev',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': self.browser_fingerprint["user_agent"]
        }
    
    def _generate_event_data(self, event_type: str) -> Dict[str, Any]:
        """生成事件数据"""
        self.event_counter += 1
        
        base_data = {
            "event_id": str(uuid.uuid4()),
            "session_id": self.session_id,
            "project_id": self.project_id,
            "time": datetime.utcnow().isoformat() + "Z",
            "is_v2": True,
            "event": event_type,
            "url": "https://app.warp.dev/login",
            "referrer": "https://app.warp.dev/",
            "user_agent": self.browser_fingerprint["user_agent"],
            "screen": {
                "width": 1920,
                "height": 1080,
                "color_depth": 24,
                "pixel_ratio": 1
            },
            "viewport": {
                "width": 1920,
                "height": 947
            },
            "timezone": "UTC",
            "language": "zh-CN,zh;q=0.9,en;q=0.8",
            "platform": "Win32",
            "cookies_enabled": True,
            "do_not_track": "1"
        }
        
        # 根据事件类型添加特定数据
        if event_type == "device_minmet":
            base_data.update({
                "device": {
                    "vendor": "Google Inc.",
                    "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)",
                    "memory": 8,
                    "cores": 8
                },
                "webgl": True,
                "canvas": True,
                "plugins": len(self.browser_fingerprint["plugins"])
            })
        elif event_type == "device_complete":
            base_data.update({
                "javascript": True,
                "cookies": True,
                "images": True,
                "css": True,
                "flash": False
            })
        elif event_type == "device_worker":
            base_data.update({
                "worker": True,
                "service_worker": True,
                "shared_worker": False
            })
        elif event_type == "device_experimental":
            base_data.update({
                "experimental": True,
                "features": ["webgl", "webgl2", "webassembly"]
            })
        
        return base_data
    
    def start_session(self) -> bool:
        """启动Verisoul会话"""
        try:
            logger.info("🚀 启动Verisoul会话...")
            
            # 1. 建立WebSocket连接
            self._establish_websocket_connection()
            
            # 2. 获取ICE服务器
            self._get_ice_servers()
            
            # 3. 发送设备指纹事件
            self._send_device_events()
            
            # 4. 发送WebRTC SDP
            self._send_webrtc_sdp()
            
            self.session_active = True
            logger.info("✅ Verisoul会话启动成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 启动Verisoul会话失败: {e}")
            return False
    
    def _establish_websocket_connection(self):
        """建立WebSocket连接"""
        try:
            # WebSocket请求头
            ws_headers = [
                f"Origin: https://app.warp.dev",
                f"Cache-Control: no-cache",
                f"Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                f"Pragma: no-cache",
                f"User-Agent: {self.browser_fingerprint['user_agent']}"
            ]
            
            # 创建WebSocket连接
            self.ws = websocket.create_connection(
                self.ws_url,
                header=ws_headers,
                timeout=10
            )
            
            logger.info("✅ WebSocket连接建立成功")
            
        except Exception as e:
            logger.error(f"❌ 建立WebSocket连接失败: {e}")
            # WebSocket连接失败不应该阻止整个流程
            logger.warning("⚠️ WebSocket连接失败，继续执行HTTP请求")
    
    def _get_ice_servers(self):
        """获取ICE服务器"""
        try:
            url = f"{self.base_url}/worker/ice-servers"
            params = {
                "project_id": self.project_id,
                "session_id": self.session_id
            }
            
            response = requests.get(
                url, 
                params=params, 
                headers=self._generate_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ ICE服务器获取成功")
            else:
                logger.warning(f"⚠️ ICE服务器获取失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ 获取ICE服务器异常: {e}")
            raise
    
    def _send_device_events(self):
        """发送设备指纹事件"""
        events = ["device_minmet", "device_complete", "device_worker", "device_experimental"]
        
        for event in events:
            try:
                url = f"{self.base_url}/worker"
                data = self._generate_event_data(event)
                
                response = requests.post(
                    url,
                    json=data,
                    headers=self._generate_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ 事件 {event} 发送成功")
                else:
                    logger.warning(f"⚠️ 事件 {event} 发送失败: {response.status_code}")
                
                # 添加延迟模拟真实用户行为
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                logger.error(f"❌ 发送事件 {event} 异常: {e}")
    
    def _send_webrtc_sdp(self):
        """发送WebRTC SDP"""
        try:
            url = f"{self.base_url}/webrtc-sdp"
            data = {
                "session_id": self.session_id,
                "sdp": f"v=0\r\no=- {random.randint(1000000000, 9999999999)} 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n",
                "type": "offer"
            }
            
            response = requests.post(
                url,
                json=data,
                headers=self._generate_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ WebRTC SDP发送成功")
            else:
                logger.warning(f"⚠️ WebRTC SDP发送失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ 发送WebRTC SDP异常: {e}")
    
    def maintain_session(self):
        """维护会话活动"""
        if not self.session_active:
            return
        
        try:
            # 定期发送心跳事件
            heartbeat_data = self._generate_event_data("heartbeat")
            
            url = f"{self.base_url}/worker"
            response = requests.post(
                url,
                json=heartbeat_data,
                headers=self._generate_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug("💓 会话心跳发送成功")
            else:
                logger.warning(f"⚠️ 会话心跳发送失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ 维护会话异常: {e}")
    
    def end_session(self):
        """结束会话"""
        try:
            logger.info("🛑 结束Verisoul会话...")
            
            if self.ws:
                self.ws.close()
                self.ws = None
            
            self.session_active = False
            logger.info("✅ Verisoul会话已结束")
            
        except Exception as e:
            logger.error(f"❌ 结束会话异常: {e}")
    
    def get_session_id(self) -> str:
        """获取会话ID"""
        return self.session_id
    
    def is_session_active(self) -> bool:
        """检查会话是否活动"""
        return self.session_active


# 全局客户端实例
_verisoul_client = None

def get_verisoul_client() -> VerisoulClient:
    """获取Verisoul客户端实例（单例模式）"""
    global _verisoul_client
    if _verisoul_client is None:
        _verisoul_client = VerisoulClient()
    return _verisoul_client


def start_verisoul_session() -> str:
    """启动Verisoul会话并返回会话ID"""
    client = get_verisoul_client()
    if client.start_session():
        return client.get_session_id()
    else:
        raise Exception("无法启动Verisoul会话")


def end_verisoul_session():
    """结束Verisoul会话"""
    global _verisoul_client
    if _verisoul_client:
        _verisoul_client.end_session()
        _verisoul_client = None


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    client = VerisoulClient()
    
    try:
        # 启动会话
        session_id = client.get_session_id()
        print(f"会话ID: {session_id}")
        
        # 启动会话
        if client.start_session():
            print("✅ 会话启动成功")
            
            # 维护会话
            for i in range(5):
                time.sleep(10)
                client.maintain_session()
                print(f"💓 心跳 {i+1}/5")
            
            # 结束会话
            client.end_session()
            print("✅ 会话结束")
        else:
            print("❌ 会话启动失败")
            
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        client.end_session()
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        client.end_session()