#!/usr/bin/env python3
"""Usage: Find executable matches in system path.

Command: wch
"""

from __future__ import annotations

import logging
import os
import subprocess
from typing import List

from typer import Argument
from typer import Option
from typing_extensions import Annotated

from pycmd2.client import get_client

StrList = List[str]

cli = get_client()
logger = logging.getLogger(__name__)


def find_executable(name: str, *, fuzzy: bool) -> str | None:
    """跨平台查找可执行文件路径.

    Returns:
        str | None: 可执行文件路径, 如果未找到则返回 None
    """
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
        return paths[0] if cli.is_windows else result.stdout.strip()

    except (subprocess.CalledProcessError, FileNotFoundError):
        # 检查 UNIX 系统的直接可执行路径
        if not cli.is_windows and os.access(f"/usr/bin/{name}", os.X_OK):
            return f"/usr/bin/{name}"
        return None


@cli.app.command()
def main(
    commands: Annotated[StrList, Argument(help="待查询命令")],
    *,
    fuzzy: Annotated[
        bool,
        Option("--fuzzy", help="是否模糊匹配"),
    ] = False,
) -> None:
    for cmd in commands:
        path = find_executable(cmd, fuzzy=fuzzy)
        if path:
            logger.info(f"找到命令: [[green bold]{path}[/]]")
        else:
            logger.error(f"未找到符合的命令: [[red bold]{cmd}[/]]")
