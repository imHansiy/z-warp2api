# Warp2API完整服务 - 修复版
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 升级pip并安装所有Python依赖
RUN pip install --upgrade pip setuptools wheel && \
    pip install --root-user-action=ignore \
    "fastapi[standard]" \
    "uvicorn[standard]" \
    "httpx[http2]" \
    protobuf \
    grpcio-tools \
    python-dotenv \
    "websockets>=15.0.1" \
    "requests>=2.32.5" \
    "openai>=1.106.0" \
    aiohttp \
    pydantic \
    PyYAML \
    redis \
    sqlalchemy \
    psycopg2-binary

# 复制整个项目
COPY . /app/

# 如果账号池服务有额外依赖，安装它们
RUN if [ -f "account-pool-service/requirements.txt" ]; then \
        pip install --root-user-action=ignore -r account-pool-service/requirements.txt; \
    fi

# 创建必要的目录
RUN mkdir -p /app/logs /app/data

# 设置Python路径
ENV PYTHONPATH=/app/warp2api-main:/app/account-pool-service:$PYTHONPATH

# 暴露端口
EXPOSE 8000 8010 8019 8080

# 创建启动脚本
RUN cat > /app/start.sh << 'EOF'
#!/bin/sh
set -e

echo "========================================"
echo "Starting Warp2API Production Services"
echo "========================================"

# 加载环境变量
if [ -f /app/config/production.env ]; then
    echo "Loading production environment from /app/config/production.env..."
    # 使用dotenv加载环境变量，保留已有的环境变量
    python -c "from dotenv import load_dotenv; load_dotenv('/app/config/production.env'); print('Environment variables loaded successfully')"
else
    echo "WARNING: /app/config/production.env not found, using default values"
fi

# 启动账号池服务
echo "[1/3] Starting Account Pool Service..."
cd /app/account-pool-service
if [ -f main.py ]; then
    python main.py > /app/logs/pool-service.log 2>&1 &
    echo "      PID: $!"
else
    echo "      WARNING: Account Pool Service not found, skipping..."
fi

# 等待初始化
sleep 5

# 启动Warp2API主服务
echo "[2/3] Starting Warp2API Service..."
cd /app/warp2api-main
if [ -f server.py ]; then
    python server.py > /app/logs/warp2api.log 2>&1 &
    echo "      PID: $!"
elif [ -f main.py ]; then
    python main.py > /app/logs/warp2api.log 2>&1 &
    echo "      PID: $!"
else
    echo "      ERROR: Warp2API service file not found!"
fi

# 等待初始化
sleep 5

# 启动OpenAI兼容服务
echo "[3/3] Starting OpenAI Compatible Service..."
cd /app/warp2api-main
# 在Docker环境中使用容器内网络
export HOST=0.0.0.0
export PORT=8080
export WARP_BRIDGE_URL=http://localhost:8000
if [ -f start.py ]; then
    python start.py > /app/logs/openai-compat.log 2>&1 &
    echo "      PID: $!"
else
    echo "      WARNING: OpenAI Compatible Service not found, skipping..."
fi

echo ""
echo "========================================"
echo "All services started successfully!"
echo "========================================"
echo "📍 Account Pool:  http://localhost:8019"
echo "📍 Warp2API:      http://localhost:8000"
echo "📍 OpenAI API:    http://0.0.0.0:8080"
echo "========================================"
echo ""
echo "Monitoring logs..."
echo "Press Ctrl+C to stop all services."
echo ""

# 创建日志文件（如果不存在）
touch /app/logs/pool-service.log /app/logs/warp2api.log /app/logs/openai-compat.log

# 持续显示日志
tail -f /app/logs/*.log
EOF

RUN chmod +x /app/start.sh

# 启动命令
CMD ["/app/start.sh"]
