"""功能：pip 下载库到本地 packages 文件夹"""

from pathlib import Path
from typing import List

from typer import Argument

from pycmd2.common.cli import get_client
from pycmd2.pip.conf import settings

cli = get_client()


def pip_download(libname: str) -> None:
    cli.run_cmd(
        [
            "pip",
            "download",
            libname,
            "-d",
            settings.get("dest_dir"),
            *settings.get("trusted_pip_url"),
        ]
    )


@cli.app.command()
def main(
    libnames: List[Path] = Argument(help="待下载库清单"),  # noqa: B008
):
    cli.run(pip_download, libnames)
