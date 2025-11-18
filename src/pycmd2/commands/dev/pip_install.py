"""功能: pip 安装库到本地."""

from __future__ import annotations

from typing import List

from typer import Argument

from pycmd2.client import get_client
from pycmd2.commands.dev.pip_download import conf

cli = get_client()
StrList = List[str]


def pip_install(libname: str, options: StrList | None = None) -> None:
    run_opt = options or []
    cli.run_cmd(
        [
            "pip",
            "install",
            libname,
            *conf.TRUSTED_PIP_URL,
            *run_opt,
        ],
    )


@cli.app.command()
def main(
    libnames: List[str] = Argument(help="库名列表"),  # noqa: B008
) -> None:
    cli.run(pip_install, libnames)
