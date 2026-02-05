"""Agent任务工具包装器

提供xiaozhi_agent_task工具的实现。
"""

import asyncio
from typing import Dict, Any, Optional
from plugins_func.register import Action, ActionResponse
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


# 简单的任务存储（生产环境应使用数据库或缓存）
_task_store: Dict[str, Dict[str, Any]] = {}


async def agent_task(
    action: str, task_id: Optional[str] = None, prompt: Optional[str] = None, **kwargs
) -> ActionResponse:
    """执行或查询Agent任务

    Args:
        action: 操作类型（execute, status, cancel）
        task_id: 任务ID（用于status和cancel操作）
        prompt: 任务提示（用于execute操作）
        **kwargs: 其他参数

    Returns:
        ActionResponse对象
    """
    try:
        logger.bind(tag=TAG).info(
            f"Agent任务: action={action}, task_id={task_id}, prompt={prompt[:50] if prompt else None}..."
        )

        if action == "execute":
            return await _execute_task(prompt)
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


async def _execute_task(prompt: str) -> ActionResponse:
    """执行新任务

    Args:
        prompt: 任务提示

    Returns:
        ActionResponse对象
    """
    if not prompt:
        return ActionResponse(
            action=Action.ERROR,
            response="execute 操作需要提供 prompt 参数",
        )

    # 生成任务ID
    task_id = f"task_{asyncio.get_event_loop().time()}"

    # 存储任务信息
    _task_store[task_id] = {
        "id": task_id,
        "prompt": prompt,
        "status": "running",
        "created_at": asyncio.get_event_loop().time(),
    }

    # TODO: 实现实际的Agent任务执行逻辑
    # 这里可以创建新的Agent会话来执行prompt
    # 或者将任务提交给任务队列

    logger.bind(tag=TAG).info(f"创建新任务: {task_id}, prompt: {prompt[:50]}...")

    # 示例：模拟异步执行
    asyncio.create_task(_simulate_task_execution(task_id, prompt))

    return ActionResponse(
        action=Action.REQLLM,
        response=f"任务已创建: {task_id}",
    )


async def _get_task_status(task_id: str) -> ActionResponse:
    """获取任务状态

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

    return ActionResponse(
        action=Action.RESPONSE,
        response=f"任务 {task_id} 状态: {task['status']}",
    )


async def _cancel_task(task_id: str) -> ActionResponse:
    """取消任务

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

    # 更新任务状态
    task["status"] = "cancelled"

    logger.bind(tag=TAG).info(f"任务已取消: {task_id}")

    return ActionResponse(
        action=Action.RESPONSE,
        response=f"任务 {task_id} 已取消",
    )


async def _simulate_task_execution(task_id: str, prompt: str) -> None:
    """模拟任务执行（示例）

    Args:
        task_id: 任务ID
        prompt: 任务提示
    """
    # 模拟任务执行延迟
    await asyncio.sleep(2)

    # 更新任务状态
    if task_id in _task_store:
        _task_store[task_id]["status"] = "completed"
        _task_store[task_id]["result"] = f"已完成: {prompt[:50]}..."
        logger.bind(tag=TAG).info(f"任务已完成: {task_id}")
