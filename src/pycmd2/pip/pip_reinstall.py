"""功能: 重新安装库."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typer import Argument
from typing_extensions import Annotated

from pycmd2.common.cli import get_client
from pycmd2.pip.conf import conf
from pycmd2.pip.pip_uninstall import pip_uninstall

if TYPE_CHECKING:
    from pathlib import Path

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
    libnames: Annotated[list[Path], Argument(help="待下载库清单")],
) -> None:
    cli.run(pip_reinstall, libnames)
