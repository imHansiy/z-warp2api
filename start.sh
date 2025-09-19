#!/bin/bash
# Warp2API 一键启动脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 打印Logo
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║           Warp2API with Account Pool Service        ║"
echo "║                    一键启动脚本                     ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 设置环境变量
export POOL_SERVICE_URL="http://localhost:8019"
export USE_POOL_SERVICE="true"
export LOG_LEVEL="INFO"

# 创建日志目录
mkdir -p logs

# 函数：检查Python环境
check_python() {
    echo -e "${YELLOW}🔍 检查Python环境...${NC}"
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ 未找到Python3，请先安装Python3${NC}"
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    echo -e "${GREEN}✓ Python版本: $python_version${NC}"
}

# 函数：检查并安装依赖
install_dependencies() {
    echo -e "${YELLOW}📦 检查并安装依赖...${NC}"
    
    # 账号池服务依赖
    if [ -d "account-pool-service" ]; then
        echo "  安装账号池服务依赖..."
        cd account-pool-service
        if [ -f "requirements.txt" ]; then
            pip3 install -q -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt
        fi
        cd ..
    fi
    
    # Warp2API主服务依赖
    if [ -d "warp2api-main" ]; then
        echo "  安装Warp2API服务依赖..."
        cd warp2api-main
        if [ -f "requirements.txt" ]; then
            pip3 install -q -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt
        fi
        if [ -f "uv.lock" ] && command -v uv &> /dev/null; then
            echo "  使用uv安装依赖..."
            uv pip install -q -r requirements.txt 2>/dev/null || true
        fi
        cd ..
    fi
    
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
}

# 函数：检查端口占用
check_port() {
    local port=$1
    local name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  端口 $port 已被占用 ($name)${NC}"
        echo -n "是否要结束占用端口的进程? [y/N]: "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            kill $(lsof -ti:$port) 2>/dev/null
            sleep 1
            echo -e "${GREEN}✓ 已结束占用端口 $port 的进程${NC}"
        else
            echo -e "${RED}❌ 无法启动 $name，端口被占用${NC}"
            return 1
        fi
    fi
    return 0
}

# 函数：启动账号池服务
start_pool_service() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}1️⃣  启动账号池服务...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    check_port 8019 "账号池服务" || return 1
    
    cd account-pool-service
    
    # 启动服务
    nohup python3 main.py > ../logs/pool-service.log 2>&1 &
    local pid=$!
    echo "  PID: $pid"
    
    # 等待服务启动
    echo -n "  等待服务就绪"
    for i in {1..15}; do
        if curl -s http://localhost:8019/health > /dev/null 2>&1; then
            echo ""
            echo -e "${GREEN}✓ 账号池服务已启动 (http://localhost:8019)${NC}"
            
            # 获取账号池状态
            status=$(curl -s http://localhost:8019/api/accounts/status 2>/dev/null)
            if [ $? -eq 0 ]; then
                available=$(echo $status | python3 -c "import sys, json; print(json.load(sys.stdin).get('pool_stats', {}).get('available', 0))" 2>/dev/null || echo "0")
                total=$(echo $status | python3 -c "import sys, json; print(json.load(sys.stdin).get('pool_stats', {}).get('total', 0))" 2>/dev/null || echo "0")
                echo -e "  ${GREEN}📊 账号状态: 可用 $available / 总计 $total${NC}"
                
                if [ "$available" = "0" ] && [ "$total" = "0" ]; then
                    echo -e "  ${YELLOW}⚠️  账号池为空，正在自动注册账号...${NC}"
                    echo -e "  ${YELLOW}   请稍等，首次启动需要1-2分钟注册账号${NC}"
                fi
            fi
            
            cd ..
            return 0
        fi
        echo -n "."
        sleep 1
    done
    
    echo ""
    echo -e "${RED}❌ 账号池服务启动失败，请检查日志: logs/pool-service.log${NC}"
    cd ..
    return 1
}

# 函数：启动Warp2API服务
start_warp2api() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}2️⃣  启动Warp2API服务...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    check_port 8000 "Warp2API服务" || return 1
    
    cd warp2api-main
    
    # 启动服务
    if [ -f "server.py" ]; then
        nohup python3 server.py > ../logs/warp2api.log 2>&1 &
    elif [ -f "main.py" ]; then
        nohup python3 main.py > ../logs/warp2api.log 2>&1 &
    else
        echo -e "${RED}❌ 找不到启动文件${NC}"
        cd ..
        return 1
    fi
    
    local pid=$!
    echo "  PID: $pid"
    
    # 等待服务启动
    echo -n "  等待服务就绪"
    for i in {1..15}; do
        if curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
            echo ""
            echo -e "${GREEN}✓ Warp2API服务已启动 (http://localhost:8000)${NC}"
            cd ..
            return 0
        fi
        echo -n "."
        sleep 1
    done
    
    echo ""
    echo -e "${YELLOW}⚠️  Warp2API服务启动较慢，请查看日志: logs/warp2api.log${NC}"
    cd ..
    return 0
}

# 函数：显示服务状态
show_status() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}📊 服务状态${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # 检查账号池服务
    if curl -s http://localhost:8019/health > /dev/null 2>&1; then
        status=$(curl -s http://localhost:8019/api/accounts/status 2>/dev/null)
        if [ $? -eq 0 ]; then
            health=$(echo $status | python3 -c "import sys, json; print(json.load(sys.stdin).get('health', 'unknown'))" 2>/dev/null || echo "unknown")
            available=$(echo $status | python3 -c "import sys, json; print(json.load(sys.stdin).get('pool_stats', {}).get('available', 0))" 2>/dev/null || echo "0")
            total=$(echo $status | python3 -c "import sys, json; print(json.load(sys.stdin).get('pool_stats', {}).get('total', 0))" 2>/dev/null || echo "0")
            echo -e "🔹 账号池服务:  ${GREEN}✓ 运行中${NC}"
            echo -e "   健康度: $health | 可用账号: $available/$total"
        else
            echo -e "🔹 账号池服务:  ${GREEN}✓ 运行中${NC}"
        fi
    else
        echo -e "🔹 账号池服务:  ${RED}✗ 未运行${NC}"
    fi
    
    # 检查Warp2API服务
    if curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
        echo -e "🔹 Warp2API服务: ${GREEN}✓ 运行中${NC}"
    else
        echo -e "🔹 Warp2API服务: ${RED}✗ 未运行${NC}"
    fi
}

# 函数：显示使用说明
show_usage() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎯 快速使用${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "📝 API端点:"
    echo "  • Warp2API: http://localhost:8000"
    echo "  • 账号池服务: http://localhost:8019"
    echo ""
    echo "🔧 常用命令:"
    echo "  • 查看账号池状态:"
    echo "    curl http://localhost:8019/api/accounts/status | jq"
    echo ""
    echo "  • 测试Protobuf编码:"
    echo "    curl -X POST http://localhost:8000/api/encode -H 'Content-Type: application/json' \\"
    echo "      -d '{\"message_type\":\"warp.multi_agent.v1.AgentRequest\",\"json_data\":{}}'"
    echo ""
    echo "  • 查看日志:"
    echo "    tail -f logs/pool-service.log  # 账号池日志"
    echo "    tail -f logs/warp2api.log      # 主服务日志"
    echo ""
    echo "  • 停止服务:"
    echo "    ./stop.sh"
    echo ""
    echo "  • 运行测试:"
    echo "    python3 tests/test_integration.py"
}

# 主函数
main() {
    # 检查环境
    check_python
    
    # 安装依赖
    install_dependencies
    
    echo ""
    echo -e "${GREEN}🚀 开始启动服务...${NC}"
    echo ""
    
    # 启动账号池服务
    if ! start_pool_service; then
        echo -e "${RED}❌ 启动失败${NC}"
        exit 1
    fi
    
    echo ""
    
    # 启动Warp2API服务
    if ! start_warp2api; then
        echo -e "${RED}❌ 启动失败${NC}"
        exit 1
    fi
    
    echo ""
    
    # 显示状态
    show_status
    
    echo ""
    
    # 显示使用说明
    show_usage
    
    echo ""
    echo -e "${GREEN}✨ 所有服务已成功启动！${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 执行主函数
main