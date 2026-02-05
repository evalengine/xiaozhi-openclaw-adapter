"""Unit tests for OpenClaw adapter protocol module"""

import pytest
import json
from core.providers.tools.openclaw.protocol import (
    JsonRpcRequest,
    JsonRpcSuccessResponse,
    JsonRpcErrorResponse,
    parse_jsonrpc_request,
    create_success_response,
    create_error_response,
    response_to_json,
    create_tool_call_result,
    JsonRpcErrorCodes,
)


class TestJsonRpcRequest:
    """Test JSON-RPC request parsing"""

    def test_parse_valid_request(self):
        """Test parsing a valid JSON-RPC request"""
        data = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "test_tool",
                "arguments": {"foo": "bar"}
            }
        })

        request = parse_jsonrpc_request(data)

        assert request is not None
        assert request.jsonrpc == "2.0"
        assert request.id == 1
        assert request.method == "tools/call"
        assert request.params == {
            "name": "test_tool",
            "arguments": {"foo": "bar"}
        }

    def test_parse_request_without_params(self):
        """Test parsing request without params"""
        data = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "ping"
        })

        request = parse_jsonrpc_request(data)

        assert request is not None
        assert request.method == "ping"
        assert request.params is None

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON"""
        request = parse_jsonrpc_request("not json")

        assert request is None

    def test_parse_missing_jsonrpc_version(self):
        """Test parsing request without jsonrpc version"""
        data = json.dumps({
            "id": 1,
            "method": "test"
        })

        request = parse_jsonrpc_request(data)

        assert request is None

    def test_parse_missing_id(self):
        """Test parsing request without id"""
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "test"
        })

        request = parse_jsonrpc_request(data)

        assert request is None

    def test_parse_missing_method(self):
        """Test parsing request without method"""
        data = json.dumps({
            "jsonrpc": "2.0",
            "id": 1
        })

        request = parse_jsonrpc_request(data)

        assert request is None

    def test_parse_not_dict(self):
        """Test parsing non-dict data"""
        data = json.dumps(["array", "data"])

        request = parse_jsonrpc_request(data)

        assert request is None


class TestCreateSuccessResponse:
    """Test success response creation"""

    def test_create_success_response_with_data(self):
        """Test creating success response with result data"""
        result = {"success": True, "data": {"messageId": "msg_123"}}
        response = create_success_response(1, result)

        assert response.jsonrpc == "2.0"
        assert response.id == 1
        assert response.result == result

    def test_create_success_response_simple(self):
        """Test creating success response with simple result"""
        result = {"status": "ok"}
        response = create_success_response(1, result)

        assert response.result == result


class TestCreateErrorResponse:
    """Test error response creation"""

    def test_create_error_response_with_data(self):
        """Test creating error response with data"""
        response = create_error_response(
            1,
            JsonRpcErrorCodes.INVALID_PARAMS,
            "Invalid parameters",
            {"details": "Missing required field"}
        )

        assert response.jsonrpc == "2.0"
        assert response.id == 1
        assert response.error["code"] == JsonRpcErrorCodes.INVALID_PARAMS
        assert response.error["message"] == "Invalid parameters"
        assert response.error["data"] == {"details": "Missing required field"}

    def test_create_error_response_without_data(self):
        """Test creating error response without data"""
        response = create_error_response(
            2,
            JsonRpcErrorCodes.INTERNAL_ERROR,
            "Internal error"
        )

        assert response.error["code"] == JsonRpcErrorCodes.INTERNAL_ERROR
        assert response.error["message"] == "Internal error"
        assert "data" not in response.error


class TestResponseToJson:
    """Test response serialization"""

    def test_success_response_to_json(self):
        """Test serializing success response to JSON"""
        response = create_success_response(1, {"success": True})
        json_str = response_to_json(response)
        data = json.loads(json_str)

        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert data["result"] == {"success": True}

    def test_error_response_to_json(self):
        """Test serializing error response to JSON"""
        response = create_error_response(
            1,
            JsonRpcErrorCodes.METHOD_NOT_FOUND,
            "Unknown method"
        )
        json_str = response_to_json(response)
        data = json.loads(json_str)

        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert data["error"]["code"] == JsonRpcErrorCodes.METHOD_NOT_FOUND
        assert data["error"]["message"] == "Unknown method"


class TestCreateToolCallResult:
    """Test tool call result creation"""

    def test_success_result_with_data(self):
        """Test creating successful result with data"""
        result = create_tool_call_result(success=True, data={"id": "123"})

        assert result["success"] is True
        assert result["data"] == {"id": "123"}
        assert "error" not in result

    def test_success_result_without_data(self):
        """Test creating successful result without data"""
        result = create_tool_call_result(success=True)

        assert result["success"] is True
        assert "data" not in result

    def test_error_result(self):
        """Test creating error result"""
        result = create_tool_call_result(success=False, error="Execution failed")

        assert result["success"] is False
        assert result["error"] == "Execution failed"
        assert "data" not in result


class TestJsonRpcErrorCodes:
    """Test JSON-RPC error codes"""

    def test_error_codes_values(self):
        """Test error code values match JSON-RPC 2.0 spec"""
        assert JsonRpcErrorCodes.PARSE_ERROR == -32700
        assert JsonRpcErrorCodes.INVALID_REQUEST == -32600
        assert JsonRpcErrorCodes.METHOD_NOT_FOUND == -32601
        assert JsonRpcErrorCodes.INVALID_PARAMS == -32602
        assert JsonRpcErrorCodes.INTERNAL_ERROR == -32603
        assert JsonRpcErrorCodes.SERVER_ERROR_START == -32000
        assert JsonRpcErrorCodes.SERVER_ERROR_END == -32099
