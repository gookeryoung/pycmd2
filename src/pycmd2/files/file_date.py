"""
功能: 移除文件日期, 用创建日期替代.
命令: filedate.exe [TARGETS ...]
特性:
 - 日期格式为: YYYYMMDD
 - 文件分隔符包含: -_#.~
"""

import re
import time
from pathlib import Path
from typing import List
from typing import Tuple

from typer import Argument
from typing_extensions import Annotated

from pycmd2.common.cli import get_client
from pycmd2.common.settings import get_settings

cli = get_client()

settings = get_settings(
    "file_date",
    default_config=dict(
        # 检测分隔符
        detect_seperators="-_#.~",
        # 处理后使用分隔符
        seperator="_",
    ),
)


def remove_date_prefix(
    filename: str,
) -> str:
    """移除形式如 `YYYYMMDD` 的日期格式.

    Args:
        filename (str): 原始文件名

    Returns:
        移除日期后文件名

    >>> remove_date_prefix('20211211_hello.txt')
    'hello.txt'
    >>> remove_date_prefix('20191112-my-file.xls')
    'my-file.xls'
    >>> remove_date_prefix('20201211my-file.xls')
    'my-file.xls'
    >>> remove_date_prefix('2022-my-file.xls')
    '2022-my-file.xls'
    """
    separators = settings.get("detect_seperators", "-_#.~")
    pattern = re.compile(
        r"(20|19)\d{2}((0[1-9])|(1[012]))((0[1-9])|([12]\d)|(3[01]))"
    )
    match = re.search(pattern, filename)

    if not match:
        return filename

    b, e = match.start(), match.end()
    if b >= 1 and filename[b - 1] in separators:
        filename = filename.replace(filename[b - 1 : e], "")
    elif e + 1 <= len(filename) - 1 and filename[e] in separators:
        filename = filename.replace(filename[b : e + 1], "")
    else:
        filename = filename.replace(filename[b:e], "")
    return remove_date_prefix(filename)


def rename_target(
    filepath: Path,
) -> Tuple[str, str]:
    """更新日期标识, 如果没有则创建, 按照 YYYYMMDD 格式

    Args:
        filepath: 文件路径

    Returns:
        修改后的路径
    """
    seperator = settings.get("seperator", "_")
    modified, created = filepath.stat().st_mtime, filepath.stat().st_ctime
    time_mark = time.strftime(
        "%Y%m%d", time.localtime(max((modified, created)))
    )
    dst_name = filepath.with_name(
        f"{time_mark}{seperator}{remove_date_prefix(filepath.name)}"
    )
    filepath.rename(dst_name)
    return filepath.name, dst_name.name


@cli.app.command()
def main(
    targets: Annotated[List[Path], Argument(help="输入文件清单")],
):
    cli.run(rename_target, targets)
