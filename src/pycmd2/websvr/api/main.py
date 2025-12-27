from fastapi.middleware.cors import CORSMiddleware
from fastapi_offline import FastAPIOffline

from pycmd2.websvr.api.todo import router as todo_router

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

app.include_router(todo_router)
