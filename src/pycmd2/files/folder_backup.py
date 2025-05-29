"""
功能: 将其压缩成 zip 文件存储在指定的目标文件夹中
命令: folderback.exe [DIRECTORY] --dest [DESTINATION] --max [MAX_FILE_COUNT]
"""

import logging
import pathlib
import time
import zipfile
from pathlib import Path

from typer import Argument
from typer import Option
from typing_extensions import Annotated

from pycmd2.common.cli import get_client

cli = get_client()


def remove_dump(src: pathlib.Path, dst: pathlib.Path, max_zip: int) -> None:
    """删除超过 max_zip 个的备份."""

    zip_paths = [
        filepath for filepath in dst.rglob("*.zip") if src.stem in str(filepath)
    ]
    zip_files = sorted(zip_paths, key=lambda fn: str(fn)[-19:-4])
    if len(zip_files) > max_zip:
        print(f"remove oldest zip file: [{zip_files[0]}].")
        zip_files[0].unlink()
        remove_dump(src, dst, max_zip)


def zip_folder(
    src: pathlib.Path,
    dst: pathlib.Path,
    max_zip: int,
) -> None:
    """备份源文件夹 src 到目标文件夹 dst, 并删除超过 max_zip 个的备份."""

    entries = list(e for e in src.iterdir() if e.stem != dst.stem)
    timestamp = time.strftime("_%Y%m%d_%H%M%S")
    target_path = dst / (src.stem + timestamp + ".zip")
    zip_file = zipfile.ZipFile(target_path, "w")

    logging.info(f"压缩文件夹 [{src}] —> [{dst}]...")
    for file in entries:
        zip_file.write(
            str(file), arcname=str(file).replace(str(src.parent), "")
        )
    remove_dump(src, dst, max_zip)


@cli.app.command()
def main(
    directory: Annotated[Path, Argument(help="备份目录, 默认当前")] = Path("."),
    dest: Annotated[Path, Option(help="目标文件夹")] = (
        Path(".").parent / "_backup"
    ),
    max: Annotated[int, Option(help="最大备份数量")] = 5,
):
    if not dest.exists():
        print(f"创建备份目标文件夹: {dest}")
        dest.mkdir(parents=True, exist_ok=True)

    zip_folder(directory, dest, max)
