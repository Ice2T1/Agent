import { useState, useRef, useEffect } from 'react';
import { sendMessage, streamMessage } from '../services/api';
import type { Message } from '../types/chat';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './Chat.css';

interface ChatProps {
  className?: string;
  windowId: string;
  initialMessages: Message[];
  initialThreadId: string;
  onUpdateMessages: (messages: Message[]) => void;
  onUpdateThreadId: (threadId: string) => void;
}

export default function Chat({
  className,
  windowId,
  initialMessages,
  initialThreadId,
  onUpdateMessages,
  onUpdateThreadId,
}: ChatProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState<string>(initialThreadId);
  const [useStream, setUseStream] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // 当初始消息变化时更新（切换窗口时）
  useEffect(() => {
    setMessages(initialMessages);
    setThreadId(initialThreadId);
  }, [windowId, initialMessages, initialThreadId]);

  // 当消息变化时通知父组件
  useEffect(() => {
    onUpdateMessages(messages);
  }, [messages, onUpdateMessages]);

  // 当 threadId 变化时通知父组件
  useEffect(() => {
    onUpdateThreadId(threadId);
  }, [threadId, onUpdateThreadId]);

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

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    // 添加占位助手消息
    setMessages(prev => [
      ...prev,
      { role: 'assistant', content: '' },
    ]);

    try {
      if (useStream) {
        const accumulatedContentRef = { current: '' };
        let lastUpdateTime = Date.now();
        const UPDATE_INTERVAL = 50;

        abortControllerRef.current = await streamMessage(
          {
            message: userMessage.content,
            thread_id: threadId,
          },
          (chunk) => {
            accumulatedContentRef.current += chunk;
            const now = Date.now();
            if (now - lastUpdateTime >= UPDATE_INTERVAL) {
              lastUpdateTime = now;
              setMessages(prev => {
                const newMessages = prev.map((msg, idx) =>
                  idx === prev.length - 1
                    ? { ...msg, content: accumulatedContentRef.current }
                    : msg
                );
                return newMessages;
              });
            }
          },
          () => {
            setMessages(prev => {
              const newMessages = prev.map((msg, idx) =>
                idx === prev.length - 1
                  ? { ...msg, content: accumulatedContentRef.current }
                  : msg
              );
              return newMessages;
            });
            setIsLoading(false);
          },
          (error) => {
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
        const response = await sendMessage({
          message: userMessage.content,
          thread_id: threadId,
        });

        setMessages(prev => {
          const newMessages = prev.map((msg, idx) =>
            idx === prev.length - 1
              ? { ...msg, content: response.message }
              : msg
          );
          return newMessages;
        });

        setIsLoading(false);
      }
    } catch (error) {
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
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>开始与 AI 助手对话吧！</p>
            <p className="hint">支持流式传输，实时显示回复内容</p>
          </div>
        ) : (
          messages.map((msg, index) => {
            const isLastMessage = index === messages.length - 1;
            const isThinking = isLoading && isLastMessage && msg.role === 'assistant' && !msg.content;
            
            return (
              <div
                key={index}
                className={`message ${msg.role}`}
              >
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  {isThinking ? (
                    <div className="thinking-indicator">
                      <span className="dot"></span>
                      <span className="dot"></span>
                      <span className="dot"></span>
                    </div>
                  ) : (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  )}
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入消息..."
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
