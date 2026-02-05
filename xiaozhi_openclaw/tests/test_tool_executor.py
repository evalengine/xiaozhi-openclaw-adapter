"""Unit tests for OpenClaw adapter tool executor module"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from core.providers.tools.openclaw.tool_executor import OpenClawToolExecutor


class TestOpenClawToolExecutor:
    """Test OpenClawToolExecutor class"""

    def test_init(self):
        """Test executor initialization"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        assert executor.conn == mock_conn
        assert executor.func_handler is None

    def test_init_with_func_handler(self):
        """Test executor with func_handler in conn"""
        mock_conn = Mock()
        mock_func_handler = Mock()
        mock_conn.func_handler = mock_func_handler

        executor = OpenClawToolExecutor(mock_conn)

        assert executor.func_handler == mock_func_handler

    @pytest.mark.asyncio
    async def test_execute_send_message_success(self):
        """Test executing send_message tool successfully"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_send_message", {
            "to": "user123",
            "text": "Hello, world!",
            "channel": "telegram"
        })

        assert result["success"] is True
        assert "data" in result
        assert result["data"]["to"] == "user123"
        assert result["data"]["channel"] == "telegram"

    @pytest.mark.asyncio
    async def test_execute_send_message_missing_to(self):
        """Test send_message with missing 'to' parameter"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_send_message", {
            "text": "Hello!"
        })

        assert result["success"] is False
        assert "error" in result
        assert "to" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_send_message_missing_text(self):
        """Test send_message with missing 'text' parameter"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_send_message", {
            "to": "user123"
        })

        assert result["success"] is False
        assert "error" in result
        assert "text" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_device_control_success(self):
        """Test executing device_control tool successfully"""
        mock_conn = Mock()
        mock_conn.func_handler = None
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_device_control", {
            "deviceId": "light_01",
            "action": "turn_on"
        })

        assert result["success"] is True
        assert result["data"]["deviceId"] == "light_01"
        assert result["data"]["action"] == "turn_on"

    @pytest.mark.asyncio
    async def test_execute_device_control_with_value(self):
        """Test device_control with value parameter"""
        mock_conn = Mock()
        mock_conn.func_handler = None
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_device_control", {
            "deviceId": "dimmer_01",
            "action": "set_value",
            "value": 50
        })

        assert result["success"] is True
        assert result["data"]["value"] == 50

    @pytest.mark.asyncio
    async def test_execute_device_control_missing_device_id(self):
        """Test device_control with missing deviceId"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_device_control", {
            "action": "turn_on"
        })

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_execute_device_control_missing_action(self):
        """Test device_control with missing action"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_device_control", {
            "deviceId": "light_01"
        })

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_execute_device_control_invalid_action(self):
        """Test device_control with invalid action"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_device_control", {
            "deviceId": "light_01",
            "action": "invalid_action"
        })

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_execute_device_control_set_value_requires_value(self):
        """Test device_control set_value requires value parameter"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_device_control", {
            "deviceId": "dimmer_01",
            "action": "set_value"
        })

        assert result["success"] is False
        assert "error" in result
        assert "value" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_device_control_value_range(self):
        """Test device_control value must be 0-100"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        # Test value > 100
        result = await executor.execute_tool("xiaozhi_device_control", {
            "deviceId": "dimmer_01",
            "action": "set_value",
            "value": 150
        })
        assert result["success"] is False

        # Test value < 0
        result = await executor.execute_tool("xiaozhi_device_control", {
            "deviceId": "dimmer_01",
            "action": "set_value",
            "value": -10
        })
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_execute_agent_task_execute(self):
        """Test executing agent_task with execute action"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_agent_task", {
            "action": "execute",
            "prompt": "Summarize the conversation"
        })

        assert result["success"] is True
        assert "taskId" in result["data"]
        assert result["data"]["action"] == "execute"
        assert result["data"]["status"] == "started"

    @pytest.mark.asyncio
    async def test_execute_agent_task_status(self):
        """Test executing agent_task with status action"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_agent_task", {
            "action": "status",
            "taskId": "task_123"
        })

        assert result["success"] is True
        assert result["data"]["action"] == "status"

    @pytest.mark.asyncio
    async def test_execute_agent_task_cancel(self):
        """Test executing agent_task with cancel action"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_agent_task", {
            "action": "cancel",
            "taskId": "task_123"
        })

        assert result["success"] is True
        assert result["data"]["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_execute_agent_task_missing_action(self):
        """Test agent_task with missing action"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_agent_task", {})

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_execute_agent_task_status_requires_task_id(self):
        """Test agent_task status requires taskId"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_agent_task", {
            "action": "status"
        })

        assert result["success"] is False
        assert "taskId" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_agent_task_cancel_requires_task_id(self):
        """Test agent_task cancel requires taskId"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_agent_task", {
            "action": "cancel"
        })

        assert result["success"] is False
        assert "taskId" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_agent_task_execute_requires_prompt(self):
        """Test agent_task execute requires prompt"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("xiaozhi_agent_task", {
            "action": "execute"
        })

        assert result["success"] is False
        assert "prompt" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self):
        """Test executing unknown tool"""
        mock_conn = Mock()
        executor = OpenClawToolExecutor(mock_conn)

        result = await executor.execute_tool("unknown_tool", {})

        assert result["success"] is False
        assert "error" in result
        assert "unknown" in result["error"].lower()
