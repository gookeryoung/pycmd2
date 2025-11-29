"""功能: pip 下载库到本地 packages 文件夹, 使用 requirements.txt.

命令: pipdr
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Tuple

from pycmd2.client import get_client
from pycmd2.commands.core.runner import BaseRunner
from pycmd2.commands.dev.piptools.pip_conf import conf


def pip_download(libname: str) -> None:
    """下载指定的Python库到本地packages目录.

    Args:
        libname: 要下载的库名称
    """
    cli = get_client()
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


def pip_download_req() -> None:
    cli = get_client()

    dest_dir = cli.cwd / "packages"
    cli.run_cmd(
        [
            "pip",
            "download",
            "-r",
            "requirements.txt",
            "-d",
            str(dest_dir),
            *conf.TRUSTED_PIP_URL,
        ],
    )


class PipDownloadRunner(BaseRunner):
    """pip 批量下载库到本地 packages 文件夹."""

    DESCRIPTION = "pip 批量下载库到本地 packages 文件夹"

    def run(
        self,
        libname: str = "",
        *args: Tuple[Any, ...],
        is_require: bool = False,
        **kwargs: Dict[str, Any],
    ) -> None:
        """运行命令."""
        super().run(*args, **kwargs)

        if is_require:
            pip_download_req()

        if libname:
            pip_download(libname)
