from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi_offline import FastAPIOffline

from .database import create_db_and_tables
from .models import user

__all__ = ["app"]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:  # noqa: RUF029
    """应用生命周期管理器.

    Args:
        _: FastAPI应用实例

    Yields:
        None
    """
    create_db_and_tables()
    yield


app = FastAPIOffline(lifespan=lifespan)
app.include_router(user.router)
