"""功能: 卸载库."""

from __future__ import annotations

from pathlib import Path
from typing import List

import typer

from pycmd2.client import get_client

cli = get_client()


def pip_uninstall(libname: str) -> None:
    cli.run_cmd(["pip", "uninstall", libname, "-y"])


@cli.app.command()
def main(
    libnames: List[Path] = typer.Argument(help="待下载库清单"),  # noqa: B008
) -> None:
    cli.run(pip_uninstall, libnames)
