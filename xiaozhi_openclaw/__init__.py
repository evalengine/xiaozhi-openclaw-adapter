"""OpenClaw工具适配器 - 为小智服务器提供OpenClaw集成功能

此模块提供WebSocket服务器，接收来自OpenClaw插件的工具调用请求，
并通过统一工具处理器执行相应的操作。

支持双向通信：
- OpenClaw → 小智: 通过WebSocket工具调用（device_control, agent_task, send_message）
- 小智 → OpenClaw: 通过WebSocket广播通知（message/send, device/control）
"""

from .websocket_server import OpenClawWebSocketServer, get_server_instance
from .config import OpenClawConfig, get_openclaw_config
from .executor import OpenClawToolExecutor

__all__ = [
    "OpenClawWebSocketServer",
    "get_server_instance",
    "OpenClawConfig",
    "get_openclaw_config",
    "OpenClawToolExecutor",
]
