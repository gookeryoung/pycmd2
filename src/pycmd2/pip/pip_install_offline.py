"""功能：pip 安装库到本地"""

from functools import partial
from typing import List

from typer import Argument
from typing_extensions import Annotated

from pycmd2.common.cli import get_client
from pycmd2.pip.pip_install import pip_install

cli = get_client()


@cli.app.command()
def main(
    libnames: Annotated[List[str], Argument(help="待下载库清单")],
):
    run_pip_install_offline = partial(
        pip_install, options=["--no-index", "--find-links", "."]
    )
    cli.run(run_pip_install_offline, libnames)
