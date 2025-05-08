"""功能：pip 下载库到本地 packages 文件夹"""

from pathlib import Path
from typing import List

from typer import Argument

from pycmd2.common.cli import run_cmd
from pycmd2.common.cli import run_parallel
from pycmd2.common.cli import setup_client
from pycmd2.common.consts import TRUSTED_PIP_URL

cli = setup_client()

cwd = Path.cwd()
dest_dir = cwd / "packages"


def run(libname: str) -> None:
    run_cmd(["pip", "download", libname, "-d", str(dest_dir), *TRUSTED_PIP_URL])


@cli.app.command()
def main(
    libnames: List[Path] = Argument(help="待下载库清单"),  # noqa: B008
):
    run_parallel(run, libnames)
