"""OpenClaw WebSocket服务器

接收来自OpenClaw插件的WebSocket连接，处理工具调用请求。
"""

import asyncio
import json
import websockets
from typing import Optional, Set
from websockets.server import WebSocketServerProtocol
from .config import get_openclaw_config
from .protocol import (
    parse_jsonrpc_request,
    create_success_response,
    create_error_response,
    response_to_json,
    JsonRpcErrorCodes,
)
from .tool_executor import OpenClawToolExecutor
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class OpenClawWebSocketServer:
    """OpenClaw WebSocket服务器"""

    def __init__(self, conn):
        """初始化WebSocket服务器

        Args:
            conn: 连接处理器实例
        """
        self.conn = conn
        self.config = get_openclaw_config()
        self.server: Optional[websockets.WebSocketServer] = None
        self.clients: Set[WebSocketServerProtocol] = set()
        self.is_running = False
        self.executor = OpenClawToolExecutor(conn)

    async def start(self) -> None:
        """启动WebSocket服务器"""
        if self.is_running:
            logger.bind(tag=TAG).warning("OpenClaw WebSocket服务器已在运行")
            return

        if not self.config.enabled:
            logger.bind(tag=TAG).info("OpenClaw适配器未启用")
            return

        host = self.config.host
        port = self.config.port

        logger.bind(tag=TAG).info(f"启动OpenClaw WebSocket服务器: {host}:{port}")

        try:
            self.server = await websockets.serve(
                self._handle_client,
                host,
                port,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10,
            )
            self.is_running = True
            logger.bind(tag=TAG).info(f"OpenClaw WebSocket服务器已启动: ws://{host}:{port}/ws")
        except Exception as e:
            logger.bind(tag=TAG).error(f"启动OpenClaw WebSocket服务器失败: {e}")
            self.is_running = False
            raise

    async def stop(self) -> None:
        """停止WebSocket服务器"""
        if not self.is_running:
            return

        logger.bind(tag=TAG).info("停止OpenClaw WebSocket服务器")

        # 关闭所有客户端连接
        for client in self.clients.copy():
            try:
                await client.close()
            except Exception as e:
                logger.bind(tag=TAG).error(f"关闭客户端连接时出错: {e}")

        self.clients.clear()

        # 关闭服务器
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None

        self.is_running = False
        logger.bind(tag=TAG).info("OpenClaw WebSocket服务器已停止")

    async def _handle_client(self, websocket: WebSocketServerProtocol) -> None:
        """处理客户端连接

        Args:
            websocket: WebSocket连接对象
        """
        client_id = id(websocket)
        remote_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"

        logger.bind(tag=TAG).info(f"新客户端连接: {remote_addr}")

        # 验证认证令牌（如果配置了）
        if not await self._authenticate_client(websocket):
            logger.bind(tag=TAG).warning(f"客户端认证失败: {remote_addr}")
            return

        self.clients.add(websocket)

        try:
            async for message in websocket:
                await self._handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.bind(tag=TAG).info(f"客户端断开连接: {remote_addr}")
        except Exception as e:
            logger.bind(tag=TAG).error(f"处理客户端 {remote_addr} 时出错: {e}")
        finally:
            self.clients.discard(websocket)
            logger.bind(tag=TAG).debug(f"客户端已移除: {remote_addr}")

    async def _authenticate_client(self, websocket: WebSocketServerProtocol) -> bool:
        """验证客户端认证

        Args:
            websocket: WebSocket连接对象

        Returns:
            认证是否成功
        """
        auth_token = self.config.auth_token
        if not auth_token:
            # 未配置认证令牌，允许所有连接
            return True

        # 从请求头中获取认证令牌
        headers = websocket.request_headers
        auth_header = headers.get("Authorization", "")

        if not auth_header:
            return False

        # 验证Bearer token
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            return token == auth_token

        return False

    async def _handle_message(self, websocket: WebSocketServerProtocol, message: str) -> None:
        """处理客户端消息

        Args:
            websocket: WebSocket连接对象
            message: 接收到的消息
        """
        try:
            # 解析JSON-RPC请求
            request = parse_jsonrpc_request(message)
            if request is None:
                await websocket.send(
                    response_to_json(
                        create_error_response(
                            None,
                            JsonRpcErrorCodes.INVALID_REQUEST,
                            "Invalid JSON-RPC 2.0 request",
                        )
                    )
                )
                return

            logger.bind(tag=TAG).debug(f"收到请求: method={request.method}, id={request.id}")

            # 处理不同方法
            if request.method == "tools/call":
                response = await self._handle_tools_call(request)
            elif request.method == "ping":
                response = create_success_response(request.id, {"pong": True})
            else:
                response = create_error_response(
                    request.id,
                    JsonRpcErrorCodes.METHOD_NOT_FOUND,
                    f"Unknown method: {request.method}",
                )

            # 发送响应
            await websocket.send(response_to_json(response))

        except Exception as e:
            logger.bind(tag=TAG).error(f"处理消息时出错: {e}")
            try:
                await websocket.send(
                    response_to_json(
                        create_error_response(
                            None,
                            JsonRpcErrorCodes.INTERNAL_ERROR,
                            str(e),
                        )
                    )
                )
            except Exception:
                pass

    async def _handle_tools_call(self, request) ->:
        """处理tools/call方法

        Args:
            request: JSON-RPC请求对象

        Returns:
            JSON-RPC响应对象
        """
        if not request.params or not isinstance(request.params, dict):
            return create_error_response(
                request.id,
                JsonRpcErrorCodes.INVALID_PARAMS,
                "Missing or invalid params",
            )

        tool_name = request.params.get("name")
        arguments = request.params.get("arguments")

        if not tool_name:
            return create_error_response(
                request.id,
                JsonRpcErrorCodes.INVALID_PARAMS,
                "Missing tool name",
            )

        if not isinstance(arguments, dict):
            return create_error_response(
                request.id,
                JsonRpcErrorCodes.INVALID_PARAMS,
                "Invalid arguments, expected object",
            )

        # 执行工具调用
        result = await self.executor.execute_tool(tool_name, arguments)

        return create_success_response(request.id, result)

    def get_client_count(self) -> int:
        """获取当前连接的客户端数量"""
        return len(self.clients)
