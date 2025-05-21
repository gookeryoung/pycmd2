"""
功能：清理git
命令: gitc --force/-f
"""

import logging

from typer import Option
from typing_extensions import Annotated

from pycmd2.common.cli import get_client
from pycmd2.git.git_push_all import check_git_status

cli = get_client()

# 排除目录
exclude_dirs = [
    ".venv",
]


@cli.app.command()
def main(
    force: Annotated[bool, Option("--force", "-f", help="强制清理")] = False,
) -> None:
    if force:
        logging.warning("强制清理模式, 会删除未提交的修改和新文件")

    if not force and not check_git_status():
        return

    clean_cmd = ["git", "clean", "-xfd"]
    for exclude_dir in exclude_dirs:
        clean_cmd.extend(["-e", exclude_dir])

    cli.run_cmd(clean_cmd)
    cli.run_cmd(["git", "checkout", "."])
