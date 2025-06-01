#!/usr/bin/env python3
import logging
import os
import subprocess
from typing import List

from typer import Argument
from typer import Option
from typing_extensions import Annotated

from pycmd2.common.cli import get_client

cli = get_client()


def find_executable(name: str, fuzzy: bool):
    """跨平台查找可执行文件路径"""

    try:
        # 根据系统选择命令
        match_name = name if not fuzzy else f"*{name}*.exe"
        cmd = ["where" if cli.IS_WINDOWS else "which", match_name]

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
        return paths[0] if cli.IS_WINDOWS else result.stdout.strip()

    except (subprocess.CalledProcessError, FileNotFoundError):
        # 检查 UNIX 系统的直接可执行路径
        if not cli.IS_WINDOWS and os.access(f"/usr/bin/{name}", os.X_OK):
            return f"/usr/bin/{name}"
        return None


@cli.app.command()
def main(
    commmands: Annotated[List[str], Argument(help="待查询命令")],
    fuzzy: Annotated[
        bool, Option("--fuzzy", "-F", help="是否模糊匹配")
    ] = False,
):
    for cmd in commmands:
        path = find_executable(cmd, fuzzy=fuzzy)
        if path:
            logging.info(f"找到命令: [[green bold]{path}[/]]")
        else:
            logging.error(f"未找到符合的命令: [[red bold]{cmd}[/]]")
