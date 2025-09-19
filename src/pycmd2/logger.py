from __future__ import annotations

import logging

from rich.logging import RichHandler

__all__ = [
    "Logger",
]


class Logger:
    """日志记录器."""

    __instance: logging.Logger | None = None

    @classmethod
    def get_instance(cls, name: str) -> logging.Logger:
        """获取日志记录器实例.

        Args:
            name (str): 模块名称.
            debug (bool, optional): 是否开启调试模式. Defaults to False.

        Returns:
            logging.Logger: 日志记录器实例.
        """
        if cls.__instance is None:
            logging.basicConfig(
                level=logging.INFO,
                format="[%(asctime)s] %(message)s",
                datefmt="%X",
                handlers=[RichHandler(markup=True)],
            )

            cls.__instance = logging.getLogger(name)
        return cls.__instance
