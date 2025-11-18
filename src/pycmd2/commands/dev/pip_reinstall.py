"""功能: 重新安装库."""

from __future__ import annotations

from pathlib import Path
from typing import List

import typer

from pycmd2.client import get_client
from pycmd2.commands.dev.pip_download import conf
from pycmd2.commands.dev.pip_uninstall import pip_uninstall

cli = get_client()


def pip_reinstall(libname: str) -> None:
    pip_uninstall(libname)
    cli.run_cmd(
        [
            "pip",
            "install",
            libname,
            *conf.TRUSTED_PIP_URL,
        ],
    )


@cli.app.command()
def main(
    libnames: List[Path] = typer.Argument(help="待下载库清单"),  # noqa: B008
) -> None:
    cli.run(pip_reinstall, libnames)
