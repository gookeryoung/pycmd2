"""功能: pip 下载库到本地 packages 文件夹."""

from __future__ import annotations

from typing import ClassVar
from typing import List

import typer

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin


class PipConfig(TomlConfigMixin):
    """Pip配置."""

    NAME = "pip"

    TRUSTED_PIP_URL: ClassVar[List[str]] = [
        "--trusted-host",
        "mirrors.aliyun.com",
        "-i",
        "http://mirrors.aliyun.com/pypi/simple/",
    ]


cli = get_client()
conf = PipConfig()


def pip_download(libname: str) -> None:
    dest_dir = cli.cwd / "packages"

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
    libname: List[str] = typer.Argument(help="待下载库清单"),  # noqa: B008
) -> None:
    cli.run(pip_download, libname)
