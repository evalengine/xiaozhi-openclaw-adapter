"""Agent任务工具包装器

通过小智服务器的HTTP chat API执行Agent任务。
实现方向：OpenClaw → 小智 → LLM Agent
"""

import time
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from plugins_func.register import Action, ActionResponse
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()

# 任务状态存储：task_id → {status, result, created_at, device_id, prompt}
_task_store: Dict[str, Dict[str, Any]] = {}


async def agent_task(
    action: str,
    task_id: Optional[str] = None,
    prompt: Optional[str] = None,
    device_id: Optional[str] = None,
    **kwargs,
) -> ActionResponse:
    """通过小智服务器执行或查询Agent任务

    execute: 通过小智HTTP chat API提交prompt，异步执行并返回taskId。
             可用 status 操作轮询结果。
    status:  查询任务状态和结果。
    cancel:  标记任务为已取消（若任务仍在运行则无法中断）。

    Args:
        action: 操作类型（execute / status / cancel）
        task_id: 任务ID（status 和 cancel 操作必须提供）
        prompt: 任务提示词（execute 操作必须提供）
        device_id: 小智设备MAC地址（execute 时指定哪个小智设备处理任务，
                   留空使用配置中的默认设备）
        **kwargs: 其他参数（忽略）

    Returns:
        ActionResponse对象
    """
    try:
        if action == "execute":
            return await _execute_task(prompt, device_id)
        elif action == "status":
            return await _get_task_status(task_id)
        elif action == "cancel":
            return await _cancel_task(task_id)
        else:
            return ActionResponse(
                action=Action.ERROR,
                response=f"无效的操作类型: {action}，必须是: execute, status, cancel",
            )

    except Exception as e:
        logger.bind(tag=TAG).error(f"Agent任务操作失败: {e}")
        return ActionResponse(
            action=Action.ERROR,
            response=f"Agent任务操作失败: {str(e)}",
        )


async def _execute_task(
    prompt: Optional[str], device_id: Optional[str]
) -> ActionResponse:
    """提交任务到小智，异步执行并返回taskId

    Args:
        prompt: 任务提示词
        device_id: 小智设备ID

    Returns:
        ActionResponse对象
    """
    if not prompt:
        return ActionResponse(
            action=Action.ERROR,
            response="execute 操作需要提供 prompt 参数",
        )

    from ..config import get_openclaw_config
    config = get_openclaw_config()

    target_device = device_id or config._config.get("xiaozhi", {}).get("defaultDeviceId", "")
    if not target_device:
        return ActionResponse(
            action=Action.ERROR,
            response="未指定小智设备ID。请在请求中传入 device_id 参数，"
                     "或在配置文件中设置 xiaozhi.defaultDeviceId",
        )

    task_id = f"task_{int(time.time() * 1000)}"
    _task_store[task_id] = {
        "id": task_id,
        "prompt": prompt,
        "device_id": target_device,
        "status": "running",
        "result": None,
        "created_at": time.time(),
    }

    logger.bind(tag=TAG).info(
        f"创建Agent任务: {task_id}, device={target_device}, prompt={prompt[:80]}..."
    )

    # 异步执行任务，不阻塞当前调用
    asyncio.create_task(_run_task(task_id, target_device, prompt, config.http_port))

    return ActionResponse(
        action=Action.RESPONSE,
        response=f"任务已提交，任务ID: {task_id}。使用 status 操作查询结果。",
    )


async def _run_task(
    task_id: str, device_id: str, prompt: str, http_port: int
) -> None:
    """在后台通过小智HTTP chat API执行任务

    Args:
        task_id: 任务ID
        device_id: 小智设备ID
        prompt: 任务提示词
        http_port: 小智HTTP端口
    """
    url = f"http://127.0.0.1:{http_port}/xiaozhi/chat"
    payload = {"device_id": device_id, "text": prompt}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, json=payload, timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        result = data.get("response", "")
                        _task_store[task_id]["status"] = "completed"
                        _task_store[task_id]["result"] = result
                        logger.bind(tag=TAG).info(
                            f"任务完成: {task_id}, result={result[:80]}..."
                        )
                    else:
                        err = data.get("error", "未知错误")
                        _task_store[task_id]["status"] = "failed"
                        _task_store[task_id]["result"] = err
                        logger.bind(tag=TAG).error(f"任务失败: {task_id}, error={err}")
                else:
                    _task_store[task_id]["status"] = "failed"
                    _task_store[task_id]["result"] = f"HTTP {resp.status}"
    except aiohttp.ClientConnectorError as e:
        _task_store[task_id]["status"] = "failed"
        _task_store[task_id]["result"] = f"无法连接小智服务器: {e}"
        logger.bind(tag=TAG).error(f"任务连接失败: {task_id}, error={e}")
    except asyncio.TimeoutError:
        _task_store[task_id]["status"] = "failed"
        _task_store[task_id]["result"] = "任务超时（120秒）"
        logger.bind(tag=TAG).error(f"任务超时: {task_id}")
    except Exception as e:
        _task_store[task_id]["status"] = "failed"
        _task_store[task_id]["result"] = str(e)
        logger.bind(tag=TAG).error(f"任务异常: {task_id}, error={e}")


async def _get_task_status(task_id: Optional[str]) -> ActionResponse:
    """查询任务状态和结果

    Args:
        task_id: 任务ID

    Returns:
        ActionResponse对象
    """
    if not task_id:
        return ActionResponse(
            action=Action.ERROR,
            response="status 操作需要提供 task_id 参数",
        )

    task = _task_store.get(task_id)
    if not task:
        return ActionResponse(
            action=Action.NOTFOUND,
            response=f"任务不存在: {task_id}",
        )

    status = task["status"]
    result = task.get("result")

    if status == "completed" and result:
        return ActionResponse(
            action=Action.RESPONSE,
            response=f"任务 {task_id} 已完成。结果: {result}",
        )
    elif status == "failed":
        return ActionResponse(
            action=Action.RESPONSE,
            response=f"任务 {task_id} 失败: {result or '未知错误'}",
        )
    elif status == "cancelled":
        return ActionResponse(
            action=Action.RESPONSE,
            response=f"任务 {task_id} 已取消",
        )
    else:
        elapsed = int(time.time() - task["created_at"])
        return ActionResponse(
            action=Action.RESPONSE,
            response=f"任务 {task_id} 正在执行中（已运行 {elapsed} 秒）",
        )


async def _cancel_task(task_id: Optional[str]) -> ActionResponse:
    """标记任务为已取消

    Args:
        task_id: 任务ID

    Returns:
        ActionResponse对象
    """
    if not task_id:
        return ActionResponse(
            action=Action.ERROR,
            response="cancel 操作需要提供 task_id 参数",
        )

    task = _task_store.get(task_id)
    if not task:
        return ActionResponse(
            action=Action.NOTFOUND,
            response=f"任务不存在: {task_id}",
        )

    if task["status"] in ("completed", "failed"):
        return ActionResponse(
            action=Action.RESPONSE,
            response=f"任务 {task_id} 已结束（状态: {task['status']}），无需取消",
        )

    task["status"] = "cancelled"
    logger.bind(tag=TAG).info(f"任务已标记取消: {task_id}")

    return ActionResponse(
        action=Action.RESPONSE,
        response=f"任务 {task_id} 已取消",
    )
