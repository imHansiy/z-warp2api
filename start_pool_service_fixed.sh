#!/bin/bash
# 修复的账号池服务启动脚本
# 确保正确加载环境变量

echo "🔍 启动账号池服务（修复版）..."

# 设置工作目录
cd "$(dirname "$0")"

# 加载环境变量
if [ -f "./config/production.env" ]; then
    echo "📋 加载环境变量..."
    export $(grep -v '^#' ./config/production.env | xargs)
    echo "✅ 环境变量加载完成"
else
    echo "❌ 配置文件不存在: ./config/production.env"
    exit 1
fi

# 检查关键环境变量
if [ -z "$FIREBASE_API_KEYS" ]; then
    echo "❌ FIREBASE_API_KEYS未设置"
    exit 1
fi

echo "🔑 Firebase API密钥: ${FIREBASE_API_KEYS:0:20}..."

# 启动服务
cd account-pool-service
python main.py
