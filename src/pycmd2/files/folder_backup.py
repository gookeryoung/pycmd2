"""
功能: 将其压缩成 zip 文件存储在指定的目标文件夹中
命令: folderback.exe [DIRECTORY] --dest [DESTINATION] --max [MAX_FILE_COUNT]
"""

import os
import pathlib
import shutil
import time
from pathlib import Path

from typer import Argument
from typer import Option
from typing_extensions import Annotated

from pycmd2.common.cli import get_client

cli = get_client()


def zip_folder(
    src: pathlib.Path,
    dst: pathlib.Path,
    max_zip: int,
) -> None:
    """备份源文件夹 src 到目标文件夹 dst, 并删除超过 max_zip 个的备份."""

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    zip_files = sorted(list(dst.rglob("*.zip")), key=lambda fn: str(fn.name))
    if len(zip_files) >= max_zip:
        cli.run(os.remove, zip_files[: len(zip_files) - max_zip + 1])

    shutil.make_archive(str(dst / f"{timestamp}_{src.name}"), "zip")


@cli.app.command()
def main(
    directory: Annotated[Path, Argument(help="备份目录, 默认当前")] = cli.CWD,
    dest: Annotated[Path, Option(help="目标文件夹")] = (
        cli.CWD.parent / f"_backup_{cli.CWD.name}"
    ),
    max: Annotated[int, Option(help="最大备份数量")] = 5,
):
    if not dest.exists():
        print(f"创建备份目标文件夹: {dest}")
        dest.mkdir(parents=True, exist_ok=True)

    zip_folder(directory, dest, max)
