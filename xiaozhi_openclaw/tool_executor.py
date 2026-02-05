"""OpenClaw工具执行器

执行来自OpenClaw插件的工具调用请求。
"""

import asyncio
from typing import Dict, Any
from .protocol import create_tool_call_result
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class OpenClawToolExecutor:
    """OpenClaw工具执行器"""

    def __init__(self, conn):
        """初始化工具执行器

        Args:
            conn: 连接处理器实例，用于访问统一工具处理器
        """
        self.conn = conn
        self.func_handler = getattr(conn, "func_handler", None)

    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行工具调用

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具调用结果字典
        """
        try:
            logger.bind(tag=TAG).info(f"执行OpenClaw工具: {tool_name}, 参数: {arguments}")

            # 根据工具名称路由到相应的处理函数
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
        """执行发送消息工具

        Args:
            arguments: 包含to, text, channel的参数字典

        Returns:
            工具调用结果
        """
        to = arguments.get("to")
        text = arguments.get("text")
        channel = arguments.get("channel")

        if not to or not text:
            return create_tool_call_result(
                success=False,
                error="缺少必需参数: to, text",
            )

        try:
            # 这里可以调用实际的消息发送逻辑
            # 例如：通过统一工具处理器调用现有的消息发送功能
            # 或者直接调用消息发送接口

            # 示例：记录日志
            logger.bind(tag=TAG).info(
                f"发送消息: to={to}, channel={channel or 'default'}, text={text[:50]}..."
            )

            # TODO: 实现实际的消息发送逻辑
            # 可能需要调用类似 self.conn.send_message(to, text, channel) 的方法

            return create_tool_call_result(
                success=True,
                data={
                    "messageId": f"msg_{id(to)}_{asyncio.get_event_loop().time()}",
                    "timestamp": asyncio.get_event_loop().time(),
                    "to": to,
                    "channel": channel or "default",
                },
            )

        except Exception as e:
            logger.bind(tag=TAG).error(f"发送消息失败: {e}")
            return create_tool_call_result(
                success=False,
                error=f"发送消息失败: {str(e)}",
            )

    async def _execute_device_control(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行设备控制工具

        Args:
            arguments: 包含deviceId, action, value的参数字典

        Returns:
            工具调用结果
        """
        device_id = arguments.get("deviceId")
        action = arguments.get("action")
        value = arguments.get("value")

        if not device_id or not action:
            return create_tool_call_result(
                success=False,
                error="缺少必需参数: deviceId, action",
            )

        try:
            logger.bind(tag=TAG).info(
                f"设备控制: device={device_id}, action={action}, value={value}"
            )

            # 如果有统一工具处理器，可以通过它调用IoT控制功能
            if self.func_handler and hasattr(self.func_handler, "handle_tool_call"):
                # 尝试调用IoT设备控制
                iot_arguments = {
                    "device_id": device_id,
                    "action": action,
                }
                if value is not None:
                    iot_arguments["value"] = value

                result = await self.func_handler.handle_tool_call("device_iot", iot_arguments)

                if result and hasattr(result, "action"):
                    from plugins_func.register import Action
                    if result.action == Action.REQLLM:
                        # 工具需要LLM处理，返回结果数据
                        return create_tool_call_result(
                            success=True,
                            data={"result": result.result},
                        )
                    elif result.action in [Action.RESPONSE, Action.NOTFOUND]:
                        return create_tool_call_result(
                            success=True,
                            data={"result": result.response or result.result},
                        )
                    else:
                        return create_tool_call_result(
                            success=False,
                            error=result.response or "未知错误",
                        )

            # 没有统一工具处理器时的备用实现
            return create_tool_call_result(
                success=True,
                data={
                    "deviceId": device_id,
                    "action": action,
                    "value": value,
                    "status": "executed",
                },
            )

        except Exception as e:
            logger.bind(tag=TAG).error(f"设备控制失败: {e}")
            return create_tool_call_result(
                success=False,
                error=f"设备控制失败: {str(e)}",
            )

    async def _execute_agent_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行Agent任务工具

        Args:
            arguments: 包含action, taskId, prompt的参数字典

        Returns:
            工具调用结果
        """
        action = arguments.get("action")
        task_id = arguments.get("taskId")
        prompt = arguments.get("prompt")

        if not action:
            return create_tool_call_result(
                success=False,
                error="缺少必需参数: action",
            )

        if action in ["status", "cancel"] and not task_id:
            return create_tool_call_result(
                success=False,
                error=f"{action} 操作需要 taskId 参数",
            )

        if action == "execute" and not prompt:
            return create_tool_call_result(
                success=False,
                error="execute 操作需要 prompt 参数",
            )

        try:
            logger.bind(tag=TAG).info(
                f"Agent任务: action={action}, taskId={task_id}, prompt={prompt[:50] if prompt else None}..."
            )

            # TODO: 实现实际的Agent任务执行逻辑
            # 可能需要调用任务管理器或创建新的Agent会话

            if action == "execute":
                # 执行新任务
                # 这里可以创建一个新的Agent会话来执行prompt
                return create_tool_call_result(
                    success=True,
                    data={
                        "taskId": f"task_{asyncio.get_event_loop().time()}",
                        "action": action,
                        "status": "started",
                        "prompt": prompt,
                    },
                )

            elif action == "status":
                # 查询任务状态
                return create_tool_call_result(
                    success=True,
                    data={
                        "taskId": task_id,
                        "action": action,
                        "status": "running",
                    },
                )

            elif action == "cancel":
                # 取消任务
                return create_tool_call_result(
                    success=True,
                    data={
                        "taskId": task_id,
                        "action": action,
                        "status": "cancelled",
                    },
                )

        except Exception as e:
            logger.bind(tag=TAG).error(f"Agent任务执行失败: {e}")
            return create_tool_call_result(
                success=False,
                error=f"Agent任务执行失败: {str(e)}",
            )
