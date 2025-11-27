from __future__ import annotations

from typing import Generator

from fastapi import Depends
from sqlmodel import create_engine
from sqlmodel import Session
from sqlmodel import SQLModel
from typing_extensions import Annotated

__all__ = ["SessionDep", "create_db_and_tables"]

_sqlite_file_name = "database.db"
_sqlite_url = f"sqlite:///{_sqlite_file_name}"
_connect_args = {"check_same_thread": False}
_engine = create_engine(_sqlite_url, connect_args=_connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(_engine)


def _get_session() -> Generator[Session, None, None]:
    """生成数据库会话.

    Yields:
        Generator[Session, None, None]: 数据库会话生成器
    """
    with Session(_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(_get_session)]
