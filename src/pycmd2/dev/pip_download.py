"""功能: pip 下载库到本地 packages 文件夹."""

from __future__ import annotations

from typing import List

import typer

from pycmd2.client import get_client
from pycmd2.dev.conf import conf

cli = get_client()
StrList = List[str]


def pip_download(libname: str) -> None:
    dest_dir = cli.cwd / "packages"

    cli.run_cmd(
        [
            "pip",
            "download",
            libname,
            "-d",
            str(dest_dir),
            *conf.TRUSTED_PIP_URL,
        ],
    )


@cli.app.command()
def main(
    libname: List[str] = typer.Argument(help="待下载库清单"),  # noqa: B008
) -> None:
    cli.run(pip_download, libname)
