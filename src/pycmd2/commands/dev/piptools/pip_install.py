"""功能: pip 安装库到本地."""

from __future__ import annotations

from functools import partial
from typing import Any
from typing import List
from typing import Optional

from pycmd2.client import get_client
from pycmd2.commands.core.runner import BaseRunner
from pycmd2.commands.dev.piptools.pip_download import conf

cli = get_client()


def pip_install(libname: str = "", options: Optional[List[str]] = None) -> None:
    run_opt = options or []

    if libname:
        run_opt.append(libname)

    cli.run_cmd(
        [
            "pip",
            "install",
            *conf.TRUSTED_PIP_URL,
            *run_opt,
        ],
    )


class PipInstallRunner(BaseRunner):
    """功能: pip 安装库到本地."""

    DESCRIPTION = "pip 安装库到本地"

    def run(
        self,
        libnames: Optional[List[str]] = None,
        options: Optional[List[str]] = None,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """运行命令."""
        super().run(*args, **kwargs)

        if libnames is None:
            libnames = []

        pip_install_options = partial(pip_install, options=options)
        cli.run(pip_install_options, libnames)
