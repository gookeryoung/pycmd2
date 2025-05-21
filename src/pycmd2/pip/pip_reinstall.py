"""功能：重新安装库"""

from pathlib import Path
from typing import List

from typer import Argument

from pycmd2.common.cli import get_client
from pycmd2.pip.consts import TRUSTED_PIP_URL
from pycmd2.pip.pip_uninstall import pip_uninstall

cli = get_client()


def pip_reinstall(libname: str) -> None:
    pip_uninstall(libname)
    cli.run_cmd(["pip", "install", libname, *TRUSTED_PIP_URL])


@cli.app.command()
def main(
    libnames: List[Path] = Argument(help="待下载库清单"),  # noqa: B008
):
    cli.run(pip_reinstall, libnames)
