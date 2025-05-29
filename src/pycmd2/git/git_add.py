"""
功能：增加文件到 git 目录, 显示新增的文件清单
命令: gitadd
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Set
from typing import Tuple

from pycmd2.common.cli import get_client

cli = get_client()


def get_changed_files() -> Set[Tuple[str, str]]:
    """获取git状态变化的文件列表"""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
    )
    files = set()
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if line.strip():
                status = line[:2].strip()
                filename = line[3:].strip()
                files.add((status, filename))
    return files


@cli.app.command()
def main():
    os.chdir(str(cli.CWD))

    before = get_changed_files()
    cli.run_cmd(["git", "add", "."])
    after = get_changed_files()

    added_files = after - before

    # 显示结果
    if added_files:
        logging.info(f"新增的文件:{added_files}")
        cli.run_cmd([
            "git",
            "commit",
            "-m",
            f"新增文件: {''.join(list(Path(f[1]).stem for f in added_files))}",
        ])
    else:
        logging.warning("没有新增文件")
