"""
Agent 图定义
使用 LangGraph 构建可对话的 Agent
"""
from typing import Literal, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.llm import get_llm
from app.tools import get_all_tools


class AgentState(TypedDict):
    """
    Agent 状态

    定义 Agent 运行时的状态结构
    """
    # 消息历史，使用 add_messages 归约器
    messages: Annotated[list, add_messages]


def create_agent_graph() -> StateGraph:
    """
    创建 Agent 图

    Returns:
        编译好的 StateGraph
    """
    # 获取 LLM 和工具
    llm = get_llm()
    tools = get_all_tools()
    print(f"create_agent_graph: 加载了 {len(tools)} 个工具")

    # 如果有工具，绑定到 LLM
    if tools:
        llm_with_tools = llm.bind_tools(tools)
        print(f"create_agent_graph: LLM 已绑定 {len(tools)} 个工具")
    else:
        llm_with_tools = llm
        print(f"create_agent_graph: 没有可用工具")

    # 定义节点
    def call_model(state: AgentState):
        """调用 LLM 模型"""
        messages = state.get("messages", [])
        print(f"call_model: 收到 {len(messages)} 条消息")

        for i, msg in enumerate(messages):
            msg_type = type(msg).__name__
            content = msg.content if hasattr(msg, 'content') else str(msg)
            print(f"call_model: 消息[{i}] 类型: {msg_type}, 内容: {str(content)[:80]}")

        # 添加系统提示
        system_message = SystemMessage(
            content="你是一个有帮助的 AI 助手。当用户询问需要实时信息时，请使用 search_web 工具进行搜索。搜索结果请以友好的方式呈现。"
        )

        # 处理消息：清除 AIMessage 中已执行的 tool_calls
        from langchain_core.messages import AIMessage
        processed_messages = []
        for msg in messages:
            if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                # 清除 tool_calls 因为这些工具调用已经被执行过了
                print(f"call_model: 清除 AIMessage 中的 tool_calls (数量: {len(msg.tool_calls)})")
                msg = AIMessage(content=msg.content)
            processed_messages.append(msg)

        # 准备发送给 LLM 的消息
        llm_messages = [system_message] + processed_messages
        print(f"call_model: 准备调用 LLM，输入消息数: {len(llm_messages)}")
        
        # 详细打印每条消息
        for i, msg in enumerate(llm_messages):
            msg_type = type(msg).__name__
            print(f"call_model: LLM消息[{i}] 类型: {msg_type}")
            if hasattr(msg, 'content'):
                print(f"call_model: LLM消息[{i}] content长度: {len(str(msg.content))}")
                print(f"call_model: LLM消息[{i}] content前100字符: {str(msg.content)[:100]}")
            if hasattr(msg, 'type'):
                print(f"call_model: LLM消息[{i}] type属性: {msg.type}")
            if hasattr(msg, 'role'):
                print(f"call_model: LLM消息[{i}] role属性: {msg.role}")
            if hasattr(msg, 'tool_calls'):
                print(f"call_model: LLM消息[{i}] tool_calls: {msg.tool_calls}")
            if hasattr(msg, 'tool_call_id'):
                print(f"call_model: LLM消息[{i}] tool_call_id: {msg.tool_call_id}")
            if hasattr(msg, 'name'):
                print(f"call_model: LLM消息[{i}] name: {msg.name}")

        # 调用模型
        response = llm_with_tools.invoke(llm_messages)
        print(f"call_model: 收到响应 - 类型: {type(response).__name__}, tool_calls: {getattr(response, 'tool_calls', None)}")

        return {"messages": [response]}

    # 使用 ToolNode 处理工具调用
    tool_node = ToolNode(tools)
    print(f"create_agent_graph: 创建 ToolNode，工具数: {len(tools)}")

    # 构建图
    builder = StateGraph(AgentState)

    # 添加节点
    builder.add_node("agent", call_model)
    builder.add_node("tools", tool_node)

    # 添加边
    builder.add_edge(START, "agent")

    # 条件路由：检查是否需要调用工具
    def should_call_tools(state: AgentState) -> Literal["tools", "end"]:
        """判断是否需要执行工具"""
        messages = state.get("messages", [])
        if not messages:
            return "end"

        last_message = messages[-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            print(f"should_call_tools: 检测到 tool_calls，调用 tools")
            return "tools"
        print(f"should_call_tools: 无 tool_calls，结束")
        return "end"

    builder.add_conditional_edges(
        "agent",
        should_call_tools,
        {
            "tools": "tools",
            "end": END,
        }
    )

    # 工具执行完成后回到 agent
    builder.add_edge("tools", "agent")

    # 编译图
    from app.persistence import get_checkpointer
    checkpointer = get_checkpointer()

    graph = builder.compile(checkpointer=checkpointer)
    print(f"create_agent_graph: 图编译完成")

    return graph


# 全局 Agent 图实例
_agent_graph = None


def get_agent_graph():
    """
    获取 Agent 图实例（单例模式）

    Returns:
        编译好的 StateGraph
    """
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = create_agent_graph()
    return _agent_graph