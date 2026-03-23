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

    # 如果有工具，绑定到 LLM
    if tools:
        llm_with_tools = llm.bind_tools(tools)
    else:
        llm_with_tools = llm

    # 定义节点
    def call_model(state: AgentState):
        """调用 LLM 模型"""
        messages = state.get("messages", [])

        # 添加系统提示
        system_message = SystemMessage(
            content="你是一个有帮助的 AI 助手。当用户询问需要实时信息时，请使用 search_web 工具进行搜索。搜索结果请以友好的方式呈现。"
        )

        # 处理消息：清除 AIMessage 中已执行的 tool_calls
        processed_messages = []
        for msg in messages:
            if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                msg = AIMessage(content=msg.content)
            processed_messages.append(msg)

        # 调用模型
        response = llm_with_tools.invoke([system_message] + processed_messages)

        return {"messages": [response]}

    # 使用 ToolNode 处理工具调用
    tool_node = ToolNode(tools)

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
            return "tools"
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