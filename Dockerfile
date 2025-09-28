# 多阶段构建 - Warp2API完整服务
FROM python:3.12-slim as base

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

# 升级pip
RUN pip install --upgrade pip setuptools wheel

# 复制整个项目
COPY . /app/

# 安装Python依赖
# 账号池服务依赖
RUN if [ -f "account-pool-service/requirements.txt" ]; then \
        pip install -r account-pool-service/requirements.txt; \
    fi

# Warp2API主服务依赖（使用pyproject.toml）
RUN if [ -f "warp2api-main/pyproject.toml" ]; then \
        cd warp2api-main && \
        pip install . ; \
        cd .. ; \
    fi

# 创建必要的目录
RUN mkdir -p /app/logs /app/data

# 暴露端口
EXPOSE 8000 8010 8019 9090

# 启动脚本 - 简化版，移除健康检查等待
RUN echo '#!/bin/sh\n\
echo "Starting Warp2API Services..."\n\
\n\
# 加载环境变量\n\
if [ -f /app/config/production.env ]; then\n\
    export $(cat /app/config/production.env | grep -v "^#" | xargs)\n\
fi\n\
\n\
# 启动账号池服务\n\
echo "Starting Account Pool Service on port 8019..."\n\
cd /app/account-pool-service\n\
python main.py > /app/logs/pool-service.log 2>&1 &\n\
POOL_PID=$!\n\
echo "Account Pool Service PID: $POOL_PID"\n\
\n\
# 等待几秒让服务初始化\n\
sleep 10\n\
\n\
# 启动Warp2API主服务\n\
echo "Starting Warp2API Service on port 8000..."\n\
cd /app/warp2api-main\n\
if [ -f server.py ]; then\n\
    python server.py > /app/logs/warp2api.log 2>&1 &\n\
elif [ -f main.py ]; then\n\
    python main.py > /app/logs/warp2api.log 2>&1 &\n\
fi\n\
WARP_PID=$!\n\
echo "Warp2API Service PID: $WARP_PID"\n\
\n\
# 等待几秒让服务初始化\n\
sleep 10\n\
\n\
# 启动OpenAI兼容服务\n\
echo "Starting OpenAI Compatible Service on port 8010..."\n\
cd /app/warp2api-main\n\
export HOST=0.0.0.0\n\
export PORT=8010\n\
export WARP_BRIDGE_URL=http://localhost:8000\n\
python start.py > /app/logs/openai-compat.log 2>&1 &\n\
OPENAI_PID=$!\n\
echo "OpenAI Compatible Service PID: $OPENAI_PID"\n\
\n\
# 显示服务状态\n\
echo ""\n\
echo "======================================"\n\
echo "All services started!"\n\
echo "======================================"\n\
echo "🔹 Account Pool Service: http://localhost:8019"\n\
echo "🔹 Warp2API Service: http://localhost:8000"\n\
echo "🔹 OpenAI Compatible API: http://0.0.0.0:8010"\n\
echo "======================================"\n\
echo ""\n\
echo "Tailing logs..."\n\
\n\
# 保持容器运行并显示日志\n\
tail -f /app/logs/*.log' > /app/start.sh && \
    chmod +x /app/start.sh

# 启动命令
CMD ["/app/start.sh"]
