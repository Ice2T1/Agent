"""
示例工具 - 搜索工具
这是一个工具模板，后续可以添加更多工具
"""
from langchain_core.tools import tool
from app.tools.registry import register_tool


@register_tool
@tool
def search_web(query: str) -> str:
    """
    搜索网络信息
    
    Args:
        query: 搜索查询
        
    Returns:
        搜索结果
    """
    # TODO: 实现实际的搜索逻辑
    # 可以使用 Tavily、Serper 或其他搜索 API
    return f"搜索 '{query}' 的结果（待实现）"


@register_tool
@tool
def calculator(expression: str) -> float:
    """
    计算数学表达式
    
    Args:
        expression: 数学表达式，如 "2 + 2"
        
    Returns:
        计算结果
    """
    try:
        # 注意：在生产环境中应该使用更安全的计算方法
        return eval(expression)
    except Exception as e:
        return f"计算错误：{str(e)}"


@register_tool
@tool
def get_current_time() -> str:
    """
    获取当前时间
    
    Returns:
        当前时间字符串
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
