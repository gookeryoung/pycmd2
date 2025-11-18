"""功能: 压缩为 zip 文件存储在指定文件夹.

命令: folderback [DIR] --dest [DEST] --max [N]
"""

import logging
import os
import pathlib
import shutil
import time
from pathlib import Path

from typer import Argument
from typer import Option
from typing_extensions import Annotated

from pycmd2.client import get_client

cli = get_client()
logger = logging.getLogger(__name__)


def zip_folder(
    src: pathlib.Path,
    dst: pathlib.Path,
    max_zip: int,
) -> None:
    """备份源文件夹 src 到目标文件夹 dst, 并删除超过 max_zip 个的备份."""
    logger.info(f"备份文件夹: {src} 到 {dst} 目录")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    zip_files = sorted(dst.glob("*.zip"), key=lambda fn: str(fn.name))
    if len(zip_files) >= max_zip:
        remove_files = zip_files[: len(zip_files) - max_zip + 1]
        logger.info(
            f"超过最大备份数量 {max_zip}, 删除旧备份: {[f.name for f in remove_files]}",
        )
        cli.run(os.remove, remove_files)

    backup_path = dst / f"{timestamp}_{src.name}"
    logger.info(f"创建备份: [purple]{backup_path.name}")
    shutil.make_archive(str(backup_path), "zip")


@cli.app.command()
def main(
    directory: Annotated[Path, Argument(help="备份目录, 默认当前")] = cli.cwd,
    dest: Annotated[Path, Option(help="目标文件夹")] = (cli.cwd.parent / f"_backup_{cli.cwd.name}"),
    max_count: Annotated[int, Option(help="最大备份数量")] = 5,
    *,
    clean: Annotated[bool, Option("--clean", help="清理已有备份")] = False,
    ls: Annotated[bool, Option("--list", help="列出备份文件")] = False,
) -> None:
    backup_files = list(dest.glob("*.zip"))
    if ls:
        if not backup_files:
            logger.info(f"没有找到备份文件: {dest}")
        else:
            logger.info(f"备份文件列表: {[f.name for f in backup_files]}")
        return

    if clean:
        logger.info(f"清理已有备份: [purple]{backup_files}")
        cli.run(os.remove, backup_files)
        return

    if not dest.exists():
        logger.info(f"创建备份目标文件夹: {dest}")
        dest.mkdir(parents=True, exist_ok=True)

    zip_folder(directory, dest, max_count)
