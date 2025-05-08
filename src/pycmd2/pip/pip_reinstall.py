"""功能：重新安装库到本地"""

from pathlib import Path
from typing import List

from typer import Argument

from pycmd2.common.cli import run_parallel
from pycmd2.common.cli import setup_client
from pycmd2.common.consts import TRUSTED_PIP_URL
from pycmd2.common.logger import run_cmd

cli = setup_client()


def run_pip_reinstall(libname: str) -> None:
    run_cmd(["pip", "uninstall", libname, "-y"])
    run_cmd(["pip", "install", libname, *TRUSTED_PIP_URL])


@cli.app.command()
def main(
    lib_names: List[Path] = Argument(help="待下载库清单"),  # noqa: B008
):
    run_parallel(run_pip_reinstall, lib_names)
