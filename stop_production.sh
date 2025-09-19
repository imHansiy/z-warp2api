#!/bin/bash
# Warp2API 生产环境停止脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 停止 Warp2API 生产环境服务"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"
echo

# 函数：停止服务
stop_service() {
    local service_name=$1
    local port=$2
    local pid_file=$3
    
    echo -n "停止 $service_name (端口 $port)... "
    
    # 首先尝试使用PID文件停止
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            rm -f "$pid_file"
            echo -e "${GREEN}[已停止]${NC} PID: $pid"
            return 0
        else
            rm -f "$pid_file"
        fi
    fi
    
    # 如果PID文件不存在或进程已死，尝试通过端口查找并停止
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill 2>/dev/null
        echo -e "${GREEN}[已停止]${NC} PIDs: $pids"
    else
        echo -e "${YELLOW}[未运行]${NC}"
    fi
}

# 停止服务
stop_service "账号池服务" 8019 "data/pool-service.pid"
stop_service "Warp2API服务" 8000 "data/warp2api.pid"

echo
echo -e "${GREEN}✅ 所有服务已停止${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"