from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from fastapi_offline import FastAPIOffline

from .database import create_db_and_tables

__all__ = ["app"]


@contextmanager
def lifespan() -> Generator[None, None, None]:
    """应用生命周期管理器.

    Yields:
        None
    """
    create_db_and_tables()
    yield


app = FastAPIOffline(lifespan=lifespan)
