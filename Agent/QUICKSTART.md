# 🚀 快速启动指南

欢迎使用 LangGraph Agent！按照以下步骤快速启动项目。

## 📋 前置要求

- Python 3.10 或更高版本
- Node.js 18 或更高版本
- npm 或 yarn

## 🔧 安装步骤

### 方法 1：使用启动脚本（推荐）

**Windows (PowerShell)**:
```powershell
cd Agent
.\start.ps1
```

**Linux/Mac**:
```bash
cd Agent
chmod +x start.sh
./start.sh
```

### 方法 2：手动启动

#### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 2. 配置环境变量

编辑 `backend/.env` 文件（已默认配置好 SiliconFlow API）：
```env
SILICONFLOW_API_KEY=sk-pkjxikgkwjdvpmszfxhmzydlaqwcrgjamuxyotbjxmdrbpmb
SILICONFLOW_MODEL=deepseek-ai/DeepSeek-V3
```

#### 3. 启动后端

```bash
cd backend
python main.py
```

后端将在 http://localhost:8000 启动

#### 4. 安装前端依赖（新终端）

```bash
cd frontend
npm install
```

#### 5. 启动前端（新终端）

```bash
npm run dev
```

前端将在 http://localhost:5173 启动

## 🎯 访问应用

- **前端界面**: http://localhost:5173
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## ✅ 测试功能

1. 打开浏览器访问 http://localhost:5173
2. 在聊天框中输入消息
3. 点击"发送"按钮
4. 查看 AI 助手的回复

## 🔍 故障排除

### 后端启动失败

**错误**: `ModuleNotFoundError`
```bash
# 解决方案：重新安装依赖
cd backend
pip install -r requirements.txt --force-reinstall
```

**错误**: 端口被占用
```bash
# 解决方案：修改端口
# 编辑 backend/.env 文件
PORT=8001
```

### 前端启动失败

**错误**: `npm: command not found`
```bash
# 解决方案：安装 Node.js
# 访问 https://nodejs.org/ 下载安装
```

**错误**: 无法连接后端
```bash
# 解决方案：
# 1. 确认后端已启动
# 2. 检查 backend/.env 中的 CORS_ORIGINS 配置
# 3. 检查 frontend/vite.config.ts 中的代理配置
```

### API 调用失败

**错误**: `401 Unauthorized`
```bash
# 解决方案：检查 API Key 配置
# 编辑 backend/.env 文件
SILICONFLOW_API_KEY=sk-pkjxikgkwjdvpmszfxhmzydlaqwcrgjamuxyotbjxmdrbpmb
```

**错误**: `429 Too Many Requests`
```bash
# 解决方案：API 额度用尽
# 访问 https://account.siliconflow.cn/zh 查看额度
```

## 🛠️ 常用操作

### 查看日志

**后端日志**: 终端会实时显示日志
**前端日志**: 浏览器开发者工具 -> Console

### 停止服务

**手动启动的服务**:
- 后端：终端按 `Ctrl+C`
- 前端：终端按 `Ctrl+C`

**启动脚本**: 按 `Ctrl+C` 自动停止所有服务

### 清空对话

在前端界面点击"清空对话"按钮，或刷新页面。

## 📚 下一步

1. **添加自定义工具**: 参考 [DEVELOPMENT.md](./DEVELOPMENT.md)
2. **修改系统提示**: 编辑 `backend/app/agents/graph.py`
3. **切换模型**: 修改 `.env` 中的 `SILICONFLOW_MODEL`
4. **自定义 UI**: 编辑 `frontend/src/components/Chat.tsx`

## 🆘 获取帮助

- 查看 [README.md](./README.md) 了解项目架构
- 查看 [DEVELOPMENT.md](./DEVELOPMENT.md) 了解开发指南
- 查看 [LangGraph 文档](../LangGraph_Info/README.md) 了解 LangGraph

## 🎉 开始使用

现在你已经准备好了！享受你的 AI 助手吧！

---

**提示**: 首次启动可能需要几分钟安装依赖，请耐心等待。
