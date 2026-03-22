#!/bin/bash
# LangGraph Agent 快速启动脚本

echo "🚀 启动 LangGraph Agent..."

# 检查 Python
if ! command -v python &> /dev/null; then
    echo "❌ 未找到 Python，请先安装 Python 3.10+"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js，请先安装 Node.js 18+"
    exit 1
fi

# 启动后端
echo "📦 启动后端服务..."
cd backend

# 检查依赖
if ! pip show fastapi &> /dev/null; then
    echo "📥 安装后端依赖..."
    pip install -r requirements.txt
fi

# 启动后端（后台运行）
python main.py &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
sleep 3

# 启动前端
echo "🎨 启动前端服务..."
cd ../frontend

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📥 安装前端依赖..."
    npm install
fi

# 启动前端
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

echo ""
echo "======================================"
echo "✨ 服务启动完成！"
echo "======================================"
echo "📡 后端：http://localhost:8000"
echo "📚 API 文档：http://localhost:8000/docs"
echo "🎨 前端：http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '👋 服务已停止'; exit 0" INT
