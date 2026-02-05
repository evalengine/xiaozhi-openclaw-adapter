"""OpenClaw工具包装器

提供OpenClaw工具调用的包装函数，便于从其他模块调用。
"""

from .send_message import send_message
from .device_control import device_control
from .agent_task import agent_task

__all__ = ["send_message", "device_control", "agent_task"]
