"""
工具模块初始化
"""
from app.tools.registry import (
    register_tool,
    get_tool,
    get_all_tools,
    list_tools,
    clear_tools,
)

# 导入示例工具以注册
from app.tools import example_tools

__all__ = [
    "register_tool",
    "get_tool",
    "get_all_tools",
    "list_tools",
    "clear_tools",
    "example_tools",
]
