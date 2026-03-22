"""
工具模块
所有工具都应该在这里注册，Agent 会自动调用已注册的工具
"""
from typing import Callable
from langchain_core.tools import BaseTool


# 全局工具注册表
_tools_registry: dict[str, BaseTool] = {}


def register_tool(tool: BaseTool) -> BaseTool:
    """
    注册工具到全局注册表
    
    Args:
        tool: 要注册的工具实例
        
    Returns:
        注册的工具实例
    """
    _tools_registry[tool.name] = tool
    return tool


def get_tool(tool_name: str) -> BaseTool | None:
    """
    获取已注册的工具
    
    Args:
        tool_name: 工具名称
        
    Returns:
        工具实例，如果不存在则返回 None
    """
    return _tools_registry.get(tool_name)


def get_all_tools() -> list[BaseTool]:
    """
    获取所有已注册的工具
    
    Returns:
        工具列表
    """
    return list(_tools_registry.values())


def list_tools() -> list[str]:
    """
    列出所有已注册的工具名称
    
    Returns:
        工具名称列表
    """
    return list(_tools_registry.keys())


def clear_tools() -> None:
    """
    清空所有已注册的工具
    """
    _tools_registry.clear()
