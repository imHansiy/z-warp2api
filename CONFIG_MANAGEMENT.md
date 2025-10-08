# 配置管理说明

本项目已将所有硬编码参数提取到配置文件中，提高了配置的灵活性和可维护性。

## 配置文件

### 主要配置文件
- `config/production.env` - 生产环境配置文件，包含所有服务的配置参数

### 配置项说明

#### 账号池服务配置
- `POOL_SERVICE_HOST` - 账号池服务主机地址
- `POOL_SERVICE_PORT` - 账号池服务端口
- `POOL_MIN_SIZE` - 最小账号池大小
- `POOL_MAX_SIZE` - 最大账号池大小
- `BATCH_REGISTER_SIZE` - 批量注册账号数量
- `REGISTER_TIMEOUT` - 注册超时时间（秒）

#### Warp2API服务配置
- `WARP_API_HOST` - Warp API服务主机地址
- `WARP_API_PORT` - Warp API服务端口
- `WARP_URL` - Warp API URL
- `WARP_JWT` - Warp JWT令牌
- `WARP_REFRESH_TOKEN` - Warp刷新令牌
- `CLIENT_VERSION` - 客户端版本
- `OS_CATEGORY` - 操作系统类别
- `OS_NAME` - 操作系统名称
- `OS_VERSION` - 操作系统版本

#### OpenAI兼容服务配置
- `HOST` - OpenAI兼容服务主机地址
- `PORT` - OpenAI兼容服务端口
- `WARP_BRIDGE_URL` - Warp Bridge URL
- `WARP_BRIDGE_HOST` - Warp Bridge主机地址
- `WARP_BRIDGE_PORT` - Warp Bridge端口

#### Firebase配置
- `FIREBASE_API_KEY` - Firebase API密钥
- `FIREBASE_API_KEY_1` - Firebase API密钥1
- `FIREBASE_DEFAULT_API_KEY` - 默认Firebase API密钥
- `FIREBASE_AUTH_URL` - Firebase认证URL

#### 邮箱服务配置
- `MOEMAIL_URL` - MoeMail服务URL
- `MOEMAIL_API_KEY` - MoeMail API密钥
- `MOEMAIL_DOMAIN` - MoeMail域名
- `MOEMAIL_CLIENT_VERSION` - MoeMail客户端版本
- `EMAIL_PREFIX` - 邮箱前缀
- `EMAIL_EXPIRY_HOURS` - 邮箱过期时间（小时）
- `EMAIL_TIMEOUT` - 邮箱超时时间（秒）
- `EMAIL_CHECK_INTERVAL` - 邮箱检查间隔（秒）

#### 代理池配置
- `PROXY_POOL_URL` - 代理池URL
- `USE_PROXY` - 是否使用代理
- `PROXY_MAX_FAIL_COUNT` - 代理最大失败次数
- `PROXY_REFRESH_INTERVAL` - 代理刷新间隔（秒）
- `PROXY_REQUEST_TIMEOUT` - 代理请求超时时间（秒）
- `PROXY_TEST_TIMEOUT` - 代理测试超时时间（秒）
- `PROXY_TEST_URL` - 代理测试URL

#### 数据库配置
- `DATABASE_PATH` - 数据库路径
- `DB_HOST` - 数据库主机
- `DB_PORT` - 数据库端口
- `DB_USERNAME` - 数据库用户名
- `DB_PASSWORD` - 数据库密码
- `DB_NAME` - 数据库名称

#### 会话管理配置
- `SESSION_TIMEOUT_MINUTES` - 会话超时时间（分钟）
- `MAINTENANCE_INTERVAL_SECONDS` - 维护间隔（秒）
- `EMERGENCY_REPLENISH_COUNT` - 紧急补充数量
- `TOKEN_REFRESH_BUFFER_MINUTES` - Token刷新缓冲时间（分钟）

#### 连接池配置
- `HTTP_KEEPALIVE` - HTTP Keep-Alive时间
- `CONNECTION_POOL_SIZE` - 连接池大小
- `RESPONSE_CACHE_TTL` - 响应缓存TTL
- `STREAM_CHUNK_DELAY` - 流响应延迟

#### 安全配置
- `MAX_CONCURRENT_REQUESTS` - 最大并发请求数
- `REQUEST_TIMEOUT` - 请求超时时间
- `ENABLE_AUTH_VALIDATION` - 是否启用认证验证
- `JWT_SECRET_KEY` - JWT密钥

#### 监控配置
- `ENABLE_METRICS` - 是否启用指标
- `METRICS_PORT` - 指标端口

#### 日志配置
- `LOG_LEVEL` - 日志级别
- `LOG_FILE` - 日志文件路径

#### Token管理配置
- `TOKEN_EXPIRY_BUFFER_MINUTES` - Token过期缓冲时间（分钟）
- `TOKEN_REFRESH_TIMEOUT` - Token刷新超时时间
- `TOKEN_REFRESH_BUFFER_MINUTES` - Token刷新缓冲时间（分钟）
- `TOKEN_VALIDITY_CHECK_BUFFER` - Token有效性检查缓冲时间
- `ANON_USER_TIMEOUT` - 匿名用户超时时间
- `IDENTITY_TOOLKIT_TIMEOUT` - Identity Toolkit超时时间
- `ACCESS_TOKEN_TIMEOUT` - 访问令牌超时时间

#### Warp API配置
- `WARP_API_TIMEOUT` - Warp API超时时间

#### 用户代理配置
- `USER_AGENT_1` - 用户代理1
- `USER_AGENT_2` - 用户代理2
- `USER_AGENT_3` - 用户代理3
- `USER_AGENT_4` - 用户代理4

## 使用方法

### 1. 直接运行（使用配置文件）

```bash
# 启动所有服务
./start_with_config.sh

# 停止所有服务
./stop_services.sh
```

### 2. 使用Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止所有服务
docker-compose down
```

### 3. 单独启动服务

#### 账号池服务
```bash
cd account-pool-service
python -c "from dotenv import load_dotenv; load_dotenv('../config/production.env'); exec(open('main.py').read())"
```

#### Warp2API服务
```bash
cd warp2api-main
python -c "from dotenv import load_dotenv; load_dotenv('../config/production.env'); exec(open('server.py').read())"
```

#### OpenAI兼容服务
```bash
cd warp2api-main
python -c "from dotenv import load_dotenv; load_dotenv('../config/production.env'); exec(open('start.py').read())"
```

## 环境变量优先级

1. 命令行设置的环境变量（最高优先级）
2. Docker Compose文件中的environment设置
3. 配置文件（config/production.env）
4. 代码中的默认值（最低优先级）

## 安全注意事项

1. **敏感信息**：配置文件中包含敏感信息（如API密钥、数据库密码），在生产环境中应使用环境变量或密钥管理系统
2. **文件权限**：确保配置文件有适当的权限设置
3. **版本控制**：不要将包含敏感信息的配置文件提交到版本控制系统

## 配置验证

可以使用提供的验证脚本检查配置是否正确：

```bash
python verify_config_changes.py
```

## 故障排除

1. **服务无法启动**：检查配置文件是否存在，格式是否正确
2. **连接错误**：检查URL和端口配置是否正确
3. **认证失败**：检查API密钥和认证相关配置是否正确

## 自定义配置

如需添加新的配置项：

1. 在`config/production.env`中添加新的配置项
2. 在代码中使用`os.getenv()`获取配置值
3. 更新此文档说明新配置项的用途