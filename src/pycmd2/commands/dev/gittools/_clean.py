"""功能: 清理git.

命令: gitc --force/-f
"""

import logging
from typing import ClassVar

from pycmd2.client import get_client
from pycmd2.commands.dev.gittools.git_push_all import _check_git_status
from pycmd2.commands.runner import BaseRunner

__version__ = "0.1.1"
__build_date__ = "2025-07-30"

cli = get_client()
logger = logging.getLogger(__name__)

# 排除目录
exclude_dirs = [
    ".venv",
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
]


def _clean(*, force: bool = False) -> None:
    logger.info(f"gitc {__version__}, 构建日期: {__build_date__}")

    if force:
        logger.warning("强制清理模式, 会删除未提交的修改和新文件")

    if not force and not _check_git_status():
        return

    clean_cmd = ["git", "clean", "-xfd"]
    for exclude_dir in exclude_dirs:
        clean_cmd.extend(["-e", exclude_dir])

    cli.run_cmd(clean_cmd)
    cli.run_cmd(["git", "checkout", "."])


class GitCleanRunner(BaseRunner):
    """GitCleanRunner 类."""

    DESCRIPTION = "清理git"
    SUBCOMMANDS: ClassVar = [lambda _: _clean(force=False)]


class GitCleanForceRunner(BaseRunner):
    """GitCleanForceRunner 类."""

    DESCRIPTION = "清理git, 强制模式"
    SUBCOMMANDS: ClassVar = [lambda _: _clean(force=True)]
