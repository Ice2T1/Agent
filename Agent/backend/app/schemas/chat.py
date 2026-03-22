"""
数据模式定义
"""
from pydantic import BaseModel, Field
from typing import Optional, Any


class Message(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="消息角色：user, assistant, system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    thread_id: Optional[str] = Field(None, description="会话线程 ID")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="额外元数据")


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str = Field(..., description="助手回复")
    thread_id: str = Field(..., description="会话线程 ID")
    checkpoint_id: Optional[str] = Field(None, description="检查点 ID")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="额外信息")


class StreamChunk(BaseModel):
    """流式传输块"""
    type: str = Field(..., description="块类型：token, message, error")
    content: Optional[str] = Field(None, description="内容")
    data: Optional[Any] = Field(None, description="额外数据")


class ToolInfo(BaseModel):
    """工具信息"""
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    available: bool = Field(True, description="是否可用")


class AgentState(BaseModel):
    """Agent 状态信息"""
    thread_id: str = Field(..., description="线程 ID")
    message_count: int = Field(0, description="消息数量")
    last_checkpoint: Optional[str] = Field(None, description="最后检查点")
    tools_available: list[str] = Field(default_factory=list, description="可用工具列表")
