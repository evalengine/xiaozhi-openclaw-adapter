"""JSON-RPC 2.0 协议处理

处理与OpenClaw插件之间的JSON-RPC 2.0通信协议。
"""

import json
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


# JSON-RPC 2.0 错误码
class JsonRpcErrorCodes:
    """JSON-RPC 2.0 错误码定义"""

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_START = -32000
    SERVER_ERROR_END = -32099


@dataclass
class JsonRpcRequest:
    """JSON-RPC 2.0 请求"""

    jsonrpc: str
    id: Union[int, str]
    method: str
    params: Optional[Dict[str, Any]] = None


@dataclass
class JsonRpcResponse:
    """JSON-RPC 2.0 响应基类"""

    jsonrpc: str
    id: Union[int, str]


@dataclass
class JsonRpcSuccessResponse(JsonRpcResponse):
    """JSON-RPC 2.0 成功响应"""

    result: Any


@dataclass
class JsonRpcErrorResponse(JsonRpcResponse):
    """JSON-RPC 2.0 错误响应"""

    error: Dict[str, Any]


def parse_jsonrpc_request(data: str) -> Optional[JsonRpcRequest]:
    """解析JSON-RPC 2.0请求

    Args:
        data: JSON字符串

    Returns:
        JsonRpcRequest对象，解析失败返回None
    """
    try:
        parsed = json.loads(data)
        if not isinstance(parsed, dict):
            return None

        if parsed.get("jsonrpc") != "2.0":
            return None

        if "id" not in parsed or "method" not in parsed:
            return None

        return JsonRpcRequest(
            jsonrpc="2.0",
            id=parsed["id"],
            method=parsed["method"],
            params=parsed.get("params"),
        )
    except json.JSONDecodeError as e:
        logger.bind(tag=TAG).error(f"解析JSON-RPC请求失败: {e}")
        return None
    except Exception as e:
        logger.bind(tag=TAG).error(f"解析JSON-RPC请求时发生错误: {e}")
        return None


def create_success_response(
    request_id: Union[int, str], result: Any
) -> JsonRpcSuccessResponse:
    """创建成功响应

    Args:
        request_id: 请求ID
        result: 结果数据

    Returns:
        JsonRpcSuccessResponse对象
    """
    return JsonRpcSuccessResponse(jsonrpc="2.0", id=request_id, result=result)


def create_error_response(
    request_id: Union[int, str],
    code: int,
    message: str,
    data: Optional[Any] = None,
) -> JsonRpcErrorResponse:
    """创建错误响应

    Args:
        request_id: 请求ID
        code: 错误码
        message: 错误消息
        data: 附加数据

    Returns:
        JsonRpcErrorResponse对象
    """
    error = {"code": code, "message": message}
    if data is not None:
        error["data"] = data

    return JsonRpcErrorResponse(jsonrpc="2.0", id=request_id, error=error)


def response_to_json(response: Union[JsonRpcSuccessResponse, JsonRpcErrorResponse]) -> str:
    """将响应对象转换为JSON字符串

    Args:
        response: 响应对象

    Returns:
        JSON字符串
    """
    if isinstance(response, JsonRpcSuccessResponse):
        data = {
            "jsonrpc": response.jsonrpc,
            "id": response.id,
            "result": response.result,
        }
    else:
        data = {
            "jsonrpc": response.jsonrpc,
            "id": response.id,
            "error": response.error,
        }

    return json.dumps(data, ensure_ascii=False)


def create_tool_call_result(success: bool, data: Any = None, error: str = None) -> Dict[str, Any]:
    """创建工具调用结果

    Args:
        success: 是否成功
        data: 结果数据
        error: 错误信息

    Returns:
        工具调用结果字典
    """
    result = {"success": success}
    if data is not None:
        result["data"] = data
    if error is not None:
        result["error"] = error
    return result
