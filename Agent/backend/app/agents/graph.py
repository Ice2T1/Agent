"""
Agent 图定义
使用 LangGraph 构建可对话的 Agent
"""
from typing import Literal, Annotated
from typing_extensions import TypedDict
from operator import add
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool

from app.core.llm import get_llm
from app.tools import get_all_tools


class AgentState(TypedDict):
    """
    Agent 状态
    
    定义 Agent 运行时的状态结构
    """
    # 消息历史，使用 add_messages 归约器
    messages: Annotated[list, add_messages]
    
    # 元数据
    metadata: dict


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
        print(f"call_model: 收到 {len(messages)} 条消息")
        
        # 添加系统提示
        system_message = SystemMessage(
            content="你是一个有帮助的 AI 助手。请友好、准确地回答用户的问题。"
        )
        
        print(f"call_model: 准备调用 LLM，总消息数：{len([system_message] + messages)}")
        # 调用模型
        response = llm_with_tools.invoke([system_message] + messages)
        print(f"call_model: 收到响应，类型：{type(response)}, 内容：{response.content if hasattr(response, 'content') else 'N/A'}")
        
        return {"messages": [response]}
    
    def execute_tools(state: AgentState):
        """执行工具调用"""
        messages = state.get("messages", [])
        if not messages:
            return {"messages": []}
        
        last_message = messages[-1]
        
        # 检查是否有工具调用
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            tool_results = []
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                
                # 查找并执行工具
                from app.tools import get_tool
                tool = get_tool(tool_name)
                
                if tool:
                    try:
                        result = tool.invoke(tool_args)
                        tool_results.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call.get("id"),
                            "name": tool_name,
                        })
                    except Exception as e:
                        tool_results.append({
                            "role": "tool",
                            "content": f"工具执行错误：{str(e)}",
                            "tool_call_id": tool_call.get("id"),
                            "name": tool_name,
                        })
            
            return {"messages": tool_results}
        
        return {"messages": []}
    
    # 构建图
    builder = StateGraph(AgentState)
    
    # 添加节点
    builder.add_node("agent", call_model)
    builder.add_node("tools", execute_tools)
    
    # 添加边
    builder.add_edge(START, "agent")
    builder.add_edge("tools", "agent")
    
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
