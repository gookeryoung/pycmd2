from __future__ import annotations

from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from fastapi_offline import FastAPIOffline

from pycmd2.websvr.api.todo import router as todo_router

# 获取前端构建目录
FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "deploy"

app = FastAPIOffline(
    title="PyCmd2 Web API",
    description="PyCmd2 Web API",
    version="1.0.0",
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查
@app.get("/health")
def health_check() -> dict:
    """健康检查端点."""
    return {"status": "healthy", "service": "PyCmd2 Todo API"}


# 包含API路由
app.include_router(todo_router)
