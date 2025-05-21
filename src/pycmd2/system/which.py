#!/usr/bin/env python3
import logging
import os
import subprocess
from typing import List

from typer import Argument

from pycmd2.common.cli import get_client

cli = get_client()


def find_executable(name: str):
    """跨平台查找可执行文件路径"""

    try:
        # 根据系统选择命令
        cmd = ["where" if cli.IS_WINDOWS else "which", name]

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
def main(commmands: List[str] = Argument(help="待查询命令")):  # noqa: B008
    for cmd in commmands:
        path = find_executable(cmd)
        if path:
            logging.info(f"找到命令: [[green bold]{path}[/]]")
        else:
            logging.error(f"未找到符合的命令: [[red bold]{cmd}[/]]")


if __name__ == "__main__":
    main()
