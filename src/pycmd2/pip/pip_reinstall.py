"""功能：重新安装库"""

from pathlib import Path
from typing import List

from typer import Argument

from pycmd2.common.cli import run_cmd
from pycmd2.common.cli import run_parallel
from pycmd2.common.cli import setup_client
from pycmd2.common.consts import TRUSTED_PIP_URL
from pycmd2.pip.pip_uninstall import pip_uninstall

cli = setup_client()


def pip_reinstall(libname: str) -> None:
    pip_uninstall(libname)
    run_cmd(["pip", "install", libname, *TRUSTED_PIP_URL])


@cli.app.command()
def main(
    libnames: List[Path] = Argument(help="待下载库清单"),  # noqa: B008
):
    run_parallel(pip_reinstall, libnames)
