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
from typing import Tuple

import typer

from pycmd2.client import get_client
from pycmd2.commands import ParallelRunner

cli = get_client()
logger = logging.getLogger(__name__)


def find_executable(name: str, *, fuzzy: bool) -> Tuple[str, Optional[str]]:
    """跨平台查找可执行文件路径.

    Returns:
        Tuple[str, Optional[str]]: 命令名称和路径.
    """
    try:
        # 根据系统选择命令
        match_name = name if not fuzzy else f"*{name}*.exe"
        cmd = ["where" if cli.is_windows else "which", match_name]
        logger.info(f"执行命令: [green b]{cmd}")

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
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 检查 UNIX 系统的直接可执行路径
        if not cli.is_windows and os.access(f"/usr/bin/{name}", os.X_OK):
            return name, f"/usr/bin/{name}"
        return name, None
    else:
        return (name, paths[0]) if cli.is_windows else (name, result.stdout.strip())


_commands_arg = typer.Argument(help="待查询命令")
_fuzzy_option = typer.Option(False, "--fuzzy", "-f", help="是否模糊匹配")


@cli.app.command()
def main(
    commands: List[str] = _commands_arg,
    *,
    fuzzy: bool = _fuzzy_option,
) -> None:
    results = ParallelRunner().run(
        partial(find_executable, fuzzy=fuzzy),
        commands,
    )

    for name, exepath in results:
        if exepath:
            logger.info(f"找到 `{name}` 对应命令: [{exepath}]")
        else:
            logger.warning(f"未找到 `{name}` 对应命令.")
