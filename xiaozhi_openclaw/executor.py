"""OpenClaw工具执行器

将OpenClaw工具集成到统一工具管理器中。
"""

from typing import Dict, Any
from ..base import ToolType, ToolDefinition, ToolExecutor
from .config import get_openclaw_config
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class OpenClawToolExecutor(ToolExecutor):
    """OpenClaw工具执行器"""

    def __init__(self, conn):
        """初始化OpenClaw工具执行器

        Args:
            conn: 连接处理器实例
        """
        self.conn = conn
        self.config = get_openclaw_config()

    async def execute(
        self, conn, tool_name: str, arguments: Dict[str, Any]
    ) -> Any:
        """执行OpenClaw工具

        Args:
            conn: 连接处理器
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            ActionResponse对象
        """
        from .tools import send_message, device_control, agent_task

        try:
            if tool_name == "xiaozhi_send_message":
                return await send_message(**arguments)
            elif tool_name == "xiaozhi_device_control":
                return await device_control(**arguments)
            elif tool_name == "xiaozhi_agent_task":
                return await agent_task(**arguments)
            else:
                from plugins_func.register import Action, ActionResponse
                return ActionResponse(
                    action=Action.NOTFOUND,
                    response=f"未知的OpenClaw工具: {tool_name}",
                )

        except Exception as e:
            logger.bind(tag=TAG).error(f"执行OpenClaw工具 {tool_name} 时出错: {e}")
            from plugins_func.register import Action, ActionResponse
            return ActionResponse(
                action=Action.ERROR,
                response=str(e),
            )

    def get_tools(self) -> Dict[str, ToolDefinition]:
        """获取所有OpenClaw工具定义

        Returns:
            工具定义字典
        """
        if not self.config.enabled:
            return {}

        tools = {}

        # xiaozhi_send_message工具
        tools["xiaozhi_send_message"] = ToolDefinition(
            name="xiaozhi_send_message",
            description={
                "type": "function",
                "function": {
                    "name": "xiaozhi_send_message",
                    "description": "Send a message to a configured messaging channel (Telegram, Discord, WeChat, etc.) through the xiaozhi server",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "Recipient identifier (user ID, chat ID, phone number, etc.)",
                            },
                            "text": {
                                "type": "string",
                                "description": "Message content to send",
                            },
                            "channel": {
                                "type": "string",
                                "description": "Channel name (telegram, discord, wechat, etc.). Uses default channel from config if not specified.",
                            },
                        },
                        "required": ["to", "text"],
                    },
                },
            },
            tool_type=ToolType.OPENCLAW,
        )

        # xiaozhi_device_control工具
        tools["xiaozhi_device_control"] = ToolDefinition(
            name="xiaozhi_device_control",
            description={
                "type": "function",
                "function": {
                    "name": "xiaozhi_device_control",
                    "description": "Control IoT devices connected to the xiaozhi server (turn on/off, toggle, set value)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "deviceId": {
                                "type": "string",
                                "description": "Device identifier (e.g., 'light_01', 'switch_bedroom')",
                            },
                            "action": {
                                "type": "string",
                                "enum": ["turn_on", "turn_off", "toggle", "set_value"],
                                "description": "Action to perform on the device",
                            },
                            "value": {
                                "type": "number",
                                "description": "Value to set (0-100, for use with set_value action). Example: 50 for 50% brightness",
                                "minimum": 0,
                                "maximum": 100,
                            },
                        },
                        "required": ["deviceId", "action"],
                    },
                },
            },
            tool_type=ToolType.OPENCLAW,
        )

        # xiaozhi_agent_task工具
        tools["xiaozhi_agent_task"] = ToolDefinition(
            name="xiaozhi_agent_task",
            description={
                "type": "function",
                "function": {
                    "name": "xiaozhi_agent_task",
                    "description": "Execute or query agent tasks on the xiaozhi server (execute a task, check status, or cancel a task)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["execute", "status", "cancel"],
                                "description": "Action to perform on the task",
                            },
                            "taskId": {
                                "type": "string",
                                "description": "Task ID (required for status and cancel actions). Example: 'task_123abc'",
                            },
                            "prompt": {
                                "type": "string",
                                "description": "Task prompt/instruction (required for execute action). Example: 'Summarize the latest chat history'",
                            },
                        },
                        "required": ["action"],
                    },
                },
            },
            tool_type=ToolType.OPENCLAW,
        )

        return tools

    def has_tool(self, tool_name: str) -> bool:
        """检查是否有指定的OpenClaw工具"""
        if not self.config.enabled:
            return False
        return tool_name in ["xiaozhi_send_message", "xiaozhi_device_control", "xiaozhi_agent_task"]
