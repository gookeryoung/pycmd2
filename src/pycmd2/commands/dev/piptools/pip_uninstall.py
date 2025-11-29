"""功能: 卸载库."""

from __future__ import annotations

from functools import partial
from typing import Any
from typing import List
from typing import Optional

from pycmd2.client import get_client
from pycmd2.commands.core.runner import BaseRunner

cli = get_client()


def pip_uninstall(libname: str = "", options: Optional[List[str]] = None) -> None:
    run_opt = options or []
    if libname:
        run_opt.append(libname)

    cli.run_cmd(["pip", "uninstall", "-y", *run_opt])


class PipUninstallRunner(BaseRunner):
    """PipUninstallRunner."""

    DESCRIPTION = "pip 批量卸载库"

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

        pip_uninstall_options = partial(pip_uninstall, options=options)
        cli.run(pip_uninstall_options, libnames)
