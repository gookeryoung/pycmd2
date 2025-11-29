"""功能: 重新安装库."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from typing import List

from pycmd2.client import get_client
from pycmd2.commands.dev.piptools.pip_install import pip_install
from pycmd2.commands.dev.piptools.pip_uninstall import pip_uninstall
from pycmd2.commands.runner import BaseRunner


class PipReinstallRunner(BaseRunner):
    """功能: 重新安装库."""

    DESCRIPTION = "重新安装库"

    def run(self, libnames: List[Path], *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """运行命令."""
        super().run(*args, **kwargs)

        cli = get_client()
        cli.run(pip_uninstall, libnames)
        cli.run(pip_install, libnames)
