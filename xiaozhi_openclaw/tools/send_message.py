"""发送消息工具包装器

通过已连接的OpenClaw插件，将消息推送到外部渠道（Telegram、Discord、微信等）。
实现方向：小智 → OpenClaw → 外部渠道
"""

import time
from typing import Optional
from plugins_func.register import Action, ActionResponse
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


async def send_message(
    to: str, text: str, channel: Optional[str] = None, **kwargs
) -> ActionResponse:
    """通过OpenClaw插件发送消息到外部渠道

    小智LLM调用此工具时，适配器将通过已建立的WebSocket连接向所有已连接的
    OpenClaw客户端广播 "message/send" 通知，由OpenClaw插件完成实际的消息投递。

    Args:
        to: 接收者标识符（用户ID、群组ID、手机号等，取决于渠道）
        text: 消息内容
        channel: 渠道名称（telegram / discord / wechat 等），留空则使用OpenClaw默认渠道
        **kwargs: 其他参数（忽略）

    Returns:
        ActionResponse对象
    """
    # 延迟导入避免循环依赖
    from ..websocket_server import get_server_instance

    try:
        server = get_server_instance()

        if server is None:
            logger.bind(tag=TAG).warning("OpenClaw WebSocket服务器未运行，无法发送消息")
            return ActionResponse(
                action=Action.RESPONSE,
                response="OpenClaw适配器未运行，消息发送失败",
            )

        if server.get_client_count() == 0:
            logger.bind(tag=TAG).warning("没有已连接的OpenClaw客户端，无法发送消息")
            return ActionResponse(
                action=Action.RESPONSE,
                response="没有已连接的OpenClaw客户端，请确认OpenClaw插件已启动并连接",
            )

        message_id = f"msg_{int(time.time() * 1000)}"
        params = {
            "messageId": message_id,
            "to": to,
            "text": text,
            "channel": channel or "default",
            "timestamp": int(time.time()),
        }

        logger.bind(tag=TAG).info(
            f"广播消息通知: to={to}, channel={channel or 'default'}, text={text[:80]}..."
        )

        sent_count = await server.broadcast_notification("message/send", params)

        if sent_count > 0:
            return ActionResponse(
                action=Action.RESPONSE,
                response=f"消息已发送给 {to}（渠道: {channel or 'default'}）",
            )
        else:
            return ActionResponse(
                action=Action.RESPONSE,
                response="消息广播失败，OpenClaw客户端未响应",
            )

    except Exception as e:
        logger.bind(tag=TAG).error(f"发送消息失败: {e}")
        return ActionResponse(
            action=Action.ERROR,
            response=f"发送消息失败: {str(e)}",
        )
