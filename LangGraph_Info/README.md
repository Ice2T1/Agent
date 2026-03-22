# LangGraph 开发者指南

本文档是对 LangGraph 官方文档的整理和改写，旨在为开发人员（包括 AI 助手）提供清晰、结构化的参考指南。

## 文档结构

```
LangGraph_Info/
├── 图/                      # LangGraph 核心概念
│   └── 概述.md           # StateGraph、节点、边、Pregel 运行时完整内容
│
├── 函数式 API/               # 函数式编程风格的工作流 API
│   └── 概述.md           # entrypoint、task、记忆、流式传输
│
├── 代理架构/                # 代理系统设计
│   └── 概述.md              # 代理类型、常见架构模式
│
├── 多代理/                  # 多代理系统
│   └── 概述.md              # 多代理架构、交接、通信
│
├── 子图/                    # 子图与封装
│   └── 概述.md              # 子图创建、使用、状态管理
│
├── 工具/                    # 工具系统
│   └── 概述.md              # 工具创建、执行、预构建工具
│
├── 持久化/                  # 状态持久化
│   └── 概述.md              # 检查点、线程、存储
│
├── 内存/                    # 记忆管理
│   └── 概述.md              # 短期记忆、长期记忆
│
├── 断点/                    # 调试功能
│   └── 概述.md              # 断点设置、状态检查
│
├── 时间旅行/                # 执行历史回溯
│   └── 概述.md              # 检查点恢复、分叉
│
├── 流式传输/                # 实时输出
│   └── 概述.md              # 流式模式、LLM 令牌流
│
└── 人机协同/                # 人工参与
    └── 概述.md              # interrupt、人工审查
```

## 快速导航

### 📐 核心概念

- **[图完整指南](./图/完整指南.md)** - LangGraph 基础与运行时
  - State（状态）、Nodes（节点）、Edges（边）
  - StateGraph API、归约器、消息处理
  - Command 原语、Send API、节点缓存
  - Pregel 运行时、执行模型、通道

- **[函数式 API 完整指南](./函数式 API/完整指南.md)** - 函数式编程风格
  - @entrypoint、@task 装饰器
  - 短期记忆、长期记忆
  - 人在环、流式传输
  - 并行执行、重试策略、缓存

### 🤖 代理系统

- **[代理架构](./代理架构/概述.md)** - 单代理系统设计
  - 路由器、工具调用代理
  - 常见模式：提示链、并行化、路由、编排器 - 工作器、评估器 - 优化器
  - 记忆、工具调用

- **[多代理系统](./多代理/概述.md)** - 多代理协作
  - 架构模式：网络、主管、分层、自定义工作流
  - 交接（Handoffs）机制
  - 代理间通信、状态管理
  - 多轮对话支持

- **[子图](./子图/概述.md)** - 封装与重用
  - 子图创建和使用
  - 状态模式转换
  - 嵌套子图
  - 可重用组件设计

### 🛠️ 工具系统

- **[工具](./工具/概述.md)** - 外部系统集成
  - 工具创建（装饰器、手动）
  - 工具执行（手动、ToolNode、create_react_agent）
  - 预构建工具集成
  - 工具最佳实践

### 💾 状态管理

- **[持久化](./持久化/概述.md)** - 检查点与存储
  - 检查点器（内存、SQLite、Postgres）
  - 线程管理
  - 状态回放与更新
  - Store 接口、语义搜索
  - 序列化与加密

- **[内存](./内存/概述.md)** - 记忆管理
  - 短期记忆（线程内）
  - 长期记忆（跨线程）
  - 记忆类型：语义、情景、程序
  - 对话历史管理（修剪、总结）

### 🔍 调试与监控

- **[断点](./断点/概述.md)** - 执行暂停
  - 设置断点
  - 状态检查
  - 人工审查工作流

- **[时间旅行](./时间旅行/概述.md)** - 历史回溯
  - 检查点恢复
  - 执行分叉
  - 调试应用场景

### ⚡ 实时功能

- **[流式传输](./流式传输/概述.md)** - 实时输出
  - 流式模式：updates、values、messages、custom、debug
  - LLM 令牌流
  - 进度通知
  - 子图流式传输

### 👥 人机交互

- **[人机协同](./人机协同/概述.md)** - 人工参与
  - interrupt() 函数
  - Command 原语
  - 审批工作流
  - 多轮对话

## 核心 API 速查

### StateGraph 基础

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from operator import add

# 定义状态
class State(TypedDict):
    messages: list
    data: Annotated[list, add]  # 使用归约器

# 创建图
builder = StateGraph(State)

# 添加节点
builder.add_node("node_a", node_function)
builder.add_node("node_b", another_function)

# 添加边
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

# 条件边
builder.add_conditional_edges(
    "node_a",
    routing_function,
    {"path_a": "node_b", "path_b": "node_c"}
)

# 编译（可选：添加检查点器）
graph = builder.compile(checkpointer=checkpointer)
```

### Command 原语

```python
from langgraph.types import Command

def node(state: State) -> Command[Literal["next_node"]]:
    return Command(
        update={"key": "value"},      # 状态更新
        goto="next_node",              # 路由到下一个节点
        graph=Command.PARENT           # 可选：导航到父图
    )
```

### Send API（动态边）

```python
from langgraph.constants import Send

def dynamic_routing(state: State):
    # 为每个项目创建 worker
    return [Send("worker", {"item": item}) for item in state["items"]]
```

### interrupt() 人工参与

```python
from langgraph.types import interrupt

def human_node(state: State):
    # 暂停并等待输入
    user_input = interrupt(value="Ready for user input")
    return {"user_input": user_input}

# 恢复执行
graph.invoke(Command(resume="user response"), config)
```

### 工具创建与使用

```python
from langchain_core.tools import tool

@tool
def my_tool(param1: str, param2: int = 10) -> str:
    """Tool description."""
    return f"Result: {param1}, {param2}"

# 绑定到 LLM
llm_with_tools = llm.bind_tools([my_tool])

# 或使用预构建代理
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(llm, [my_tool])
```

### 检查点器

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

# 内存检查点器（实验）
checkpointer = InMemorySaver()

# SQLite 检查点器（本地开发）
checkpointer = SqliteSaver(sqlite3.connect("checkpoints.db"))

# 编译时使用
graph = builder.compile(checkpointer=checkpointer)

# 配置线程
config = {"configurable": {"thread_id": "1"}}

# 调用
result = graph.invoke(input_data, config)
```

### 存储（长期记忆）

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# 保存
namespace = ("user_id", "memories")
store.put(namespace, "memory_1", {"fact": "User likes Python"})

# 检索
item = store.get(namespace, "memory_1")

# 搜索（支持语义搜索）
items = store.search(namespace, query="programming preferences")

# 在节点中使用
def node(state: State, store: BaseStore):
    memories = store.search(("user_memories",))
    return {"context": memories}

# 编译时使用
graph = builder.compile(store=store)
```

## 常见架构模式

### 1. 提示链（线性工作流）

```python
builder = StateGraph(State)
builder.add_node("step1", function1)
builder.add_node("step2", function2)
builder.add_node("step3", function3)
builder.add_edge(START, "step1")
builder.add_edge("step1", "step2")
builder.add_edge("step2", "step3")
builder.add_edge("step3", END)
```

### 2. 并行化

```python
builder = StateGraph(State)
builder.add_node("task_a", function_a)
builder.add_node("task_b", function_b)
builder.add_node("task_c", function_c)
builder.add_node("aggregate", aggregator)
builder.add_edge(START, "task_a")
builder.add_edge(START, "task_b")
builder.add_edge(START, "task_c")
builder.add_edge("task_a", "aggregate")
builder.add_edge("task_b", "aggregate")
builder.add_edge("task_c", "aggregate")
builder.add_edge("aggregate", END)
```

### 3. 路由

```python
def router(state):
    if condition_a:
        return "path_a"
    else:
        return "path_b"

builder.add_conditional_edges(
    "decision_node",
    router,
    {"path_a": "node_a", "path_b": "node_b"}
)
```

### 4. 循环（ReAct 代理）

```python
def should_continue(state):
    if has_tool_calls(state):
        return "tools"
    return END

builder.add_node("llm", call_llm)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", should_continue)
builder.add_edge("tools", "llm")
```

### 5. 多代理交接

```python
@tool
def transfer_to_agent_b(state: Annotated[MessagesState, InjectedState]) -> Command:
    """Transfer to agent B."""
    return Command(
        goto="agent_b",
        update={"messages": state["messages"]},
        graph=Command.PARENT
    )

# 在父图中
parent_builder = StateGraph(MessagesState)
parent_builder.add_node("agent_a", agent_a_graph)
parent_builder.add_node("agent_b", agent_b_graph)
parent_builder.add_edge(START, "agent_a")
```

## 最佳实践

### 1. 状态设计

- 使用 TypedDict 或 Pydantic 定义清晰的状态模式
- 为需要累加的键使用 `Annotated` 和归约器
- 区分输入状态和输出状态（可选）

### 2. 节点设计

- 保持节点功能单一、职责明确
- 使用清晰的命名
- 返回字典形式的状态更新
- 考虑添加错误处理

### 3. 边设计

- 简单路由使用条件边
- 复杂控制流使用 Command
- 动态创建边使用 Send API

### 4. 持久化

- 开发使用 InMemorySaver
- 本地测试使用 SqliteSaver
- 生产使用 PostgresSaver
- 始终为线程设置唯一 ID

### 5. 错误处理

```python
def robust_node(state: State):
    try:
        result = operation(state)
        return {"data": result, "error": None}
    except Exception as e:
        return {"error": str(e), "retry_count": state.get("retry_count", 0) + 1}
```

### 6. 测试

```python
def test_node():
    # 单元测试节点
    test_input = {"key": "value"}
    result = node_function(test_input)
    assert "expected_key" in result

def test_graph():
    # 集成测试图
    config = {"configurable": {"thread_id": "test"}}
    result = graph.invoke(test_input, config)
    assert result["expected_output"] is not None
```

## 调试技巧

### 1. 查看状态历史

```python
history = list(graph.get_state_history(config))
for snapshot in history:
    print(f"Step {snapshot.metadata['step']}: {snapshot.values}")
```

### 2. 从检查点恢复

```python
# 获取历史
history = list(graph.get_state_history(config))

# 选择检查点
checkpoint_id = history[2].config["configurable"]["checkpoint_id"]
config["configurable"]["checkpoint_id"] = checkpoint_id

# 恢复（创建新分支）
result = graph.invoke(None, config)
```

### 3. 流式调试

```python
for chunk in graph.stream(input, stream_mode="debug"):
    print(f"Event: {chunk.get('event')}")
    print(f"Data: {chunk.get('data')}")
```

### 4. 可视化图

```python
# 获取图的图形表示
graph_png = graph.get_graph().draw_mermaid_png()

# 或在 Jupyter 中显示
from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))
```

## 性能优化

### 1. 节点缓存

```python
from langgraph.types import CachePolicy
from langgraph.cache.memory import InMemoryCache

builder.add_node(
    "expensive_node",
    expensive_function,
    cache_policy=CachePolicy(ttl=3600)  # 缓存 1 小时
)

graph = builder.compile(cache=InMemoryCache())
```

### 2. 并行执行

```python
# 多个节点从同一点开始会并行执行
builder.add_edge(START, "node_a")
builder.add_edge(START, "node_b")
builder.add_edge(START, "node_c")
```

### 3. 限制上下文

```python
# 使用 trim_messages 限制消息历史
from langchain_core.messages import trim_messages

trimmed = trim_messages(
    messages,
    strategy="last",
    max_tokens=1000,
    token_counter=llm
)
```

## 资源链接

- **LangChain 学院**: https://academy.langchain.com/
- **LangSmith**: https://smith.langchain.com/
- **LangChain 集成目录**: https://python.langchain.com/docs/integrations/

## 版本信息

本文档基于 LangGraph 最新版本整理。API 可能随版本变化，请以官方文档为准。

---

**最后更新**: 2026-03-22
