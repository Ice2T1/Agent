"""
持久化模块
管理检查点和状态持久化
"""
from langgraph.checkpoint.memory import MemorySaver
from app.config.settings import settings


def create_checkpointer() -> MemorySaver:
    """
    创建内存检查点器
    
    Returns:
        MemorySaver 实例
    """
    if settings.CHECKPOINT_ENABLED:
        return MemorySaver()
    return None


# 全局检查点器实例
_checkpointer_instance: MemorySaver | None = None


def get_checkpointer() -> MemorySaver | None:
    """
    获取全局检查点器实例
    
    Returns:
        MemorySaver 实例或 None
    """
    global _checkpointer_instance
    if _checkpointer_instance is None and settings.CHECKPOINT_ENABLED:
        _checkpointer_instance = create_checkpointer()
    return _checkpointer_instance
