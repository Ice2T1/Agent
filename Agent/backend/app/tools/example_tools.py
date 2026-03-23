"""
示例工具 - 搜索工具
这是一个工具模板，后续可以添加更多工具
"""
from langchain_core.tools import tool
from app.tools.registry import register_tool
from urllib.parse import urlparse


def extract_domain(url: str) -> str:
    """从 URL 中提取域名"""
    try:
        parsed = urlparse(url)
        return parsed.netloc or url
    except:
        return url


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
    from tavily import TavilyClient
    from app.config.settings import settings

    api_key = settings.TAVILY_API_KEY
    if not api_key:
        return "错误：未配置 TAVILY_API_KEY，请检查 .env 文件"

    tavily = TavilyClient(api_key=api_key)
    response = tavily.search(query=query, search_depth="basic")

    results = []
    for i, result in enumerate(response.get("results", [])):
        domain = extract_domain(result.get('url', ''))
        results.append(
            f"{i+1}. **{result.get('title', '无标题')}**\n"
            f"   {result.get('content', '无内容')}\n"
            f"   来源：{domain}"
        )

    return "\n\n".join(results) if results else "未找到相关搜索结果"


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