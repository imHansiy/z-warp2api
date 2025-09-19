#!/bin/bash
# Warp2API 停止脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🛑 停止 Warp2API 服务${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 停止函数
stop_service() {
    local port=$1
    local name=$2
    
    echo -n "停止 $name (端口 $port)..."
    
    # 查找占用端口的进程
    PID=$(lsof -ti:$port 2>/dev/null)
    
    if [ -z "$PID" ]; then
        echo -e " ${YELLOW}[未运行]${NC}"
    else
        kill $PID 2>/dev/null
        sleep 1
        
        # 检查是否成功停止
        if lsof -ti:$port > /dev/null 2>&1; then
            echo -e " ${YELLOW}[正常停止失败，强制终止]${NC}"
            kill -9 $PID 2>/dev/null
        fi
        
        echo -e " ${GREEN}[已停止] PID: $PID${NC}"
    fi
}

# 停止服务
echo ""
stop_service 8019 "账号池服务"
stop_service 8000 "Warp2API服务"

echo ""
echo -e "${GREEN}✅ 所有服务已停止${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"