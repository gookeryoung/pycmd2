from __future__ import annotations

from pathlib import Path

from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
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

# 挂载静态文件服务
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")


# 健康检查
@app.get("/health")
def health_check() -> dict:
    """健康检查端点."""
    return {"status": "healthy", "service": "PyCmd2 Todo API"}


# 包含API路由
app.include_router(todo_router)


# 处理前端路由的通配符路由，必须在API路由之后定义
@app.get("/{full_path:path}")
def serve_spa(request: Request, full_path: str) -> Response:
    """服务单页应用，处理前端路由的刷新问题."""
    # 如果路径包含文件扩展名，尝试作为静态文件提供
    if "." in full_path:
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)

    # 对于所有其他路径，返回index.html以支持前端路由
    index_path = FRONTEND_DIR / "index.html"
    if index_path.is_file():
        return FileResponse(index_path)

    return HTMLResponse(
        content=(
            "<h1>PyCmd2 WebUI</h1><p>Frontend build not found. "
            "Run `npm run build` to build the frontend.</p>"
        ),
    )
