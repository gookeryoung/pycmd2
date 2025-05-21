"""功能：pip 安装库到本地"""

from typing import List
from typing import Optional

from typer import Argument
from typing_extensions import Annotated

from pycmd2.common.cli import get_client
from pycmd2.pip.consts import TRUSTED_PIP_URL

cli = get_client()


def pip_install(libname: str, options: Optional[List[str]] = None) -> None:
    run_opt = options or []
    cli.run_cmd(["pip", "install", libname, *TRUSTED_PIP_URL, *run_opt])


@cli.app.command()
def main(
    libnames: Annotated[List[str], Argument(help="库名列表")],
):
    cli.run(pip_install, libnames)
