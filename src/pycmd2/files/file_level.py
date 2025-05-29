"""
功能: 重命名文件级别后缀
用法: filelevel.exe -f FILES [FILES ...] -l level
特性:
 - 重命名格式为 '(PUB)'
"""

import typing
from functools import partial
from pathlib import Path
from typing import List

from typer import Argument
from typing_extensions import Annotated

from pycmd2.common.cli import get_client
from pycmd2.common.settings import get_settings

cli = get_client()
settings = get_settings(
    "file_level",
    default_config={
        # 文件级别
        "levels": {
            "0": "",
            "1": "PUB,NOR",
            "2": "INT",
            "3": "CON",
            "4": "CLA",
        },
        # 分隔符
        "brackets": [" ([_（【-", " )]_）】"],
    },
)


# 文件级别定义
class FileLevel(typing.NamedTuple):
    code: int
    names: typing.Tuple[str, ...]


levels = [
    FileLevel(int(c), n.split(","))
    for c, n in settings.get("levels", None).items()
]
bracket_pairs = settings.get("brackets", (" (（[【_-", " )）]】_"))


def remove_marks(
    filename: str,
    marks: typing.Tuple[str, ...],
) -> str:
    for mark in marks:
        pos = filename.find(mark)
        if pos != -1:
            b, e = pos - 1, pos + len(mark)
            if b >= 0 and e <= len(filename) - 1:
                if (
                    filename[b] not in bracket_pairs[0]
                    or filename[e] not in bracket_pairs[1]
                ):
                    return filename[:e] + remove_marks(filename[e:], marks)
                filename = filename.replace(filename[b : e + 1], "")
                return remove_marks(filename, marks)
    return filename


def remove_level_and_digital_mark(
    filename: str,
) -> str:
    for file_level in levels[1:]:
        filename = remove_marks(filename, file_level.names)
    filename = remove_marks(
        filename, tuple("".join([str(x) for x in range(1, 10)]))
    )
    return filename


def add_level_mark(
    filepath: Path,
    filelevel: int,
    suffix: int,
) -> Path:
    cleared_stem = remove_level_and_digital_mark(filepath.stem)
    dst_stem = (
        f"{cleared_stem}({levels[filelevel].names[0]})"
        if filelevel
        else cleared_stem
    )  # noqa

    if dst_stem == filepath.stem:
        print(f"destination stem [{dst_stem}] equals to current.")
        return filepath
    dst_name = (
        f"{dst_stem}({suffix}){filepath.suffix}"
        if suffix
        else f"{dst_stem}{filepath.suffix}"
    )

    if filepath.with_name(dst_name).exists():
        return add_level_mark(filepath, filelevel, suffix + 1)
    print(f"rename [{filepath.name}] to [{dst_name}].")
    return filepath.with_name(dst_name)


def rename(
    target: Path,
    level: int,
) -> None:
    target.rename(add_level_mark(target, level, 0))


@cli.app.command()
def main(
    targets: Annotated[List[Path], Argument(help="目标文件或目录")],
    level: Annotated[int, Argument(help="文件级别")] = 0,
):
    rename_func = partial(rename, level=level)
    cli.run(rename_func, targets)
