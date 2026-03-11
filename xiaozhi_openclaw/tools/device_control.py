"""设备控制工具包装器

通过小智服务器控制IoT设备。
实现方向：OpenClaw → 小智 → IoT设备
"""

import aiohttp
from typing import Optional
from plugins_func.register import Action, ActionResponse
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()

# 操作到自然语言指令的映射
_ACTION_COMMANDS = {
    "turn_on": "打开",
    "turn_off": "关闭",
    "toggle": "切换",
    "set_value": "设置为",
}

VALID_ACTIONS = list(_ACTION_COMMANDS.keys())


async def device_control(
    deviceId: str,
    action: str,
    value: Optional[int] = None,
    xiaozhi_device_id: Optional[str] = None,
    **kwargs,
) -> ActionResponse:
    """通过小智服务器控制IoT设备

    将设备控制指令转换为自然语言，通过小智的HTTP chat API发送给指定设备，
    由小智的IoT工具系统执行实际的设备控制操作。

    Args:
        deviceId: IoT设备标识符（如 "light_bedroom"、"switch_01"）
        action: 操作类型（turn_on / turn_off / toggle / set_value）
        value: 设置值（0-100，仅 set_value 操作时有效）
        xiaozhi_device_id: 小智设备的MAC地址（用于指定哪个小智设备执行指令，
                           留空则使用配置文件中的默认设备）
        **kwargs: 其他参数（忽略）

    Returns:
        ActionResponse对象
    """
    from ..config import get_openclaw_config

    # 参数校验
    if action not in VALID_ACTIONS:
        return ActionResponse(
            action=Action.ERROR,
            response=f"无效的操作类型: {action}，必须是: {', '.join(VALID_ACTIONS)}",
        )

    if action == "set_value" and value is None:
        return ActionResponse(
            action=Action.ERROR,
            response="set_value 操作需要提供 value 参数",
        )

    if value is not None and not (0 <= value <= 100):
        return ActionResponse(
            action=Action.ERROR,
            response="value 必须在 0-100 之间",
        )

    # 构建自然语言指令
    cmd_word = _ACTION_COMMANDS[action]
    if action == "set_value":
        command = f"{cmd_word} {deviceId} {value}%"
    else:
        command = f"{cmd_word} {deviceId}"

    config = get_openclaw_config()
    http_port = config.http_port

    # 确定目标设备ID
    target_device = xiaozhi_device_id or config._config.get("xiaozhi", {}).get("defaultDeviceId", "")

    if not target_device:
        logger.bind(tag=TAG).warning(
            "未指定小智设备ID，尝试广播IoT控制通知到OpenClaw客户端"
        )
        # 回退：通过广播通知OpenClaw客户端执行设备控制
        from ..websocket_server import get_server_instance
        server = get_server_instance()
        if server and server.get_client_count() > 0:
            await server.broadcast_notification("device/control", {
                "deviceId": deviceId,
                "action": action,
                "value": value,
            })
            status = _get_status_text(action, value)
            return ActionResponse(
                action=Action.RESPONSE,
                response=f"设备 {deviceId} {status}（已通知OpenClaw执行）",
            )
        return ActionResponse(
            action=Action.ERROR,
            response="未配置小智设备ID，且无已连接的OpenClaw客户端。"
                     "请在配置文件中设置 xiaozhi.defaultDeviceId 或在请求中传入 xiaozhi_device_id",
        )

    # 通过小智HTTP chat API发送指令
    url = f"http://127.0.0.1:{http_port}/xiaozhi/chat"
    payload = {"device_id": target_device, "text": command}

    logger.bind(tag=TAG).info(
        f"设备控制: device={deviceId}, action={action}, value={value}, "
        f"command='{command}', target_xiaozhi={target_device}"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        status = _get_status_text(action, value)
                        return ActionResponse(
                            action=Action.RESPONSE,
                            response=f"设备 {deviceId} {status}",
                        )
                    else:
                        err = data.get("error", "未知错误")
                        return ActionResponse(
                            action=Action.ERROR,
                            response=f"设备控制失败: {err}",
                        )
                else:
                    return ActionResponse(
                        action=Action.ERROR,
                        response=f"小智HTTP API返回错误状态: {resp.status}",
                    )
    except aiohttp.ClientConnectorError:
        return ActionResponse(
            action=Action.ERROR,
            response=f"无法连接到小智HTTP服务器 (127.0.0.1:{http_port})，请确认服务器正在运行",
        )
    except Exception as e:
        logger.bind(tag=TAG).error(f"设备控制失败: {e}")
        return ActionResponse(
            action=Action.ERROR,
            response=f"设备控制失败: {str(e)}",
        )


def _get_status_text(action: str, value: Optional[int]) -> str:
    """获取操作结果描述文本"""
    if action == "turn_on":
        return "已打开"
    elif action == "turn_off":
        return "已关闭"
    elif action == "toggle":
        return "已切换"
    elif action == "set_value":
        return f"已设置为 {value}%"
    return "操作已执行"
