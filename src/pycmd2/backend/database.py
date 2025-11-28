from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from fastapi import Depends
from sqlmodel import create_engine
from sqlmodel import Session
from sqlmodel import SQLModel
from typing_extensions import Annotated

from pycmd2.client import get_client

__all__ = ["SessionDep", "create_db_and_tables", "get_db_session"]

client = get_client()
logger = logging.getLogger(__name__)

_sqlite_file_name = "web_server.db"
_sqlite_file_path = client.settings_dir / _sqlite_file_name
_sqlite_url = f"sqlite:///{_sqlite_file_path}"

# 改进的连接配置，添加连接池设置
_connect_args = {
    "check_same_thread": False,
    "timeout": 30,  # 添加超时设置
}
_engine = create_engine(
    _sqlite_url,
    connect_args=_connect_args,
    pool_pre_ping=True,  # 连接前检查连接是否有效
    echo=False,  # 生产环境中关闭SQL日志
)


def create_db_and_tables() -> None:
    """创建数据库和表."""
    try:
        SQLModel.metadata.create_all(_engine)
        logger.info(f"数据库表已创建: {_sqlite_file_path}")
    except Exception as e:
        logger.exception(f"创建数据库表失败: {e}")
        raise


def _get_session() -> Generator[Session, None, None]:
    """生成数据库会话.

    Yields:
        Generator[Session, None, None]: 数据库会话生成器
    """
    session = None
    try:
        session = Session(_engine)
        yield session
        session.commit()  # 成功时提交事务
    except Exception as e:
        logger.exception(f"数据库会话错误: {e}")
        if session:
            session.rollback()  # 出错时回滚事务
        raise
    finally:
        if session:
            session.close()  # 确保会话关闭


@contextmanager
def get_db_session():
    """获取数据库会话的上下文管理器.

    使用示例:
        with get_db_session() as session:
            # 数据库操作

    Returns:
        Session: 数据库会话
    """
    session = None
    try:
        session = Session(_engine)
        yield session
        session.commit()
    except Exception as e:
        logger.exception(f"数据库操作错误: {e}")
        if session:
            session.rollback()
        raise
    finally:
        if session:
            session.close()


SessionDep = Annotated[Session, Depends(_get_session)]
