# 开发指南

本文档介绍如何扩展和维护 LangGraph Agent 项目。

## 📋 目录

1. [项目架构](#项目架构)
2. [添加新工具](#添加新工具)
3. [添加新功能](#添加新功能)
4. [调试技巧](#调试技巧)
5. [最佳实践](#最佳实践)

## 🏗️ 项目架构

### 后端架构

```
backend/
├── app/
│   ├── agents/          # Agent 核心逻辑
│   │   ├── graph.py     # StateGraph 定义
│   │   └── __init__.py
│   │
│   ├── api/             # API 路由层
│   │   ├── chat.py      # 聊天接口
│   │   └── __init__.py
│   │
│   ├── config/          # 配置管理
│   │   ├── settings.py  # 环境变量配置
│   │   └── __init__.py
│   │
│   ├── core/            # 核心功能
│   │   ├── llm.py       # LLM 初始化和配置
│   │   └── __init__.py
│   │
│   ├── memory/          # 记忆管理
│   │   ├── memory.py    # 短期/长期记忆
│   │   └── __init__.py
│   │
│   ├── persistence/     # 持久化
│   │   ├── checkpoint.py # 检查点管理
│   │   └── __init__.py
│   │
│   ├── schemas/         # 数据模式
│   │   ├── chat.py      # Pydantic 模型
│   │   └── __init__.py
│   │
│   └── tools/           # 工具系统
│       ├── registry.py  # 工具注册表
│       ├── example_tools.py  # 示例工具
│       ├── advanced_tools.py # 高级工具模板
│       └── __init__.py
│
└── main.py             # FastAPI 入口
```

### 前端架构

```
frontend/
├── src/
│   ├── components/     # React 组件
│   │   ├── Chat.tsx    # 聊天组件
│   │   └── Chat.css
│   │
│   ├── services/       # API 服务层
│   │   ├── api.ts      # HTTP 请求封装
│   │   └── ...
│   │
│   ├── types/          # TypeScript 类型
│   │   ├── chat.ts     # 聊天相关类型
│   │   └── ...
│   │
│   ├── hooks/          # 自定义 Hooks
│   │   └── ...
│   │
│   ├── utils/          # 工具函数
│   │   └── ...
│   │
│   ├── pages/          # 页面组件
│   │   └── ...
│   │
│   ├── App.tsx         # 根组件
│   ├── main.tsx        # 入口文件
│   └── index.css       # 全局样式
```

## 🔧 添加新工具

### 方式 1：使用装饰器（推荐）

在 `backend/app/tools/` 目录下创建新文件：

```python
# backend/app/tools/my_tool.py
from langchain_core.tools import tool
from app.tools.registry import register_tool

@register_tool
@tool
def my_function(param1: str, param2: int = 10) -> str:
    """
    工具的描述信息
    
    Args:
        param1: 参数 1 的描述
        param2: 参数 2 的描述，默认值 10
        
    Returns:
        返回值的描述
    """
    # 实现逻辑
    result = f"处理结果：{param1}, {param2}"
    return result
```

然后在 `backend/app/tools/__init__.py` 中导入：

```python
# backend/app/tools/__init__.py
from app.tools import my_tool  # 添加这行

__all__ = [
    "register_tool",
    "get_tool",
    "get_all_tools",
    "list_tools",
    "clear_tools",
    "example_tools",
    "my_tool",  # 添加到 __all__
]
```

**重启后端服务，工具会自动被 Agent 识别和调用！**

### 方式 2：使用类

```python
# backend/app/tools/custom_tool.py
from langchain_core.tools import BaseTool
from app.tools.registry import register_tool
from typing import Type
from pydantic import BaseModel, Field

class CustomToolInput(BaseModel):
    param1: str = Field(..., description="参数 1")
    param2: int = Field(default=10, description="参数 2")

@register_tool
class CustomTool(BaseTool):
    name: str = "custom_tool"
    description: str = "自定义工具的描述"
    args_schema: Type[BaseModel] = CustomToolInput
    
    def _run(self, param1: str, param2: int = 10) -> str:
        # 同步执行逻辑
        return f"结果：{param1}, {param2}"
    
    async def _arun(self, param1: str, param2: int = 10) -> str:
        # 异步执行逻辑（可选）
        return self._run(param1, param2)
```

## 🚀 添加新功能

### 添加新的 API 端点

1. 在 `backend/app/api/` 创建路由文件：

```python
# backend/app/api/tools.py
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ToolInfo
from app.tools import get_all_tools

router = APIRouter(prefix="/tools", tags=["工具管理"])

@router.get("/", response_model=list[ToolInfo])
async def list_tools():
    """列出所有可用工具"""
    tools = get_all_tools()
    return [
        ToolInfo(
            name=tool.name,
            description=tool.description,
            available=True
        )
        for tool in tools
    ]

@router.get("/{tool_name}")
async def get_tool_info(tool_name: str):
    """获取特定工具信息"""
    from app.tools import get_tool
    tool = get_tool(tool_name)
    
    if not tool:
        raise HTTPException(status_code=404, detail="工具不存在")
    
    return ToolInfo(
        name=tool.name,
        description=tool.description,
        available=True
    )
```

2. 在 `backend/main.py` 中注册路由：

```python
# backend/main.py
from fastapi import FastAPI
from app.api import chat_router, tools_router  # 导入新路由

def create_app() -> FastAPI:
    app = FastAPI(...)
    
    # 注册路由
    app.include_router(chat_router.router, prefix="/api/v1")
    app.include_router(tools_router.router, prefix="/api/v1")  # 添加这行
    
    return app
```

### 添加新的 Agent 模式

在 `backend/app/agents/` 目录下创建新的 Agent 实现：

```python
# backend/app/agents/research_agent.py
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.llm import get_llm

class ResearchState(TypedDict):
    query: str
    search_results: list
    summary: str

def create_research_agent():
    """创建研究助手 Agent"""
    llm = get_llm()
    
    def search(state: ResearchState):
        # 实现搜索逻辑
        return {"search_results": ["结果 1", "结果 2"]}
    
    def summarize(state: ResearchState):
        # 实现总结逻辑
        prompt = f"总结以下搜索结果：{state['search_results']}"
        response = llm.invoke([HumanMessage(content=prompt)])
        return {"summary": response.content}
    
    builder = StateGraph(ResearchState)
    builder.add_node("search", search)
    builder.add_node("summarize", summarize)
    
    builder.add_edge(START, "search")
    builder.add_edge("search", "summarize")
    builder.add_edge("summarize", END)
    
    return builder.compile()
```

### 添加前端页面

1. 在 `frontend/src/pages/` 创建新页面：

```tsx
// frontend/src/pages/Tools.tsx
import { useState, useEffect } from 'react';
import api from '../services/api';

interface Tool {
  name: string;
  description: string;
  available: boolean;
}

export default function Tools() {
  const [tools, setTools] = useState<Tool[]>([]);
  
  useEffect(() => {
    // 加载工具列表
    api.get('/tools').then(response => {
      setTools(response.data);
    });
  }, []);
  
  return (
    <div className="tools-page">
      <h1>可用工具</h1>
      <ul>
        {tools.map(tool => (
          <li key={tool.name}>
            <h3>{tool.name}</h3>
            <p>{tool.description}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

2. 在 `frontend/src/App.tsx` 中添加路由（如使用 React Router）。

## 🐛 调试技巧

### 后端调试

1. **启用调试模式**

在 `.env` 文件中设置：
```env
DEBUG=True
```

2. **查看日志**

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def my_function():
    logger.debug("调试信息")
    logger.info("信息")
    logger.warning("警告")
    logger.error("错误")
```

3. **检查工具注册**

```python
# 在 Python 交互环境中
from app.tools import list_tools, get_all_tools

print("已注册的工具:", list_tools())
print("工具详情:", get_all_tools())
```

4. **测试 Agent 图**

```python
from app.agents import get_agent_graph
from langchain_core.messages import HumanMessage

graph = get_agent_graph()
result = graph.invoke({
    "messages": [HumanMessage(content="测试消息")]
})
print(result)
```

### 前端调试

1. **浏览器开发者工具**
   - 查看 Console 日志
   - Network 面板查看 API 请求
   - React Developer Tools 检查组件状态

2. **添加日志**

```tsx
console.log('组件状态:', { messages, isLoading });
```

3. **错误边界**

```tsx
import { Component, ErrorInfo } from 'react';

class ErrorBoundary extends Component {
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('错误:', error, errorInfo);
  }
  
  render() {
    return this.props.children;
  }
}
```

## 📚 最佳实践

### 代码组织

1. **单一职责原则**: 每个模块只负责一个功能
2. **依赖注入**: 使用工厂函数创建实例
3. **类型注解**: 使用 TypeScript/Python 类型提示
4. **文档字符串**: 为所有公共 API 添加文档

### 错误处理

```python
# 后端
from fastapi import HTTPException

@router.post("/message")
async def send_message(request: ChatRequest):
    try:
        # 业务逻辑
        result = await process_message(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("未处理的错误")
        raise HTTPException(status_code=500, detail="服务器内部错误")
```

```tsx
// 前端
try {
  const response = await sendMessage(message);
  // 处理响应
} catch (error) {
  if (error.response?.status === 400) {
    // 处理客户端错误
  } else {
    // 处理服务器错误
  }
}
```

### 性能优化

1. **后端**
   - 使用异步 I/O
   - 实现缓存机制
   - 数据库连接池
   - 流式输出

2. **前端**
   - 组件懒加载
   - 虚拟滚动长列表
   - 防抖和节流
   - 合理使用 useMemo/useCallback

### 安全性

1. **API 安全**
   - 使用环境变量存储密钥
   - 实现速率限制
   - 验证用户输入
   - CORS 配置

2. **工具安全**
   - 沙箱执行不受信任的代码
   - 限制文件访问权限
   - 设置超时时间
   - 捕获并处理异常

## 🔍 常见问题

### Q: 如何添加新的 LLM 提供商？

A: 在 `backend/app/core/llm.py` 中添加新的 LLM 创建函数：

```python
from langchain_anthropic import ChatAnthropic

def create_anthropic_llm(model: str = "claude-3-5-sonnet-latest"):
    return ChatOpenAI(
        model=model,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        base_url="https://api.anthropic.com/v1",
    )
```

### Q: 如何实现多轮对话？

A: 使用 `thread_id` 参数，LangGraph 会自动维护对话历史：

```python
# 第一次请求
response1 = await sendMessage({
    "message": "你好",
    "thread_id": "my-thread-123"
})

# 第二次请求（同一线程）
response2 = await sendMessage({
    "message": "继续刚才的话题",
    "thread_id": "my-thread-123"  # 使用相同的 thread_id
})
```

### Q: 如何禁用工具调用？

A: 在 `backend/app/agents/graph.py` 中修改：

```python
def create_agent_graph():
    llm = get_llm()
    # 不绑定工具
    # tools = get_all_tools()
    # llm_with_tools = llm.bind_tools(tools)
    llm_with_tools = llm  # 直接使用 LLM
    # ...
```

## 📖 参考资源

- [LangGraph 官方文档](../LangGraph_Info/README.md)
- [FastAPI 最佳实践](https://fastapi.tiangolo.com/)
- [React 性能优化](https://react.dev/learn/render-and-commit)
- [TypeScript 深度指南](https://www.typescriptlang.org/docs/)
