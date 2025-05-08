"""功能：pip 安装库到本地"""

from functools import partial
from pathlib import Path
from typing import List

from typer import Argument

from pycmd2.common.cli import run_parallel
from pycmd2.common.cli import setup_client
from pycmd2.pip.pip_install import run_pip_install

cli = setup_client()


@cli.app.command()
def main(
    libnames: List[Path] = Argument(help="待下载库清单"),  # noqa: B008
):
    run_pip_install_offline = partial(run_pip_install, options=["--no-index", "--find-links", "."])
    run_parallel(run_pip_install_offline, libnames)
