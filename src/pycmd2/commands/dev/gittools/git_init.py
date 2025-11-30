"""功能: 初始化 git 目录.

命令: gitinit
"""

from __future__ import annotations

import logging
import os
import pathlib
from pathlib import Path
from typing import ClassVar

from pycmd2.client import get_client
from pycmd2.commands.core.runner import SequenceSubcommandRunner

logger = logging.getLogger(__name__)


class GitInitRunner(SequenceSubcommandRunner):
    """GitInitRunner 类."""

    DESCRIPTION: str = "初始化 git 目录"
    SUBCOMMANDS: ClassVar = [
        ["git", "init"],
        ["git", "add", "."],
        ["git", "commit", "-m", "initial commit"],
    ]

    def __init__(self) -> None:
        super().__init__()

        self.original_cwd: Path | None = None

    def run_before(self) -> None:
        """执行前操作."""
        super().run_before()

        cli = get_client()
        self.original_cwd = pathlib.Path.cwd()

        logger.info("GitInitRunner 运行")
        os.chdir(str(cli.cwd))

    def run_after(self) -> None:
        """执行后操作."""
        super().run_after()

        if not self.original_cwd:
            logger.error("原始目录为空, 退出")
            return

        logger.info(f"恢复到目录: {self.original_cwd}")
        os.chdir(self.original_cwd)
