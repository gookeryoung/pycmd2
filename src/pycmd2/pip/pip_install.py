"""功能：pip 安装库到本地"""

from pathlib import Path
from typing import List
from typing import Optional

from typer import Argument

from pycmd2.common.cli import run_cmd
from pycmd2.common.cli import setup_client
from pycmd2.common.consts import TRUSTED_PIP_URL

cli = setup_client()


def pip_install(libname: str, options: Optional[List[str]] = None) -> None:
    run_opt = options or []
    run_cmd(["pip", "install", libname, *TRUSTED_PIP_URL, *run_opt])


@cli.app.command()
def main(
    libnames: List[Path] = Argument(help="待下载库清单"),  # noqa: B008
):
    cli.run(pip_install, libnames)
