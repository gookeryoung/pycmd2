from __future__ import annotations

import logging
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Set

from pycmd2.client import get_client

from .build import get_build_command

__all__ = ("get_runner",)

cli = get_client()
logger = logging.getLogger(__name__)


class BaseRunner:
    """BaseRunner 基类."""

    DESCRIPTION: str = ""
    SUBCOMMANDS: ClassVar[Set[Set[str] | str | Callable[..., Any]]] = set()

    def run(self) -> None:
        """执行系列命令."""
        if self.DESCRIPTION:
            logger.info(f"功能描述: {self.DESCRIPTION}")

        if not self.SUBCOMMANDS:
            logger.info("没有子命令, 退出")
            return

        for subcommand in self.SUBCOMMANDS:
            if isinstance(subcommand, str):
                if subcommand not in _runner_keys:
                    logger.error(f"未找到执行器: {subcommand}")
                    continue

                logger.info(f"执行子命令: {subcommand}")
                get_runner(subcommand).run()
            elif isinstance(subcommand, set):
                cli.run_cmd(list(subcommand))
            elif isinstance(subcommand, Callable):
                subcommand()
            else:
                logger.error(f"未知子命令: {subcommand}")


class EmptyRunner(BaseRunner):
    """EmptyRunner 类."""

    def run(self) -> None:
        """Run command."""
        logger.info("没有子命令, 退出")


def _activate_py_env() -> None:
    if cli.is_windows:
        cli.run_cmdstr(f"cmd /c {cli.cwd / '.venv' / 'Scripts' / 'activate.bat'}")
    else:
        cli.run_cmdstr(f"source {cli.cwd / '.venv' / 'bin' / 'activate'}", executable="/bin/bash")


class ActivateRunner(BaseRunner):
    """ActivateRunner 类."""

    DESCRIPTION = "激活项目环境, 别名: act / activate"
    SUBCOMMANDS: ClassVar = {_activate_py_env}


def _run_func() -> None:
    """Run command."""
    build_tool = get_build_command()

    if build_tool is None:
        logger.error("未找到构建工具, 退出")
        return

    build_tool.run()


class BuildRunner(BaseRunner):
    """BuildRunner 类."""

    DESCRIPTION = "构建项目, 别名: b"
    SUBCOMMANDS: ClassVar = {_run_func}


_runners: dict[str, BaseRunner] = {
    "activate": ActivateRunner(),
    "build": BuildRunner(),
}
_runner_keys = set(_runners.keys())


def get_runner(command: str) -> BaseRunner:
    """获取执行器.

    Args:
        command (str): 命令

    Returns:
        BaseRunner: 执行器
    """
    runner = _runners.get(command)
    if runner is None:
        logger.error(f"未找到执行器: {command}")
        return EmptyRunner()

    return runner
