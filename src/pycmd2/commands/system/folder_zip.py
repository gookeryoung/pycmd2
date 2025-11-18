"""功能: 压缩目录下的所有文件/文件夹, 默认为当前目录.

命令: folderzip [DIRECTORY]
"""

import logging
import os
import shutil
from pathlib import Path

from typer import Argument
from typer import Option
from typing_extensions import Annotated

from pycmd2.client import get_client

cli = get_client(help_doc="目录压缩工具.")
logger = logging.getLogger(__name__)


def is_valid_entry(entry: Path) -> bool:
    """检查文件夹是否有效, 忽略已压缩的目录.

    Args:
        entry (Path): 目录

    Returns:
        bool: 是否有效
    """
    if not entry.is_dir():
        return False

    if entry.with_suffix(".zip").exists():
        logger.info(f"跳过已压缩目录: [red]{entry.name}")
        return False

    return True


def zip_folder(entry: Path) -> None:
    logger.info(
        f"压缩目录: [green]{entry.name} -> {entry.with_suffix('.zip').name}",
    )
    os.chdir(entry.parent)  # 切换到父目录, 以便正确创建 zip 文件
    shutil.make_archive(str(entry), "zip", base_dir=entry.name)


@cli.app.command()
def main(
    directory: Annotated[
        Path,
        Argument(help="待备份目录, 默认为当前目录"),
    ] = cli.cwd,
    ignore: Annotated[str, Option(help="忽略以此开头的目录或文件名")] = "._",
) -> None:
    ignores = list(ignore) or []
    dirs = [d for d in directory.iterdir() if is_valid_entry(d) and all(not d.name.startswith(ig) for ig in ignores)]

    if dirs:
        cli.run(zip_folder, dirs)
    else:
        logger.info("没有待处理的目录.")
