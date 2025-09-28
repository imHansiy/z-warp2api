#!/bin/sh
# Warp2API 容器环境停止脚本（兼容BusyBox/Alpine）

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "${BLUE}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 停止 Warp2API 容器环境服务"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "${NC}"
echo

# 获取脚本所在目录
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

# 函数：停止服务
stop_service() {
    local service_name=$1
    local port=$2
    local pid_file=$3
    
    printf "停止 %s (端口 %s)... " "$service_name" "$port"
    
    # 首先尝试使用PID文件停止
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            rm -f "$pid_file"
            echo "${GREEN}[已停止]${NC} PID: $pid"
            return 0
        else
            rm -f "$pid_file"
        fi
    fi
    
    # 尝试通过端口查找进程
    local found=0
    
    # 方法1: 使用netstat
    if command -v netstat >/dev/null 2>&1; then
        # 尝试查找监听端口的进程
        local pids=$(netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $NF}' | cut -d'/' -f1)
        if [ -n "$pids" ]; then
            for pid in $pids; do
                if [ "$pid" != "-" ] && [ -n "$pid" ]; then
                    kill "$pid" 2>/dev/null && found=1
                    echo "${GREEN}[已停止]${NC} PID: $pid"
                fi
            done
        fi
    fi
    
    # 方法2: 使用ss
    if [ $found -eq 0 ] && command -v ss >/dev/null 2>&1; then
        local pids=$(ss -tlnp 2>/dev/null | grep ":$port " | grep -o 'pid=[0-9]*' | cut -d= -f2)
        if [ -n "$pids" ]; then
            for pid in $pids; do
                kill "$pid" 2>/dev/null && found=1
                echo "${GREEN}[已停止]${NC} PID: $pid"
            done
        fi
    fi
    
    # 方法3: 使用lsof
    if [ $found -eq 0 ] && command -v lsof >/dev/null 2>&1; then
        local pids=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$pids" ]; then
            for pid in $pids; do
                kill "$pid" 2>/dev/null && found=1
                echo "${GREEN}[已停止]${NC} PID: $pid"
            done
        fi
    fi
    
    # 方法4: 通过进程名查找Python进程
    if [ $found -eq 0 ]; then
        # 查找相关的Python进程
        for cmd in python python3; do
            if command -v $cmd >/dev/null 2>&1; then
                # 使用ps查找
                if command -v ps >/dev/null 2>&1; then
                    local pids=$(ps aux 2>/dev/null | grep "$cmd.*main.py\|$cmd.*server.py\|$cmd.*start.py" | grep -v grep | awk '{print $2}')
                    if [ -n "$pids" ]; then
                        for pid in $pids; do
                            kill "$pid" 2>/dev/null && found=1
                            echo "${GREEN}[已停止]${NC} Python进程 PID: $pid"
                        done
                    fi
                fi
            fi
        done
    fi
    
    if [ $found -eq 0 ]; then
        echo "${YELLOW}[未运行]${NC}"
    fi
}

# 停止各个服务
stop_service "账号池服务" 8019 "data/pool-service.pid"
stop_service "Warp2API服务" 8000 "data/warp2api.pid"
stop_service "OpenAI兼容服务" 8080 "data/openai-compat.pid"

# 额外清理所有相关Python进程
echo
echo "清理残留进程..."

# 查找并终止所有相关Python进程
cleanup_count=0
for script in "main.py" "server.py" "start.py"; do
    if command -v pkill >/dev/null 2>&1; then
        pkill -f "$script" 2>/dev/null && cleanup_count=$((cleanup_count + 1))
    elif command -v killall >/dev/null 2>&1; then
        killall -r ".*$script.*" 2>/dev/null && cleanup_count=$((cleanup_count + 1))
    else
        # 手动查找和终止
        if command -v ps >/dev/null 2>&1; then
            pids=$(ps aux 2>/dev/null | grep "$script" | grep -v grep | awk '{print $2}')
            for pid in $pids; do
                kill "$pid" 2>/dev/null && cleanup_count=$((cleanup_count + 1))
            done
        fi
    fi
done

if [ $cleanup_count -gt 0 ]; then
    echo "  已清理 $cleanup_count 个相关进程"
fi

# 清理PID文件
rm -f data/*.pid 2>/dev/null

echo
echo "${GREEN}✅ 所有服务已停止${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查端口状态
echo
echo "端口状态检查:"
for port in 8019 8000 8080; do
    port_used=0
    
    # 检查端口是否仍被占用
    if command -v netstat >/dev/null 2>&1; then
        netstat -tln 2>/dev/null | grep -q ":$port " && port_used=1
    elif command -v ss >/dev/null 2>&1; then
        ss -tln 2>/dev/null | grep -q ":$port " && port_used=1
    fi
    
    if [ $port_used -eq 1 ]; then
        echo "  端口 $port: ${RED}✗ 仍被占用${NC}"
    else
        echo "  端口 $port: ${GREEN}✓ 已释放${NC}"
    fi
done

echo
