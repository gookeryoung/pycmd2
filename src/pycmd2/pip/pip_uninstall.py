"""功能：卸载库"""

from pathlib import Path
from typing import List

from typer import Argument

from pycmd2.common.cli import run_cmd
from pycmd2.common.cli import setup_client

cli = setup_client()


def pip_uninstall(libname: str) -> None:
    run_cmd(["pip", "uninstall", libname, "-y"])


@cli.app.command()
def main(
    libnames: List[Path] = Argument(help="待下载库清单"),  # noqa: B008
):
    cli.run(pip_uninstall, libnames)
