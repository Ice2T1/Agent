import { useState, useCallback } from 'react';
import type { ChatWindow } from '../types/chat';
import './ChatSidebar.css';

interface ChatSidebarProps {
  windows: ChatWindow[];
  activeWindowId: string | null;
  onSelectWindow: (windowId: string) => void;
  onCreateWindow: () => void;
  onDeleteWindow: (windowId: string) => void;
  isCreating: boolean;
}

export default function ChatSidebar({
  windows,
  activeWindowId,
  onSelectWindow,
  onCreateWindow,
  onDeleteWindow,
  isCreating,
}: ChatSidebarProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // 格式化时间显示
  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  // 获取窗口预览文本（最后一条消息）
  const getPreview = (window: ChatWindow) => {
    if (window.messages.length === 0) return '新对话';
    const lastMessage = window.messages[window.messages.length - 1];
    const preview = lastMessage.content.slice(0, 30);
    return preview + (lastMessage.content.length > 30 ? '...' : '');
  };

  // 处理删除
  const handleDelete = useCallback((e: React.MouseEvent, windowId: string) => {
    e.stopPropagation();
    setDeletingId(windowId);
    
    // 延迟执行删除，让用户看到反馈
    setTimeout(() => {
      onDeleteWindow(windowId);
      setDeletingId(null);
    }, 200);
  }, [onDeleteWindow]);

  return (
    <div className="chat-sidebar">
      <div className="sidebar-header">
        <h2>对话列表</h2>
        <button
          className="new-chat-btn"
          onClick={onCreateWindow}
          disabled={isCreating}
          title="新建对话"
        >
          {isCreating ? '创建中...' : '+ 新建对话'}
        </button>
      </div>

      <div className="windows-list">
        {windows.length === 0 ? (
          <div className="empty-state">
            <p>暂无对话</p>
            <p className="hint">点击上方按钮创建新对话</p>
          </div>
        ) : (
          windows.map((window) => (
            <div
              key={window.id}
              className={`window-item ${window.id === activeWindowId ? 'active' : ''} ${deletingId === window.id ? 'deleting' : ''}`}
              onClick={() => onSelectWindow(window.id)}
            >
              <div className="window-info">
                <div className="window-title">{window.title}</div>
                <div className="window-preview">{getPreview(window)}</div>
                <div className="window-time">{formatTime(window.updatedAt)}</div>
              </div>
              <button
                className="delete-btn"
                onClick={(e) => handleDelete(e, window.id)}
                title="删除对话"
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>

      <div className="sidebar-footer">
        <span>{windows.length} 个对话</span>
      </div>
    </div>
  );
}
