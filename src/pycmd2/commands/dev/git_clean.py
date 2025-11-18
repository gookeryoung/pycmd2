"""功能: 清理git.

命令: gitc --force/-f
"""

import logging

from typer import Option
from typing_extensions import Annotated

from pycmd2.client import get_client
from pycmd2.commands.dev.git_push_all import check_git_status

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


@cli.app.command()
def main(
    *,
    force: Annotated[bool, Option("--force", "-f", help="强制清理")] = False,
) -> None:
    logger.info(f"gitc {__version__}, 构建日期: {__build_date__}")

    if force:
        logger.warning("强制清理模式, 会删除未提交的修改和新文件")

    if not force and not check_git_status():
        return

    clean_cmd = ["git", "clean", "-xfd"]
    for exclude_dir in exclude_dirs:
        clean_cmd.extend(["-e", exclude_dir])

    cli.run_cmd(clean_cmd)
    cli.run_cmd(["git", "checkout", "."])
