# 🚀 安装指南

## 后端安装

### 方式 1：使用 pip（推荐）

```bash
cd backend
pip install -r requirements.txt
```

**如果遇到权限错误**，请使用管理员权限运行：
```bash
# Windows（管理员 PowerShell）
pip install -r requirements.txt --user

# 或使用 conda
conda install --file requirements.txt
```

### 方式 2：使用 conda

```bash
cd backend
conda create -n langgraph-agent python=3.10
conda activate langgraph-agent
pip install -r requirements.txt
```

## 前端安装

### 方式 1：直接安装

```bash
cd frontend
npm install --legacy-peer-deps
```

### 方式 2：清理后重新安装（如果遇到问题）

```bash
cd frontend
# 清理
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json
npm cache clean --force

# 重新安装
npm install --legacy-peer-deps
```

### 方式 3：使用 yarn

```bash
cd frontend
yarn install
```

## 验证安装

### 后端验证

```bash
cd backend
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import langgraph; print('LangGraph:', langgraph.__version__)"
```

应该看到版本号输出。

### 前端验证

```bash
cd frontend
npm list react
npm list axios
```

应该看到已安装的包和版本号。

## 常见问题

### 后端权限错误

**错误**: `WinError 5 拒绝访问`

**解决方案**:
1. 使用 `--user` 参数安装
2. 使用管理员权限运行终端
3. 使用虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 前端 esbuild 错误

**错误**: `EBUSY` 或 `command failed`

**解决方案**:
1. 关闭所有使用 node 的程序
2. 清理缓存重新安装

```bash
npm cache clean --force
Remove-Item -Recurse -Force node_modules
npm install --legacy-peer-deps
```

### TypeScript 找不到模块

**错误**: `Cannot find module 'react'`

**原因**: node_modules 未正确安装

**解决方案**:
```bash
cd frontend
npm install
```

确保安装完成后，TypeScript 会自动识别类型定义。

## 启动服务

### 后端

```bash
cd backend
python main.py
```

访问 http://localhost:8000/docs

### 前端

```bash
cd frontend
npm run dev
```

访问 http://localhost:5173

## 完整安装检查清单

- [ ] Python 3.10+ 已安装
- [ ] Node.js 18+ 已安装
- [ ] 后端依赖安装成功
- [ ] 前端依赖安装成功
- [ ] 后端服务可以启动
- [ ] 前端服务可以启动
- [ ] API 文档可以访问
- [ ] 前端页面可以访问

## 下一步

安装完成后，参考 [QUICKSTART.md](./QUICKSTART.md) 启动服务。
