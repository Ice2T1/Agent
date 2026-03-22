"""
记忆模块
管理短期记忆和长期记忆
"""
from typing import Annotated, TypedDict
from operator import add


class MemoryState(TypedDict):
    """
    记忆状态
    
    使用 Annotated 和归约器来管理消息历史
    """
    # 消息列表，使用 add 归约器来追加消息
    messages: Annotated[list, add]
    
    # 元数据
    metadata: dict
    
    # 长期记忆（可选）
    long_term_memories: list[dict]


def create_memory_state() -> MemoryState:
    """
    创建初始记忆状态
    
    Returns:
        空的记忆状态
    """
    return MemoryState(
        messages=[],
        metadata={},
        long_term_memories=[],
    )


def add_message(state: MemoryState, role: str, content: str) -> MemoryState:
    """
    添加消息到记忆
    
    Args:
        state: 当前记忆状态
        role: 消息角色（user/assistant/system）
        content: 消息内容
        
    Returns:
        更新后的记忆状态
    """
    new_message = {"role": role, "content": content}
    return MemoryState(
        messages=state["messages"] + [new_message],
        metadata=state.get("metadata", {}),
        long_term_memories=state.get("long_term_memories", []),
    )


def get_message_history(state: MemoryState, limit: int = 10) -> list[dict]:
    """
    获取消息历史
    
    Args:
        state: 记忆状态
        limit: 返回的消息数量限制
        
    Returns:
        消息历史列表
    """
    messages = state.get("messages", [])
    return messages[-limit:] if limit else messages
