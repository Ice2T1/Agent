import axios from 'axios';
import type { ChatRequest, ChatResponse, ThreadState } from '../types/chat';

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000, // 60 秒超时
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 发送聊天消息
 */
export const sendMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>('/chat/message', request);
  return response.data;
};

/**
 * 获取线程状态
 */
export const getThreadState = async (threadId: string): Promise<ThreadState> => {
  const response = await api.get<ThreadState>(`/chat/threads/${threadId}/state`);
  return response.data;
};

/**
 * 流式发送消息
 */
export const streamMessage = async (
  request: ChatRequest,
  onChunk: (chunk: string) => void,
  onComplete?: () => void,
  onError?: (error: Error) => void
): Promise<AbortController> => {
  const controller = new AbortController();
  
  const fetchStream = async () => {
    try {
      const url = '/api/v1/chat/stream';
      console.log('请求 URL:', url);
      console.log('请求参数:', request);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      console.log('响应状态码:', response.status);
      console.log('响应 OK:', response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('错误响应:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('ReadableStream not supported');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log('流式读取完成');
          onComplete?.();
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        console.log('原始 chunk:', chunk);
        buffer += chunk;

        // 解析 SSE 格式
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // 保留不完整的行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              onComplete?.();
              return;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                onChunk(parsed.content);
              }
            } catch (e) {
              console.error('Failed to parse chunk:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('流式请求错误:', error);
      if (error instanceof Error && error.name === 'AbortError') {
        // 用户取消，不处理错误
        return;
      }
      onError?.(error as Error);
    }
  };

  fetchStream();
  
  return controller;
};

export default api;
