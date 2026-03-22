import { useState, useEffect, useCallback, useRef } from 'react';
import Chat from './components/Chat';
import ChatSidebar from './components/ChatSidebar';
import type { ChatWindow, Message } from './types/chat';
import './App.css';

// 本地存储键
const STORAGE_KEY = 'chat_windows';
const STORAGE_ACTIVE_KEY = 'chat_active_window';

// 生成唯一ID
const generateId = () => `window-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

// 生成 thread ID
const generateThreadId = () => `thread-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

// 创建新窗口
const createNewWindow = (): ChatWindow => ({
  id: generateId(),
  title: '新对话',
  messages: [],
  threadId: generateThreadId(),
  createdAt: Date.now(),
  updatedAt: Date.now(),
});

function App() {
  // 所有窗口列表
  const [windows, setWindows] = useState<ChatWindow[]>([]);
  // 当前激活的窗口ID
  const [activeWindowId, setActiveWindowId] = useState<string | null>(null);
  // 是否正在创建窗口（防抖用）
  const [isCreating, setIsCreating] = useState(false);
  // 标记是否已经初始化
  const initializedRef = useRef(false);

  // 从本地存储加载数据
  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;

    try {
      const savedWindows = localStorage.getItem(STORAGE_KEY);
      const savedActiveId = localStorage.getItem(STORAGE_ACTIVE_KEY);

      if (savedWindows) {
        const parsed = JSON.parse(savedWindows);
        setWindows(parsed);
        
        // 恢复激活的窗口
        if (savedActiveId && parsed.find((w: ChatWindow) => w.id === savedActiveId)) {
          setActiveWindowId(savedActiveId);
        } else if (parsed.length > 0) {
          // 如果没有保存的激活窗口，使用最近更新的窗口
          const sorted = [...parsed].sort((a, b) => b.updatedAt - a.updatedAt);
          setActiveWindowId(sorted[0].id);
        }
      } else {
        // 首次进入，自动创建一个窗口
        const newWindow = createNewWindow();
        setWindows([newWindow]);
        setActiveWindowId(newWindow.id);
      }
    } catch (error) {
      console.error('加载本地数据失败:', error);
      // 出错时创建新窗口
      const newWindow = createNewWindow();
      setWindows([newWindow]);
      setActiveWindowId(newWindow.id);
    }
  }, []);

  // 保存到本地存储
  useEffect(() => {
    if (windows.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(windows));
    }
    if (activeWindowId) {
      localStorage.setItem(STORAGE_ACTIVE_KEY, activeWindowId);
    }
  }, [windows, activeWindowId]);

  // 获取当前激活的窗口
  const activeWindow = windows.find(w => w.id === activeWindowId) || null;

  // 创建新窗口（带防抖）
  const handleCreateWindow = useCallback(() => {
    if (isCreating) return; // 防止重复创建
    
    setIsCreating(true);
    
    const newWindow = createNewWindow();
    setWindows(prev => [newWindow, ...prev]);
    setActiveWindowId(newWindow.id);
    
    // 300ms 后解除防抖
    setTimeout(() => {
      setIsCreating(false);
    }, 300);
  }, [isCreating]);

  // 删除窗口
  const handleDeleteWindow = useCallback((windowId: string) => {
    setWindows(prev => {
      const newWindows = prev.filter(w => w.id !== windowId);
      
      // 如果删除的是当前激活窗口
      if (windowId === activeWindowId) {
        if (newWindows.length > 0) {
          // 切换到最近更新的窗口
          const sorted = [...newWindows].sort((a, b) => b.updatedAt - a.updatedAt);
          setActiveWindowId(sorted[0].id);
        } else {
          // 没有窗口了，自动创建一个新窗口
          const newWindow = createNewWindow();
          newWindows.push(newWindow);
          setActiveWindowId(newWindow.id);
        }
      }
      
      return newWindows;
    });
  }, [activeWindowId]);

  // 切换窗口
  const handleSelectWindow = useCallback((windowId: string) => {
    setActiveWindowId(windowId);
  }, []);

  // 更新窗口消息
  const handleUpdateMessages = useCallback((windowId: string, messages: Message[]) => {
    setWindows(prev => prev.map(w => {
      if (w.id === windowId) {
        // 自动更新标题（基于第一条用户消息）
        let title = w.title;
        if (title === '新对话' && messages.length > 0) {
          const firstUserMessage = messages.find(m => m.role === 'user');
          if (firstUserMessage) {
            title = firstUserMessage.content.slice(0, 20) + (firstUserMessage.content.length > 20 ? '...' : '');
          }
        }
        
        return {
          ...w,
          messages,
          title,
          updatedAt: Date.now(),
        };
      }
      return w;
    }));
  }, []);

  // 更新窗口的 threadId
  const handleUpdateThreadId = useCallback((windowId: string, threadId: string) => {
    setWindows(prev => prev.map(w => 
      w.id === windowId ? { ...w, threadId } : w
    ));
  }, []);

  return (
    <div className="app">
      <ChatSidebar
        windows={windows}
        activeWindowId={activeWindowId}
        onSelectWindow={handleSelectWindow}
        onCreateWindow={handleCreateWindow}
        onDeleteWindow={handleDeleteWindow}
        isCreating={isCreating}
      />
      <div className="main-content">
        {activeWindow ? (
          <Chat
            key={activeWindow.id}
            windowId={activeWindow.id}
            initialMessages={activeWindow.messages}
            initialThreadId={activeWindow.threadId}
            onUpdateMessages={(messages) => handleUpdateMessages(activeWindow.id, messages)}
            onUpdateThreadId={(threadId) => handleUpdateThreadId(activeWindow.id, threadId)}
          />
        ) : (
          <div className="no-window">
            <p>请创建一个新对话</p>
            <button onClick={handleCreateWindow}>新建对话</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
