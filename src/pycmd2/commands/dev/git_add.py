"""功能: 增加文件到 git 目录, 显示新增的文件清单.

命令: gitadd
"""

from __future__ import annotations

import logging
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from pycmd2.client import get_client

cli = get_client()
logger = logging.getLogger(__name__)


@dataclass
class GitAddFileStatus:
    """Git文件状态数据类.

    Properties:
        status: 文件状态, A: 新增, M: 修改
        filepath: 文件路径
    """

    status: str
    filepath: Path

    def __hash__(self) -> int:
        """计算哈希值, 用于在集合中唯一标识.

        Returns:
            int: 哈希值
        """
        return hash((self.status, str(self.filepath)))


def get_changed_files_info() -> set[GitAddFileStatus]:
    """获取git状态变化的文件列表.

    Returns:
        set[GitAddFileStatus]: 文件状态列表
    """
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    files: set[GitAddFileStatus] = set()
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if line.strip():
                status = line[:2].strip()
                filename = line[3:].strip()
                files.add(GitAddFileStatus(status, Path(filename)))
    return files


@cli.app.command()
def main() -> None:
    os.chdir(str(cli.cwd))

    # 计算新增的文件
    before = get_changed_files_info()
    cli.run_cmd(["git", "add", "."])
    after = get_changed_files_info()

    # 计算新增的文件信息
    added_files_info = after - before
    added_filenames = {f.filepath.stem for f in added_files_info if f.status == "A"}
    modified_filenames = {f.filepath.stem for f in added_files_info if f.status == "M"}

    # 显示结果
    check_status = {
        "新增": added_filenames,
        "修改": modified_filenames,
    }
    for status, filenames in check_status.items():
        if filenames:
            logger.info(f"{status}的文件: {', '.join(filenames)}")
            cli.run_cmd(["git", "commit", "-m", f"{status}文件: {filenames}"])
        else:
            logger.warning(f"没有{status}的文件")
