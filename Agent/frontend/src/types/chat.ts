/**
 * 聊天消息类型
 */
export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

/**
 * 聊天请求
 */
export interface ChatRequest {
  message: string;
  thread_id?: string;
  metadata?: Record<string, any>;
}

/**
 * 聊天响应
 */
export interface ChatResponse {
  message: string;
  thread_id: string;
  checkpoint_id?: string;
  metadata?: Record<string, any>;
}

/**
 * 线程状态
 */
export interface ThreadState {
  thread_id: string;
  message_count: number;
  last_checkpoint?: string;
  metadata?: Record<string, any>;
}

/**
 * 流式数据块
 */
export interface StreamChunk {
  type: 'token' | 'message' | 'error';
  content?: string;
  data?: any;
}

/**
 * 对话窗口
 */
export interface ChatWindow {
  id: string;
  title: string;
  messages: Message[];
  threadId: string;
  createdAt: number;
  updatedAt: number;
}
