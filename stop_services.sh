#!/bin/bash
# 停止所有服务

set -e

echo "========================================"
echo "Stopping Warp2API Services"
echo "========================================"

# 停止服务
if [ -f logs/pool-service.pid ]; then
    PID=$(cat logs/pool-service.pid)
    echo "Stopping Account Pool Service (PID: $PID)..."
    kill $PID 2>/dev/null || true
    rm logs/pool-service.pid
    echo "Account Pool Service stopped."
else
    echo "Account Pool Service not running or PID file not found."
fi

if [ -f logs/warp2api.pid ]; then
    PID=$(cat logs/warp2api.pid)
    echo "Stopping Warp2API Service (PID: $PID)..."
    kill $PID 2>/dev/null || true
    rm logs/warp2api.pid
    echo "Warp2API Service stopped."
else
    echo "Warp2API Service not running or PID file not found."
fi

if [ -f logs/openai-compat.pid ]; then
    PID=$(cat logs/openai-compat.pid)
    echo "Stopping OpenAI Compatible Service (PID: $PID)..."
    kill $PID 2>/dev/null || true
    rm logs/openai-compat.pid
    echo "OpenAI Compatible Service stopped."
else
    echo "OpenAI Compatible Service not running or PID file not found."
fi

# 强制停止任何残留的Python进程
echo "Checking for any remaining processes..."
pkill -f "account-pool-service/main.py" 2>/dev/null || true
pkill -f "warp2api-main/server.py" 2>/dev/null || true
pkill -f "warp2api-main/start.py" 2>/dev/null || true

echo ""
echo "========================================"
echo "All services stopped successfully!"
echo "========================================"