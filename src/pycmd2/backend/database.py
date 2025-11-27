from __future__ import annotations

from typing import Generator

from fastapi import Depends
from sqlmodel import create_engine
from sqlmodel import Session
from sqlmodel import SQLModel
from typing_extensions import Annotated

from pycmd2.client import get_client

__all__ = ["SessionDep", "create_db_and_tables"]

client = get_client()

_sqlite_file_name = "web_server.db"
_sqlite_file_path = client.settings_dir / _sqlite_file_name
_sqlite_url = f"sqlite:///{_sqlite_file_path}"
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
