#!/bin/bash
# 使用配置文件启动所有服务

set -e

echo "========================================"
echo "Starting Warp2API with Configuration"
echo "========================================"

# 检查配置文件是否存在
if [ ! -f "config/production.env" ]; then
    echo "ERROR: config/production.env not found!"
    echo "Please create the configuration file first."
    exit 1
fi

echo "Loading configuration from config/production.env..."

# 加载环境变量
export $(cat config/production.env | grep -v '^#' | xargs)

# 创建必要的目录
mkdir -p logs data

echo "Starting Account Pool Service..."
cd account-pool-service
if [ -f main.py ]; then
    python main.py > ../logs/pool-service.log 2>&1 &
    POOL_PID=$!
    echo "Account Pool Service started with PID: $POOL_PID"
else
    echo "WARNING: Account Pool Service not found, skipping..."
fi

cd ..

echo "Starting Warp2API Service..."
cd warp2api-main
if [ -f server.py ]; then
    python server.py > ../logs/warp2api.log 2>&1 &
    WARP_PID=$!
    echo "Warp2API Service started with PID: $WARP_PID"
else
    echo "ERROR: Warp2API service file not found!"
    exit 1
fi

cd ..

echo "Starting OpenAI Compatible Service..."
cd warp2api-main
if [ -f start.py ]; then
    python start.py > ../logs/openai-compat.log 2>&1 &
    OPENAI_PID=$!
    echo "OpenAI Compatible Service started with PID: $OPENAI_PID"
else
    echo "WARNING: OpenAI Compatible Service not found, skipping..."
fi

cd ..

echo ""
echo "========================================"
echo "All services started successfully!"
echo "========================================"
echo "📍 Account Pool:  http://localhost:${POOL_SERVICE_PORT:-8019}"
echo "📍 Warp2API:      http://localhost:${WARP_API_PORT:-8000}"
echo "📍 OpenAI API:    http://localhost:${PORT:-8080}"
echo "========================================"
echo ""
echo "Logs are being written to the logs/ directory"
echo "Press Ctrl+C to stop all services."
echo ""

# 保存PID以便于清理
echo $POOL_PID > logs/pool-service.pid
echo $WARP_PID > logs/warp2api.pid
echo $OPENAI_PID > logs/openai-compat.pid

# 设置信号处理
cleanup() {
    echo ""
    echo "Stopping all services..."
    
    if [ -f logs/pool-service.pid ]; then
        kill $(cat logs/pool-service.pid) 2>/dev/null || true
        rm logs/pool-service.pid
    fi
    
    if [ -f logs/warp2api.pid ]; then
        kill $(cat logs/warp2api.pid) 2>/dev/null || true
        rm logs/warp2api.pid
    fi
    
    if [ -f logs/openai-compat.pid ]; then
        kill $(cat logs/openai-compat.pid) 2>/dev/null || true
        rm logs/openai-compat.pid
    fi
    
    echo "All services stopped."
    exit 0
}

# 捕获中断信号
trap cleanup SIGINT SIGTERM

# 持续显示日志
tail -f logs/*.log