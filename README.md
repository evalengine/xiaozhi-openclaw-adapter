# xiaozhi-openclaw-adapter

> **Xiaozhi ESP32 Server OpenClaw Adapter** - Provides OpenClaw plugin communication capabilities for xiaozhi-esp32-server

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**[中文文档](README_zh.md)**

## Overview

This is an add-on component for [xiaozhi-esp32-server](https://github.com/xiaozhi-esp32-server) that provides a WebSocket server to receive tool call requests from OpenClaw plugins.

When used with the [@dsw0000/xiaozhi](https://github.com/dsw0000/xiaozhi-openclaw-plugin) plugin, it enables:

- 📤 OpenClaw to send messages via Xiaozhi to various channels (Telegram, Discord, WeChat, etc.)
- 🏠 OpenClaw to control IoT devices connected to Xiaozhi
- 🤖 OpenClaw to execute/query Xiaozhi Agent tasks

## Features

- 🔌 **WebSocket Server** - Async server based on websockets
- 📡 **JSON-RPC 2.0 Protocol** - Standardized remote call protocol
- 🔐 **Authentication Support** - Optional Bearer Token authentication
- 🛠️ **Three Tool Wrappers** - send_message, device_control, agent_task
- 🔧 **Unified Tool Integration** - Seamlessly integrates with Xiaozhi's existing tool system

## Requirements

- **Python**: >= 3.8
- **xiaozhi-esp32-server**: Any version
- **OpenClaw**: >= 2026.2.0 (used with @dsw0000/xiaozhi plugin)

## Installation

### Method 1: Manual Installation (Recommended)

```bash
cd /path/to/xiaozhi-esp32-server/main/xiaozhi-server
pip install -e /path/to/xiaozhi-openclaw-adapter
```

### Method 2: Install from GitHub

```bash
pip install git+https://github.com/dsw0000/xiaozhi-openclaw-adapter.git
```

### Method 3: Development Mode Installation

```bash
git clone https://github.com/dsw0000/xiaozhi-openclaw-adapter.git
cd xiaozhi-openclaw-adapter
pip install -e .
```

## Configuration

Config file: `xiaozhi-esp32-server/main/xiaozhi-server/data/.openclaw_adapter_settings.json`

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

### Configuration Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `enabled` | boolean | ✅ | true | Whether to enable WebSocket server |
| `host` | string | ✅ | "0.0.0.0" | Listen address |
| `port` | number | ✅ | 8080 | Listen port |
| `authToken` | string | ❌ | null | Authentication token (keep consistent with plugin) |

## Integration with Xiaozhi Server

### Method 1: As an Add-on Component

Copy the adapter to the `tools` directory of the Xiaozhi server:

```bash
cp -r xiaozhi_openclaw /path/to/xiaozhi-esp32-server/main/xiaozhi-server/core/providers/tools/
```

### Method 2: Install as a Standalone Package

```bash
cd /path/to/xiaozhi-esp32-server/main/xiaozhi-server
pip install -e xiaozhi-openclaw-adapter
```

Then modify `core/providers/tools/__init__.py` to add imports:

```python
from .openclaw import OpenClawWebSocketServer, get_openclaw_config
```

## WebSocket Server

After the server starts, it will listen on `ws://host:port/ws`.

### Communication Protocol

Uses JSON-RPC 2.0 protocol. See [@dsw0000/xiaozhi](https://github.com/dsw0000/xiaozhi-openclaw-plugin) plugin documentation for details.

### Supported Methods

- `tools/call` - Execute tool calls
- `ping` - Heartbeat detection

## Provided Tools

The adapter registers the following tools in the Xiaozhi server's tool system:

### 1. xiaozhi_send_message

Send a message to a configured channel.

**Parameters:**
- `to` (string, required) - Recipient identifier
- `text` (string, required) - Message content
- `channel` (string, optional) - Channel name

### 2. xiaozhi_device_control

Control IoT devices.

**Parameters:**
- `deviceId` (string, required) - Device identifier
- `action` (string, required) - Action type
- `value` (number, optional) - Value to set

### 3. xiaozhi_agent_task

Execute/query Agent tasks.

**Parameters:**
- `action` (string, required) - Action type
- `taskId` (string, optional) - Task ID
- `prompt` (string, optional) - Task prompt

## Testing

```bash
# Clone repository
git clone https://github.com/dsw0000/xiaozhi-openclaw-adapter.git
cd xiaozhi-openclaw-adapter

# Install development dependencies
pip install -e ".[test]"

# Run tests
pytest tests/
```

## Project Structure

```
xiaozhi-openclaw-adapter/
├── xiaozhi_openclaw/
│   ├── __init__.py
│   ├── config.py                 # Configuration loader
│   ├── protocol.py               # JSON-RPC 2.0 protocol
│   ├── tool_executor.py          # Tool executor
│   ├── websocket_server.py       # WebSocket server
│   ├── executor.py               # Unified tool manager executor
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
├── setup.py                      # Package configuration
├── pyproject.toml                # Modern Python project configuration
├── README.md
└── LICENSE
```

## Usage with OpenClaw Plugin

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OpenClaw Gateway                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  @dsw0000/xiaozhi Plugin (WebSocket Client)                │  │
│  │  - Actively connects to Xiaozhi WebSocket server            │  │
│  │  - Exposes tools for Agent use                              │  │
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
│  │  xiaozhi-openclaw-adapter (WebSocket Server)                │  │
│  │  - Listens on ws://host:8080/ws                             │  │
│  │  - Handles tool calls from OpenClaw                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Workflow

```
User → Speak to Xiaozhi
     ↓
Xiaozhi ASR + Agent determines intent
     ↓
Need to call OpenClaw tool
     ↓
┌─────────────────────────────────────────────────────────────┐
│ Xiaozhi calls OpenClaw tool via unified tool system         │
│                                                             │
│ xiaozhi_openclaw.executor:                                   │
│   ├─ Call tool function (send_message, device_control, etc.)│
│   ├─ Create task                                            │
│   └─ Return result                                          │
└─────────────────────────────────────────────────────────────┘
     ↓
OpenClaw executes tool (send message/control device/execute task)
     ↓
Result returns to Xiaozhi
     ↓
Xiaozhi TTS broadcast
```

## Troubleshooting

### WebSocket server cannot start

1. Confirm port is not in use: `lsof -i :8080`
2. Check firewall settings
3. Check Xiaozhi server logs

### OpenClaw plugin cannot connect

1. Confirm WebSocket server is running
2. Check `serverUrl` configuration is correct
3. Verify `authToken` matches (if used)

### Tool call failed

1. Check Xiaozhi server logs
2. Confirm tool is registered in the system
3. Verify tool parameters are correct

## License

[MIT](LICENSE)

## Acknowledgments

- [OpenClaw](https://github.com/anthropics/openclaw) - Powerful AI Agent gateway
- [xiaozhi-esp32-server](https://github.com/xiaozhi-esp32-server) - ESP32 smart hardware server

## Related Projects

- [xiaozhi-openclaw-plugin](https://github.com/dsw0000/xiaozhi-openclaw-plugin) - OpenClaw plugin for xiaozhi integration

## Contact

- GitHub Issues: https://github.com/dsw0000/xiaozhi-openclaw-adapter/issues

---

**Note**: This adapter needs to be used with the [@dsw0000/xiaozhi](https://github.com/dsw0000/xiaozhi-openclaw-plugin) plugin.
