"""功能: 初始化 git 目录.

命令: gitinit
"""

from __future__ import annotations

import logging
import os
import pathlib
from typing import Any
from typing import ClassVar

from pycmd2.client import get_client
from pycmd2.commands.core.runner import BaseRunner

logger = logging.getLogger(__name__)


class GitInitRunner(BaseRunner):
    """GitInitRunner 类."""

    DESCRIPTION: str = "初始化 git 目录"
    SUBCOMMANDS: ClassVar = [
        ["git", "init"],
        ["git", "add", "."],
        ["git", "commit", "-m", "initial commit"],
    ]

    def run(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """执行git初始化命令, 确保在正确的目录中运行."""
        cli = get_client()
        original_cwd = pathlib.Path.cwd()

        logger.info("GitInitRunner 运行")
        os.chdir(str(cli.cwd))

        try:
            super().run(*args, **kwargs)
        finally:
            logger.info(f"恢复到目录: {original_cwd}")
            os.chdir(original_cwd)
