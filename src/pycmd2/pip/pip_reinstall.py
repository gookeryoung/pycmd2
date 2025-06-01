"""功能：重新安装库"""

from pathlib import Path
from typing import List

from typer import Argument

from pycmd2.common.cli import get_client
from pycmd2.pip.conf import settings
from pycmd2.pip.pip_uninstall import pip_uninstall

cli = get_client()


def pip_reinstall(libname: str) -> None:
    pip_uninstall(libname)
    cli.run_cmd(
        [
            "pip",
            "install",
            libname,
            *settings.get("trusted_pip_url"),
        ]
    )


@cli.app.command()
def main(
    libnames: List[Path] = Argument(help="待下载库清单"),  # noqa: B008
):
    cli.run(pip_reinstall, libnames)
