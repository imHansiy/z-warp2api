# Warp2API with Account Pool Service

一个完整的Warp AI API代理服务，包含独立的账号池管理系统。

## 🌟 特性

- **账号池服务**: 独立的微服务架构，自动管理Warp账号
- **Protobuf编解码**: 提供JSON与Protobuf之间的转换
- **自动账号管理**: 自动注册、刷新和维护账号池
- **并发安全**: 支持多进程并发调用，线程安全
- **智能降级**: 账号池不可用时自动降级到临时账号
- **RESTful API**: 标准的HTTP接口，易于集成

## 📁 项目结构

```
warp2api/
├── account-pool-service/    # 账号池服务
│   ├── main.py             # 服务入口
│   ├── config.py           # 配置文件
│   └── account_pool/       # 核心模块
├── warp2api-main/          # Warp2API主服务
│   ├── server.py           # 服务入口
│   └── warp2protobuf/      # Protobuf处理
├── tests/                  # 测试文件
├── logs/                   # 日志目录
├── start.sh               # 一键启动脚本
└── stop.sh                # 停止脚本
```

## 🚀 快速开始

### 1. 安装依赖

确保已安装 Python 3.8+

### 2. 配置服务

```bash
# 复制配置文件模板（如果需要）
cp config/production.env.example config/production.env

# 编辑配置文件
nano config/production.env
```

### 3. 启动服务

#### 方法一：使用配置文件启动（推荐）
```bash
# 使用配置文件启动所有服务
./start_with_config.sh

# 停止所有服务
./stop_services.sh
```

#### 方法二：使用Docker Compose
```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止所有服务
docker-compose down
```

#### 方法三：传统启动方式
```bash
# 一键启动所有服务
./start.sh

# 停止所有服务
./stop.sh
```

服务将在以下端口运行：
- **Warp2API**: http://localhost:8000
- **OpenAI兼容API**: http://localhost:8080
- **账号池服务**: http://localhost:8019
- **监控指标**: http://localhost:9090（如果启用）

### 4. 停止服务

```bash
# 如果使用配置文件启动
./stop_services.sh

# 如果使用Docker Compose
docker-compose down

# 如果使用传统方式
./stop.sh
```

## 📝 API 使用

### 账号池服务 API

#### 查看账号池状态
```bash
curl http://localhost:8019/api/accounts/status | jq
```

#### 分配账号
```bash
curl -X POST http://localhost:8019/api/accounts/allocate \
  -H "Content-Type: application/json" \
  -d '{"count": 1}'
```

### Warp2API 服务

#### Protobuf 编码
```bash
curl -X POST http://localhost:8000/api/encode \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "warp.multi_agent.v1.AgentRequest",
    "json_data": {
      "version": 7,
      "thread_id": "test_thread",
      "user_message": {
        "content": "Hello!",
        "user_message_type": "USER_MESSAGE_TYPE_CHAT"
      }
    }
  }'
```

#### Protobuf 解码
```bash
curl -X POST http://localhost:8000/api/decode \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "warp.multi_agent.v1.ResponseEvent",
    "protobuf_bytes": "base64_encoded_data"
  }'
```

## 🧪 测试

运行集成测试：
```bash
python3 tests/test_integration.py
```

运行账号池测试：
```bash
python3 tests/test_pool_service.py
```

## 📊 监控

### 查看日志
```bash
# 账号池服务日志
tail -f logs/pool-service.log

# Warp2API服务日志
tail -f logs/warp2api.log

# 查看所有日志
tail -f logs/*.log
```

### 服务状态检查
```bash
# 账号池健康检查
curl http://localhost:8019/health

# Warp2API健康检查
curl http://localhost:8000/healthz
```

## ⚙️ 配置

本项目已将所有硬编码参数提取到配置文件中，提高了配置的灵活性和可维护性。

### 配置文件

所有配置参数都集中在 `config/production.env` 文件中，包括：

- 账号池服务配置
- Warp2API服务配置
- OpenAI兼容服务配置
- Firebase配置
- 邮箱服务配置
- 代理池配置
- 数据库配置
- 会话管理配置
- 连接池配置
- 安全配置
- 监控配置
- 日志配置

详细的配置说明请参考：[配置管理文档](CONFIG_MANAGEMENT.md)

### 环境变量优先级

1. 命令行设置的环境变量（最高优先级）
2. Docker Compose文件中的environment设置
3. 配置文件（config/production.env）
4. 代码中的默认值（最低优先级）

### 配置验证

```bash
# 验证配置是否正确
python verify_config_changes.py
```

## 🔧 故障排查

### 服务无法启动
1. 检查端口是否被占用: `lsof -i:8000` 和 `lsof -i:8019`
2. 查看日志文件了解详细错误
3. 确保Python依赖已正确安装

### 账号池为空
- 首次启动时需要1-2分钟注册账号
- 检查日志确认注册是否成功
- 可手动补充账号：
  ```bash
  curl -X POST http://localhost:8019/api/accounts/replenish \
    -d '{"count": 10}'
  ```

### Token过期
- 账号池会自动刷新即将过期的Token
- 遵守1小时刷新限制，防止账号被封

## 📄 License

MIT

## 🤝 贡献

欢迎提交Issue和Pull Request！