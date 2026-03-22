# LangGraph Agent 快速启动脚本 (PowerShell)

Write-Host "🚀 启动 LangGraph Agent..." -ForegroundColor Green

# 检查 Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 未找到 Python，请先安装 Python 3.10+" -ForegroundColor Red
    exit 1
}

# 检查 Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 未找到 Node.js，请先安装 Node.js 18+" -ForegroundColor Red
    exit 1
}

# 启动后端
Write-Host "`n📦 启动后端服务..." -ForegroundColor Cyan
Set-Location backend

# 检查依赖
$fastapiInstalled = pip show fastapi 2>&1
if ($fastapiInstalled -like "*not found*") {
    Write-Host "📥 安装后端依赖..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# 启动后端
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD/backend
    python main.py
}
Write-Host "✅ 后端服务已启动 (PID: $($backendJob.Id))" -ForegroundColor Green

# 等待后端启动
Start-Sleep -Seconds 3

# 启动前端
Write-Host "`n🎨 启动前端服务..." -ForegroundColor Cyan
Set-Location ../frontend

# 检查依赖
if (-not (Test-Path "node_modules")) {
    Write-Host "📥 安装前端依赖..." -ForegroundColor Yellow
    npm install
}

# 启动前端
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD/frontend
    npm run dev
}
Write-Host "✅ 前端服务已启动 (PID: $($frontendJob.Id))" -ForegroundColor Green

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "✨ 服务启动完成！" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host "📡 后端：http://localhost:8000" -ForegroundColor White
Write-Host "📚 API 文档：http://localhost:8000/docs" -ForegroundColor White
Write-Host "🎨 前端：http://localhost:5173" -ForegroundColor White
Write-Host "`n按 Ctrl+C 停止所有服务" -ForegroundColor Yellow

# 等待用户中断
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host "`n👋 停止服务..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob, $frontendJob
    Remove-Job -Job $backendJob, $frontendJob
    Write-Host "服务已停止" -ForegroundColor Green
}
