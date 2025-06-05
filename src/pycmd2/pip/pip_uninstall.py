"""功能: 卸载库."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typer import Argument

from pycmd2.common.cli import get_client

if TYPE_CHECKING:
    from pathlib import Path

cli = get_client()


def pip_uninstall(libname: str) -> None:
    cli.run_cmd(["pip", "uninstall", libname, "-y"])


@cli.app.command()
def main(
    libnames: list[Path] = Argument(help="待下载库清单"),  # noqa: B008
) -> None:
    cli.run(pip_uninstall, libnames)
