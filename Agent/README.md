# LangGraph Agent

基于 LangGraph 和 FastAPI 的可扩展 Agent 系统，支持前后端分离架构。

## 🚀 项目特点

- **高扩展性**: 模块化设计，轻松添加新工具和功能
- **前后端分离**: FastAPI 后端 + React 前端
- **流式传输**: 支持实时流式输出
- **持久化**: 内置检查点机制，支持对话历史管理
- **工具系统**: 可插拔的工具注册机制
- **SiliconFlow**: 集成硅基流动 API（DeepSeek 模型）

## 📁 项目结构

```
Agent/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── agents/         # Agent 图定义
│   │   ├── api/            # API 路由
│   │   ├── config/         # 配置文件
│   │   ├── core/           # 核心功能（LLM 等）
│   │   ├── memory/         # 记忆管理
│   │   ├── persistence/    # 持久化（检查点）
│   │   ├── schemas/        # Pydantic 数据模式
│   │   └── tools/          # 工具注册和实现
│   ├── main.py             # FastAPI 入口
│   ├── requirements.txt    # Python 依赖
│   └── .env                # 环境变量配置
│
└── frontend/               # 前端应用
    ├── src/
    │   ├── components/     # React 组件
    │   ├── services/       # API 服务层
    │   ├── types/          # TypeScript 类型
    │   ├── hooks/          # 自定义 Hooks
    │   ├── utils/          # 工具函数
    │   └── pages/          # 页面组件
    ├── package.json        # Node.js 依赖
    └── vite.config.ts      # Vite 配置
```

## 🛠️ 快速开始

### 后端启动

1. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **配置环境变量**
```bash
# 编辑 .env 文件，配置 API Key 等
# 已默认配置 SiliconFlow API
```

3. **启动服务**
```bash
python main.py
# 或
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

### 前端启动

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **启动开发服务器**
```bash
npm run dev
```

访问 http://localhost:5173

## 🔧 添加新功能

### 添加新工具

在 `backend/app/tools/` 目录下创建新工具文件：

```python
# backend/app/tools/my_tool.py
from langchain_core.tools import tool
from app.tools.registry import register_tool

@register_tool
@tool
def my_custom_tool(param1: str, param2: int) -> str:
    """
    我的自定义工具描述
    
    Args:
        param1: 参数 1 描述
        param2: 参数 2 描述
        
    Returns:
        返回值描述
    """
    # 实现你的工具逻辑
    return f"结果：{param1}, {param2}"
```

然后在 `backend/app/tools/__init__.py` 中导入：

```python
from app.tools import my_custom_tool  # 自动注册
```

**无需修改其他代码，Agent 会自动识别并使用新工具！**

### 添加新的 LLM 模型

在 `backend/app/config/settings.py` 中修改：

```python
SILICONFLOW_MODEL = "deepseek-ai/DeepSeek-R1"  # 或其他支持的模型
```

### 添加长期记忆

在 `backend/app/memory/` 目录下扩展记忆模块：

```python
# backend/app/memory/long_term_memory.py
from app.tools.registry import register_tool

@register_tool
def save_to_memory(key: str, value: str) -> str:
    """保存信息到长期记忆"""
    # 实现持久化存储逻辑
    return f"已保存：{key}"
```

### 添加新的 API 端点

在 `backend/app/api/` 目录下创建新的路由文件：

```python
# backend/app/api/tools.py
from fastapi import APIRouter

router = APIRouter(prefix="/tools", tags=["工具"])

@router.get("/")
async def list_tools():
    """列出所有可用工具"""
    from app.tools import list_tools
    return {"tools": list_tools()}
```

然后在 `backend/main.py` 中注册路由。

## 📊 核心功能

### 1. Agent 对话系统

- 基于 LangGraph StateGraph 构建
- 支持多轮对话和上下文理解
- 自动工具调用和结果整合
- 流式输出支持

### 2. 工具系统

- 使用装饰器注册工具
- 自动工具发现和加载
- 支持同步和异步工具
- 工具执行错误处理

### 3. 记忆管理

- 短期记忆：对话历史自动维护
- 长期记忆：可扩展的持久化存储
- 使用归约器管理状态更新

### 4. 持久化

- 内存检查点器（开发环境）
- SQLite 检查点器（生产环境）
- 支持对话历史回溯
- 线程隔离的会话管理

## 🔌 可扩展模块

以下模块已预留接口，可根据需求扩展：

### 待实现的工具示例

```python
# 网络搜索工具
@register_tool
@tool
def search_web(query: str) -> str:
    """搜索网络信息"""
    from tavily import TavilyClient
    client = TavilyClient(api_key="your-key")
    result = client.search(query)
    return result

# 数据库查询工具
@register_tool
@tool
def query_database(sql: str) -> list:
    """查询数据库"""
    # 实现数据库查询逻辑
    pass

# 文件处理工具
@register_tool
@tool
def read_file(path: str) -> str:
    """读取文件内容"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
```

### 待实现的功能

1. **人机协同**: 使用 `interrupt()` 实现人工审查
2. **多 Agent 协作**: 创建多个 Agent 进行任务分工
3. **子图系统**: 封装可复用的工作流模块
4. **时间旅行**: 支持对话历史回溯和分叉
5. **断点调试**: 在特定节点设置断点检查状态

## 📝 API 文档

### 聊天接口

**POST** `/api/v1/chat/message`

请求体：
```json
{
  "message": "你好",
  "thread_id": "可选的线程 ID",
  "metadata": {}
}
```

响应：
```json
{
  "message": "你好！有什么可以帮助你的？",
  "thread_id": "xxx-xxx-xxx",
  "checkpoint_id": "检查点 ID",
  "metadata": {"message_count": 2}
}
```

### 流式接口

**POST** `/api/v1/chat/stream`

使用 SSE (Server-Sent Events) 实时传输回复内容。

### 获取线程状态

**GET** `/api/v1/chat/threads/{thread_id}/state`

获取指定线程的对话状态和元数据。

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SILICONFLOW_API_URL` | SiliconFlow API 地址 | `https://api.siliconflow.cn/v1` |
| `SILICONFLOW_API_KEY` | API Key | 已配置 |
| `SILICONFLOW_MODEL` | 使用的模型 | `deepseek-ai/DeepSeek-V3` |
| `PORT` | 后端服务端口 | `8000` |
| `CHECKPOINT_ENABLED` | 启用检查点 | `true` |

### 支持的模型

SiliconFlow 支持以下模型：
- `deepseek-ai/DeepSeek-V3` (默认)
- `deepseek-ai/DeepSeek-R1`

## 🐛 故障排除

### 常见问题

1. **后端启动失败**
   - 检查 Python 版本（建议 3.10+）
   - 确认依赖已安装：`pip install -r requirements.txt`
   - 检查端口是否被占用

2. **前端无法连接后端**
   - 确认后端服务已启动
   - 检查 Vite 代理配置（`vite.config.ts`）
   - 查看浏览器控制台错误信息

3. **工具不生效**
   - 确认工具已使用 `@register_tool` 装饰
   - 检查工具是否在 `__init__.py` 中导入
   - 查看后端日志确认工具注册成功

## 📚 参考资料

- [LangGraph 官方文档](../LangGraph_Info/README.md)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [React 文档](https://react.dev/)
- [SiliconFlow 文档](https://api.siliconflow.cn/v1)

## 🚀 下一步

1. 根据需求添加自定义工具
2. 实现长期记忆功能
3. 添加多 Agent 协作
4. 集成向量数据库
5. 实现人机协同功能

## 📄 许可证

MIT License
