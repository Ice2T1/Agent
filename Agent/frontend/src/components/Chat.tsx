import { useState, useRef, useEffect } from 'react';
import { sendMessage, streamMessage } from '../services/api';
import type { Message } from '../types/chat';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './Chat.css';

interface ChatProps {
  className?: string;
}

export default function Chat({ className }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [useStream, setUseStream] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 清理流式请求
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // 添加占位助手消息
    setMessages(prev => [
      ...prev,
      { role: 'assistant', content: '' },
    ]);

    try {
      console.log('开始发送消息，模式:', useStream ? '流式' : '普通');
      console.log('当前消息数量:', messages.length);
      
      if (useStream) {
        // 流式模式
        let accumulatedContent = '';
        
        // 如果是第一次对话，需要先生成 thread_id
        const currentThreadId = threadId || `thread-${Date.now()}`;
        if (!threadId) {
          setThreadId(currentThreadId);
        }
        
        console.log('开始流式请求...');
        abortControllerRef.current = await streamMessage(
          {
            message: userMessage.content,
            thread_id: currentThreadId,
          },
          (chunk) => {
            console.log('收到 chunk:', chunk);
            accumulatedContent += chunk;
            setMessages(prev => {
              const newMessages = prev.map((msg, idx) =>
                idx === prev.length - 1
                  ? { ...msg, content: accumulatedContent }
                  : msg
              );
              console.log('更新后消息数量:', newMessages.length);
              return newMessages;
            });
          },
          () => {
            console.log('流式传输完成');
            setIsLoading(false);
          },
          (error) => {
            console.error('Stream error:', error);
            setMessages(prev =>
              prev.map((msg, idx) =>
                idx === prev.length - 1
                  ? { ...msg, content: `错误：${error.message}` }
                  : msg
              )
            );
            setIsLoading(false);
          }
        );
      } else {
        // 普通模式
        console.log('发送普通请求...');
        const response = await sendMessage({
          message: userMessage.content,
          thread_id: threadId || undefined,
        });

        console.log('收到响应:', response);

        // 更新 threadId
        if (!threadId) {
          setThreadId(response.thread_id);
        }

        // 更新助手消息
        setMessages(prev => {
          const newMessages = prev.map((msg, idx) =>
            idx === prev.length - 1
              ? { ...msg, content: response.message }
              : msg
          );
          console.log('更新后消息数量:', newMessages.length);
          return newMessages;
        });

        setIsLoading(false);
      }
    } catch (error) {
      console.error('Send message error:', error);
      setMessages(prev =>
        prev.map((msg, idx) =>
          idx === prev.length - 1
            ? { ...msg, content: `错误：${error instanceof Error ? error.message : '未知错误'}` }
            : msg
        )
      );
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setThreadId(null);
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  };

  return (
    <div className={`chat-container ${className || ''}`}>
      <div className="chat-header">
        <h1>LangGraph Agent</h1>
        <div className="chat-controls">
          <label className="control-label">
            <input
              type="checkbox"
              checked={useStream}
              onChange={(e) => setUseStream(e.target.checked)}
              disabled={isLoading}
            />
            流式模式
          </label>
          <button
            onClick={handleClearChat}
            disabled={isLoading || messages.length === 0}
            className="clear-btn"
          >
            清空对话
          </button>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>开始与 AI 助手对话吧！</p>
            <p className="hint">支持流式传输，实时显示回复内容</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.role}`}
            >
              <div className="message-avatar">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content}
                </ReactMarkdown>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={isLoading ? 'AI 正在思考...' : '输入消息...'}
          disabled={isLoading}
          className="chat-input"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="send-btn"
        >
          {isLoading ? '发送中...' : '发送'}
        </button>
      </form>

      {threadId && (
        <div className="thread-info">
          Thread ID: {threadId.slice(0, 8)}...
        </div>
      )}
    </div>
  );
}
