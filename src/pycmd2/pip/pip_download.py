"""功能: pip 下载库到本地 packages 文件夹."""

from pathlib import Path
from typing import List

from typer import Argument
from typing_extensions import Annotated

from pycmd2.common.cli import get_client
from pycmd2.pip.conf import conf

cli = get_client()


def pip_download(libname: str) -> None:
    dest_dir = cli.CWD / "packages"

    cli.run_cmd(
        [
            "pip",
            "download",
            libname,
            "-d",
            str(dest_dir),
            *conf.TRUSTED_PIP_URL,
        ],
    )


@cli.app.command()
def main(
    libnames: Annotated[List[Path], Argument(help="待下载库清单")],
):
    cli.run(pip_download, libnames)
