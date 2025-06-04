"""功能: pip 安装库到本地."""

from __future__ import annotations

from typer import Argument
from typing_extensions import Annotated

from pycmd2.common.cli import get_client
from pycmd2.pip.conf import conf

cli = get_client()


def pip_install(libname: str, options: list[str] | None = None) -> None:
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
    libnames: Annotated[list[str], Argument(help="库名列表")],
) -> None:
    cli.run(pip_install, libnames)
