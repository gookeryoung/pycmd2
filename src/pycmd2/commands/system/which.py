#!/usr/bin/env python3
"""用法: 在系统路径中查找可执行文件匹配项.

命令: wch
"""

from __future__ import annotations

import logging
import os
import subprocess
from functools import partial
from typing import List
from typing import Optional

import typer

from pycmd2.client import get_client
from pycmd2.commands.runner import SubcommandRunner

StrList = List[str]

cli = get_client()
logger = logging.getLogger(__name__)

_commands_arg = typer.Argument(help="待查询命令")
_fuzzy_option = typer.Option(False, "--fuzzy", "-f", help="是否模糊匹配")


def find_executable(name: str, *, fuzzy: bool) -> None:
    """跨平台查找可执行文件路径."""
    try:
        # 根据系统选择命令
        match_name = name if not fuzzy else f"*{name}*.exe"
        cmd = ["where" if cli.is_windows else "which", match_name]

        # 执行命令并捕获输出
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True,
        )

        # 处理 Windows 多结果情况
        paths = result.stdout.strip().split("\n")
        executable_path = paths[0] if cli.is_windows else result.stdout.strip()

    except (subprocess.CalledProcessError, FileNotFoundError):
        # 检查 UNIX 系统的直接可执行路径
        if not cli.is_windows and os.access(f"/usr/bin/{name}", os.X_OK):
            executable_path = f"/usr/bin/{name}"
            logger.info(f"找到命令: [[green bold]{executable_path}[/]]")
            return
        logger.warning(f"未找到符合的命令: [[red bold]{cmd}[/]]")
    else:
        logger.info(f"找到命令: [[green bold]{executable_path}[/]]")


class WhichRunner(SubcommandRunner):
    """查找可执行文件."""

    def run(
        self,
        *,
        fuzzy: bool = False,
        commands: Optional[List[str]] = None,
    ) -> None:
        """执行系列命令."""
        if commands is None:
            commands = []
        super().run()

        cli = get_client()
        which_func = partial(find_executable, fuzzy=fuzzy)
        cli.run(which_func, commands)


@cli.app.command()
def main(
    commands: List[str] = _commands_arg,
    *,
    fuzzy: bool = _fuzzy_option,
) -> None:
    runner = WhichRunner()
    runner.run(fuzzy=fuzzy, commands=commands)

    for cmd in commands:
        path = find_executable(cmd, fuzzy=fuzzy)
        if path:
            logger.info(f"找到命令: [[green bold]{path}[/]]")
        else:
            logger.error(f"未找到符合的命令: [[red bold]{cmd}[/]]")
