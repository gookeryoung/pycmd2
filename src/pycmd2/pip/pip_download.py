"""功能：pip 下载库到本地 packages 文件夹"""

from pathlib import Path
from typing import List

from typer import Argument

from pycmd2.common.cli import get_client
from pycmd2.pip.consts import TRUSTED_PIP_URL

cli = get_client()
dest_dir = cli.CWD / "packages"


def pip_download(libname: str) -> None:
    cli.run_cmd([
        "pip",
        "download",
        libname,
        "-d",
        str(dest_dir),
        *TRUSTED_PIP_URL,
    ])


@cli.app.command()
def main(
    libnames: List[Path] = Argument(help="待下载库清单"),  # noqa: B008
):
    cli.run(pip_download, libnames)
