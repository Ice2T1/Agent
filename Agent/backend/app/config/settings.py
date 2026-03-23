"""
应用配置模块
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "LangGraph Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API 配置
    API_V1_PREFIX: str = "/api/v1"
    
    # SiliconFlow API 配置
    SILICONFLOW_API_URL: str = "https://api.siliconflow.cn/v1"
    SILICONFLOW_API_KEY: str = "sk-pkjxikgkwjdvpmszfxhmzydlaqwcrgjamuxyotbjxmdrbpmb"
    SILICONFLOW_MODEL: str = "deepseek-ai/DeepSeek-V3"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS 配置
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # 检查点配置
    CHECKPOINT_ENABLED: bool = True
    
    # 搜索工具配置
    TAVILY_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
