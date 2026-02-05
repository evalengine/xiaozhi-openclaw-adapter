# xiaozhi-openclaw-adapter

> **小智 ESP32 服务器 OpenClaw 适配器** - 为小智服务器提供 OpenClaw 插件通信能力

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**[English Documentation](README.md)**

## 简介

这是一个 [xiaozhi-esp32-server](https://github.com/xiaozhi-esp32-server) 的附加组件，提供 WebSocket 服务器用于接收来自 OpenClaw 插件的工具调用请求。

当配合 [@dsw0000/xiaozhi](https://github.com/dsw0000/xiaozhi-openclaw-plugin) 插件使用时，可以实现：

- 📤 OpenClaw 通过小智发送消息到各种渠道（Telegram、Discord、微信等）
- 🏠 OpenClaw 控制连接到小智的 IoT 设备
- 🤖 OpenClaw 执行/查询小智 Agent 任务

## 功能特性

- 🔌 **WebSocket 服务器** - 基于 websockets 的异步服务器
- 📡 **JSON-RPC 2.0 协议** - 标准化的远程调用协议
- 🔐 **认证支持** - 可选的 Bearer Token 认证
- 🛠️ **三个工具包装器** - send_message、device_control、agent_task
- 🔧 **统一工具集成** - 与小智现有工具系统无缝集成

## 系统要求

- **Python**: >= 3.8
- **xiaozhi-esp32-server**: 任意版本
- **OpenClaw**: >= 2026.2.0 (配合 @dsw0000/xiaozhi 插件)

## 安装

### 方式一：手动安装（推荐）

```bash
cd /path/to/xiaozhi-esp32-server/main/xiaozhi-server
pip install -e /path/to/xiaozhi-openclaw-adapter
```

### 方式二：从 GitHub 安装

```bash
pip install git+https://github.com/dsw0000/xiaozhi-openclaw-adapter.git
```

### 方式三：开发模式安装

```bash
git clone https://github.com/dsw0000/xiaozhi-openclaw-adapter.git
cd xiaozhi-openclaw-adapter
pip install -e .
```

## 配置

配置文件：`xiaozhi-esp32-server/main/xiaozhi-server/data/.openclaw_adapter_settings.json`

```json
{
  "websocketServer": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": 8080,
    "authToken": null
  }
}
```

### 配置说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `enabled` | boolean | ✅ | true | 是否启用 WebSocket 服务器 |
| `host` | string | ✅ | "0.0.0.0" | 监听地址 |
| `port` | number | ✅ | 8080 | 监听端口 |
| `authToken` | string | ❌ | null | 认证令牌（与插件保持一致） |

## 集成到小智服务器

### 方法一：作为附加组件

将适配器复制到小智服务器的 `tools` 目录：

```bash
cp -r xiaozhi_openclaw /path/to/xiaozhi-esp32-server/main/xiaozhi-server/core/providers/tools/
```

### 方法二：作为独立包安装

```bash
cd /path/to/xiaozhi-esp32-server/main/xiaozhi-server
pip install -e xiaozhi-openclaw-adapter
```

然后修改 `core/providers/tools/__init__.py` 添加导入：

```python
from .openclaw import OpenClawWebSocketServer, get_openclaw_config
```

## WebSocket 服务器

服务器启动后将在 `ws://host:port/ws` 监听连接。

### 通信协议

使用 JSON-RPC 2.0 协议，详见 [@dsw0000/xiaozhi](https://github.com/dsw0000/xiaozhi-openclaw-plugin) 插件文档。

### 支持的方法

- `tools/call` - 执行工具调用
- `ping` - 心跳检测

## 提供的工具

适配器在小智服务器的工具系统中注册以下工具：

### 1. xiaozhi_send_message

发送消息到配置的渠道。

**参数：**
- `to` (string, 必填) - 接收者标识符
- `text` (string, 必填) - 消息内容
- `channel` (string, 可选) - 渠道名称

### 2. xiaozhi_device_control

控制 IoT 设备。

**参数：**
- `deviceId` (string, 必填) - 设备标识符
- `action` (string, 必填) - 操作类型
- `value` (number, 可选) - 设置值

### 3. xiaozhi_agent_task

执行/查询 Agent 任务。

**参数：**
- `action` (string, 必填) - 操作类型
- `taskId` (string, 可选) - 任务 ID
- `prompt` (string, 可选) - 任务提示

## 测试

```bash
# 克隆仓库
git clone https://github.com/dsw0000/xiaozhi-openclaw-adapter.git
cd xiaozhi-openclaw-adapter

# 安装开发依赖
pip install -e ".[test]"

# 运行测试
pytest tests/
```

## 项目结构

```
xiaozhi-openclaw-adapter/
├── xiaozhi_openclaw/
│   ├── __init__.py
│   ├── config.py                 # 配置加载器
│   ├── protocol.py               # JSON-RPC 2.0 协议
│   ├── tool_executor.py          # 工具执行器
│   ├── websocket_server.py       # WebSocket 服务器
│   ├── executor.py               # 统一工具管理器执行器
│   └── tools/
│       ├── __init__.py
│       ├── send_message.py
│       ├── device_control.py
│       └── agent_task.py
├── tests/
│   ├── __init__.py
│   ├── test_protocol.py
│   ├── test_config.py
│   ├── test_tool_executor.py
│   └── TEST_SUMMARY.md
├── setup.py                      # 包配置
├── pyproject.toml                # 现代 Python 项目配置
├── README.md
└── LICENSE
```

## 与 OpenClaw 插件配合使用

### 架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OpenClaw 网关                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  @dsw0000/xiaozhi 插件 (WebSocket 客户端)                  │  │
│  │  - 主动连接到小智 WebSocket 服务器                          │  │
│  │  - 暴露工具给 Agent 使用                                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────────────────┘
                            │
                    ┌───────┴────────┐
                    │  WebSocket     │
                    │  JSON-RPC 2.0  │
                    └───────┬────────┘
                            │
┌───────────────────────────┴──────────────────────────────────────────┐
│                    xiaozhi-esp32-server                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  xiaozhi-openclaw-adapter (WebSocket 服务器)                │  │
│  │  - 监听 ws://host:8080/ws                                   │  │
│  │  - 处理来自 OpenClaw 的工具调用                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 工作流程

```
用户 → 小智说话
     ↓
小智 ASR + Agent 判断
     ↓
需要调用 OpenClaw 工具
     ↓
┌─────────────────────────────────────────────────────────────┐
│ 小智通过统一工具系统调用 OpenClaw 工具                      │
│                                                             │
│ xiaozhi_openclaw.executor:                                   │
│   ├─ 调用工具函数 (send_message, device_control, etc.)      │
│   ├─ 创建任务                                               │
│   └─ 返回结果                                               │
└─────────────────────────────────────────────────────────────┘
     ↓
OpenClaw 执行工具 (发送消息/控制设备/执行任务)
     ↓
结果返回给小智
     ↓
小智 TTS 播报
```

## 故障排查

### WebSocket 服务器无法启动

1. 确认端口未被占用：`lsof -i :8080`
2. 检查防火墙设置
3. 查看小智服务器日志

### OpenClaw 插件无法连接

1. 确认 WebSocket 服务器已启动
2. 检查 `serverUrl` 配置正确
3. 验证 `authToken` 一致（如果使用）

### 工具调用失败

1. 查看小智服务器日志
2. 确认工具已在系统中注册
3. 验证工具参数正确

## 许可证

[MIT](LICENSE)

## 致谢

- [OpenClaw](https://github.com/anthropics/openclaw) - 强大的 AI Agent 网关
- [xiaozhi-esp32-server](https://github.com/xiaozhi-esp32-server) - ESP32 智能硬件服务器

## 相关项目

- [xiaozhi-openclaw-plugin](https://github.com/dsw0000/xiaozhi-openclaw-plugin) - OpenClaw 小智集成插件

## 联系方式

- GitHub Issues: https://github.com/dsw0000/xiaozhi-openclaw-adapter/issues

---

**注意**: 此适配器需要配合 [@dsw0000/xiaozhi](https://github.com/dsw0000/xiaozhi-openclaw-plugin) 插件使用。
