"""
功能：增加文件到 git 目录, 显示新增的文件清单
命令: gitadd
"""

import logging
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Set

from pycmd2.common.cli import get_client

cli = get_client()


@dataclass
class GitAddFileStatus:
    """Git文件状态数据类"""

    status: str
    filepath: Path

    def __hash__(self) -> int:
        """计算哈希值, 用于在集合中唯一标识"""
        return hash((self.status, str(self.filepath)))


def get_changed_files_info() -> Set[GitAddFileStatus]:
    """获取git状态变化的文件列表"""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
    )
    files: Set[GitAddFileStatus] = set()
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if line.strip():
                status = line[:2].strip()
                filename = line[3:].strip()
                files.add(GitAddFileStatus(status, Path(filename)))
    return files


@cli.app.command()
def main():
    os.chdir(str(cli.CWD))

    # 计算新增的文件
    before = get_changed_files_info()
    cli.run_cmd(["git", "add", "."])
    after = get_changed_files_info()

    # 计算新增的文件信息
    added_files_info = after - before
    added_filenames = {
        f.filepath.stem for f in added_files_info if f.status == "A"
    }
    modified_filenames = {
        f.filepath.stem for f in added_files_info if f.status == "M"
    }

    # 显示结果
    check_status = {
        "新增": added_filenames,
        "修改": modified_filenames,
    }
    for status, filenames in check_status.items():
        if filenames:
            logging.info(f"{status}的文件: {', '.join(filenames)}")
            cli.run_cmd(["git", "commit", "-m", f"{status}文件: {filenames}"])
        else:
            logging.warning(f"没有{status}的文件")
