"""
LLM 配置和初始化模块
"""
from langchain_openai import ChatOpenAI
from app.config.settings import settings


def create_llm(model: str | None = None, temperature: float = 0.7) -> ChatOpenAI:
    """
    创建 LLM 实例
    
    Args:
        model: 模型名称，默认使用配置中的模型
        temperature: 温度参数，控制随机性
        
    Returns:
        ChatOpenAI 实例
    """
    model_name = model or settings.SILICONFLOW_MODEL
    
    llm = ChatOpenAI(
        model=model_name,
        api_key=settings.SILICONFLOW_API_KEY,
        base_url=settings.SILICONFLOW_API_URL,
        temperature=temperature,
        streaming=True,
    )
    
    return llm


# 全局 LLM 实例（懒加载）
_llm_instance: ChatOpenAI | None = None


def get_llm(model: str | None = None, temperature: float = 0.7) -> ChatOpenAI:
    """
    获取全局 LLM 实例
    
    Args:
        model: 模型名称
        temperature: 温度参数
        
    Returns:
        ChatOpenAI 实例
    """
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = create_llm(model, temperature)
    return _llm_instance
