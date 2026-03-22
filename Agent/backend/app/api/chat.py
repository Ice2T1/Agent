"""
聊天 API 路由
"""
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, StreamChunk
from app.agents import get_agent_graph
from app.persistence import get_checkpointer
import uuid

router = APIRouter(prefix="/chat", tags=["聊天"])


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    发送消息并获取回复
    
    Args:
        request: 聊天请求
        
    Returns:
        聊天响应
    """
    print(f"收到消息请求：{request.message}")
    try:
        # 生成或使用提供的 thread_id
        thread_id = request.thread_id or str(uuid.uuid4())
        print(f"使用 thread_id: {thread_id}")
        
        # 获取 Agent 图和检查点器
        print("正在获取 Agent 图...")
        graph = get_agent_graph()
        checkpointer = get_checkpointer()
        
        # 准备配置
        config = {"configurable": {"thread_id": thread_id}}
        
        # 准备输入
        from langchain_core.messages import HumanMessage
        input_data = {
            "messages": [HumanMessage(content=request.message)],
            "metadata": request.metadata or {},
        }
        
        print("正在调用 Agent...")
        # 调用 Agent
        result = graph.invoke(input_data, config)
        print(f"Agent 调用完成，收到 {len(result.get('messages', []))} 条消息")
        
        # 提取回复
        messages = result.get("messages", [])
        assistant_message = ""
        
        for msg in reversed(messages):
            if hasattr(msg, 'type') and msg.type == "ai":
                assistant_message = msg.content
                break
        
        print(f"提取到助手消息：{assistant_message[:50] if assistant_message else 'None'}...")
        
        # 获取检查点信息
        checkpoint_id = None
        if checkpointer:
            state = graph.get_state(config)
            if state and hasattr(state, 'config'):
                checkpoint_id = state.config.get("configurable", {}).get("checkpoint_id")
        
        return ChatResponse(
            message=assistant_message,
            thread_id=thread_id,
            checkpoint_id=checkpoint_id,
            metadata={"message_count": len(messages)},
        )
        
    except Exception as e:
        print(f"处理消息时出错：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_message(request: ChatRequest):
    """
    流式发送消息（SSE）
    
    Args:
        request: 聊天请求
        
    Yields:
        流式传输块
    """
    from fastapi.responses import StreamingResponse
    import json
    
    print(f"收到流式请求：{request.message}")
    try:
        thread_id = request.thread_id or str(uuid.uuid4())
        print(f"使用 thread_id: {thread_id}")
        
        print("正在获取 Agent 图...")
        graph = get_agent_graph()
        config = {"configurable": {"thread_id": thread_id}}
        
        from langchain_core.messages import HumanMessage
        input_data = {
            "messages": [HumanMessage(content=request.message)],
            "metadata": request.metadata or {},
        }
        
        async def generate():
            try:
                # 流式调用
                print("开始流式调用 Agent...")
                async for chunk in graph.astream(input_data, config):
                    print(f"收到 chunk: {chunk}")
                    print(f"chunk 类型：{type(chunk)}")
                    if isinstance(chunk, dict):
                        print(f"chunk keys: {chunk.keys()}")
                    
                    # LangGraph 返回的 chunk 可能是 {'agent': {'messages': [...]}} 格式
                    # 需要递归提取 messages
                    def extract_messages(chunk_data):
                        """递归提取 messages"""
                        messages = []
                        if isinstance(chunk_data, dict):
                            if 'messages' in chunk_data:
                                messages.extend(chunk_data['messages'])
                            # 递归检查其他 key
                            for key, value in chunk_data.items():
                                if key != 'messages':
                                    messages.extend(extract_messages(value))
                        elif isinstance(chunk_data, list):
                            for item in chunk_data:
                                messages.extend(extract_messages(item))
                        return messages
                    
                    messages = extract_messages(chunk)
                    print(f"提取到 {len(messages)} 条消息")
                    
                    for msg in messages:
                        print(f"msg 类型：{type(msg)}, 内容：{msg.content if hasattr(msg, 'content') else 'N/A'}")
                        if hasattr(msg, 'content'):
                            data = StreamChunk(
                                type="token",
                                content=msg.content,
                            ).model_dump()
                            print(f"发送数据：{data}")
                            yield f"data: {json.dumps(data)}\n\n"
                
                # 结束标记
                print("流式传输完成")
                yield "data: [DONE]\n\n"
            except Exception as e:
                print(f"流式生成时出错：{e}")
                import traceback
                traceback.print_exc()
                raise
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
        )
        
    except Exception as e:
        print(f"流式请求出错：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads/{thread_id}/state")
async def get_thread_state(thread_id: str):
    """
    获取线程状态
    
    Args:
        thread_id: 线程 ID
        
    Returns:
        线程状态信息
    """
    try:
        graph = get_agent_graph()
        config = {"configurable": {"thread_id": thread_id}}
        
        state = graph.get_state(config)
        
        if not state:
            raise HTTPException(status_code=404, detail="线程不存在")
        
        # 提取状态信息
        values = state.values if hasattr(state, 'values') else {}
        messages = values.get("messages", [])
        
        return {
            "thread_id": thread_id,
            "message_count": len(messages),
            "last_checkpoint": state.config.get("configurable", {}).get("checkpoint_id") if hasattr(state, 'config') else None,
            "metadata": values.get("metadata", {}),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
