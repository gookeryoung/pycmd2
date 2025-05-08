"""功能：下载 pip 库到本地 packages 文件夹"""

from pathlib import Path
from typing import List

from typer import Argument

from pycmd2.common.cli import run_parallel
from pycmd2.common.cli import setup_client
from pycmd2.common.logger import run_cmd

cli = setup_client()

cwd = Path.cwd()
dest_dir = cwd / "packages"


def run(libname: str) -> None:
    run_cmd([
        "pip",
        "download",
        libname,
        "-d",
        str(dest_dir),
    ])


@cli.app.command()
def main(
    lib_names: List[Path] = Argument(help="输入库清单"),  # noqa: B008
):
    run_parallel(run, lib_names)
