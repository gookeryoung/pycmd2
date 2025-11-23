from __future__ import annotations

import logging
from typing import Any
from typing import Callable
from typing import ClassVar

from pycmd2.client import get_client

cli = get_client()
logger = logging.getLogger(__name__)


class BaseRunner:
    """BaseRunner 基类."""

    DESCRIPTION: str = ""
    CHILD_RUNNERS: ClassVar[dict[str, BaseRunner]] = {}
    SUBCOMMANDS: ClassVar[list[list[str] | str | Callable[..., Any]]] = []

    def run(self) -> None:
        """执行系列命令."""
        if self.DESCRIPTION:
            logger.info(f"功能描述: {self.DESCRIPTION}")

        if not self.SUBCOMMANDS:
            logger.info("没有子命令, 退出")
            return

        for subcommand in self.SUBCOMMANDS:
            if isinstance(subcommand, str):
                if subcommand.lower() not in self.CHILD_RUNNERS:
                    logger.error(f"未找到执行器: {subcommand}")
                    continue

                logger.info(f"执行子命令: {subcommand}")
                self.CHILD_RUNNERS[subcommand.lower()].run()
            elif isinstance(subcommand, list):
                cli.run_cmd(list(subcommand))
            elif isinstance(subcommand, Callable):
                logger.info(f"执行可调用对象: [purple b]{subcommand.__name__}")
                subcommand()
            else:
                logger.error(f"未知子命令: {subcommand}")

    @property
    def name(self) -> str:
        """获取执行器名称."""
        return self.__class__.__name__.replace("Runner", "").lower()
