"""OpenClaw工具执行器

执行来自OpenClaw插件的工具调用请求（OpenClaw → 小智方向）。
"""

from typing import Dict, Any
from .protocol import create_tool_call_result
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class OpenClawToolExecutor:
    """OpenClaw工具执行器（处理来自OpenClaw插件的入站工具调用）"""

    def __init__(self, conn):
        """初始化工具执行器

        Args:
            conn: 连接处理器实例（可为None，工具执行时通过device_id动态路由）
        """
        self.conn = conn

    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行工具调用

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具调用结果字典（JSON-RPC 2.0 result格式）
        """
        try:
            logger.bind(tag=TAG).info(f"执行OpenClaw工具: {tool_name}, 参数: {arguments}")

            if tool_name == "xiaozhi_send_message":
                return await self._execute_send_message(arguments)
            elif tool_name == "xiaozhi_device_control":
                return await self._execute_device_control(arguments)
            elif tool_name == "xiaozhi_agent_task":
                return await self._execute_agent_task(arguments)
            else:
                return create_tool_call_result(
                    success=False,
                    error=f"未知工具: {tool_name}",
                )

        except Exception as e:
            logger.bind(tag=TAG).error(f"执行工具 {tool_name} 时发生错误: {e}")
            return create_tool_call_result(
                success=False,
                error=str(e),
            )

    async def _execute_send_message(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行发送消息工具（OpenClaw → 小智渠道）

        OpenClaw调用此工具时，小智通过内部机制将消息发出。
        实际上此方向（OpenClaw主动发消息）通常由OpenClaw插件自身完成，
        此处的实现是将消息通知广播回所有连接的OpenClaw客户端，
        由OpenClaw插件选择如何处理。
        """
        from .tools.send_message import send_message

        to = arguments.get("to")
        text = arguments.get("text")
        channel = arguments.get("channel")

        if not to or not text:
            return create_tool_call_result(
                success=False,
                error="缺少必需参数: to, text",
            )

        action_response = await send_message(to=to, text=text, channel=channel)

        from plugins_func.register import Action
        if action_response.action in (Action.RESPONSE, Action.REQLLM):
            return create_tool_call_result(
                success=True,
                data={"message": action_response.response, "to": to, "channel": channel or "default"},
            )
        else:
            return create_tool_call_result(
                success=False,
                error=action_response.response or "发送失败",
            )

    async def _execute_device_control(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行设备控制工具（OpenClaw → 小智 → IoT设备）

        通过小智HTTP chat API，将设备控制指令转为自然语言发送给目标设备。
        """
        from .tools.device_control import device_control

        device_id = arguments.get("deviceId")
        action = arguments.get("action")
        value = arguments.get("value")
        xiaozhi_device_id = arguments.get("xiaozhi_device_id")

        if not device_id or not action:
            return create_tool_call_result(
                success=False,
                error="缺少必需参数: deviceId, action",
            )

        action_response = await device_control(
            deviceId=device_id,
            action=action,
            value=value,
            xiaozhi_device_id=xiaozhi_device_id,
        )

        from plugins_func.register import Action
        if action_response.action in (Action.RESPONSE, Action.REQLLM):
            return create_tool_call_result(
                success=True,
                data={"result": action_response.response, "deviceId": device_id, "action": action},
            )
        else:
            return create_tool_call_result(
                success=False,
                error=action_response.response or "设备控制失败",
            )

    async def _execute_agent_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行Agent任务工具（OpenClaw → 小智LLM Agent）

        通过小智HTTP chat API提交任务并异步追踪结果。
        """
        from .tools.agent_task import agent_task

        action = arguments.get("action")
        task_id = arguments.get("taskId")
        prompt = arguments.get("prompt")
        device_id = arguments.get("device_id")

        if not action:
            return create_tool_call_result(
                success=False,
                error="缺少必需参数: action",
            )

        action_response = await agent_task(
            action=action,
            task_id=task_id,
            prompt=prompt,
            device_id=device_id,
        )

        from plugins_func.register import Action
        if action_response.action in (Action.RESPONSE, Action.REQLLM):
            return create_tool_call_result(
                success=True,
                data={"result": action_response.response},
            )
        elif action_response.action == Action.NOTFOUND:
            return create_tool_call_result(
                success=False,
                error=action_response.response or "任务不存在",
            )
        else:
            return create_tool_call_result(
                success=False,
                error=action_response.response or "任务操作失败",
            )
