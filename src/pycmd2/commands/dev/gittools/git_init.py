"""功能: 初始化 git 目录.

命令: gitinit
"""

from __future__ import annotations

import logging
import os
import pathlib
from typing import ClassVar

from pycmd2.client import get_client
from pycmd2.commands.runner import BaseRunner

logger = logging.getLogger(__name__)


class GitInitRunner(BaseRunner):
    """GitInitRunner 类."""

    DESCRIPTION: str = "初始化 git 目录"
    SUBCOMMANDS: ClassVar = [
        ["git", "init"],
        ["git", "add", "."],
        ["git", "commit", "-m", "initial commit"],
    ]

    def run(self) -> None:
        """执行git初始化命令, 确保在正确的目录中运行."""
        if self.DESCRIPTION:
            logger.info(f"功能描述: [green b]{self.DESCRIPTION}")

        # 获取当前cli对象并切换到其工作目录
        cli = get_client()
        original_cwd = pathlib.Path.cwd()

        try:
            # 切换到cli的工作目录
            logger.info(f"切换到目录: {cli.cwd}")
            os.chdir(str(cli.cwd))

            # 执行子命令
            for subcommand in self.SUBCOMMANDS:
                if isinstance(subcommand, list):
                    logger.info(f"执行命令: {' '.join(subcommand)}")
                    cli.run_cmd(list(subcommand))

        finally:
            # 确保恢复原始工作目录
            os.chdir(original_cwd)
            logger.info(f"恢复到目录: {original_cwd}")
