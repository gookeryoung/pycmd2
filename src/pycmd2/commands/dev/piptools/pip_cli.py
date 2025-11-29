from __future__ import annotations

from typing import Dict
from typing import List

import typer

from pycmd2.client import get_client
from pycmd2.commands.core.runner import BaseRunner
from pycmd2.commands.dev.piptools.pip_download import PipDownloadRunner
from pycmd2.commands.dev.piptools.pip_freeze import PipFreezeRunner
from pycmd2.commands.dev.piptools.pip_install import PipInstallRunner
from pycmd2.commands.dev.piptools.pip_reinstall import PipReinstallRunner
from pycmd2.commands.dev.piptools.pip_uninstall import PipUninstallRunner

__version__ = "0.0.1"
__build_date__ = "2025-11-20"


cli = get_client()

_runners: Dict[str, BaseRunner] = {
    "download": PipDownloadRunner(),
    "freeze": PipFreezeRunner(),
    "install": PipInstallRunner(),
    "reinstall": PipReinstallRunner(),
    "uninstall": PipUninstallRunner(),
}

# 定义模块级别的默认参数
_libnames_default = typer.Argument(help="库名列表")


@cli.app.command("download", help="下载依赖, 别名: d")
@cli.app.command("d", help="下载依赖, 别名: download")
def pip_download(libname: str) -> None:
    """下载依赖."""
    _runners.get("download", BaseRunner()).run(libname=libname)


@cli.app.command("downloadreq", help="下载依赖[requirements], 别名: dr")
@cli.app.command("dr", help="下载依赖[requirements], 别名: downloadreq")
def pip_download_requirements() -> None:
    """下载依赖."""
    _runners.get("download", BaseRunner()).run(is_require=True)


@cli.app.command("freeze", help="冻结依赖, 别名: f")
@cli.app.command("f", help="冻结依赖, 别名: freeze")
def pip_freeze() -> None:
    """冻结依赖."""
    _runners.get("freeze", BaseRunner()).run()


@cli.app.command("install", help="安装依赖, 别名: i")
@cli.app.command("i", help="安装依赖, 别名: install")
def pip_install(
    libnames: List[str] = _libnames_default,
) -> None:
    """安装依赖."""
    _runners.get("install", BaseRunner()).run(libnames=libnames)


@cli.app.command("installoffline", help="安装依赖[离线], 别名: io")
@cli.app.command("io", help="安装依赖[离线], 别名: installoffline")
def pip_install_offline(
    libnames: List[str] = _libnames_default,
) -> None:
    """安装依赖, 离线."""
    _runners.get("install", BaseRunner()).run(
        libnames=libnames,
        options=["--no-index", "--find-links", "."],
    )


@cli.app.command("installreq", help="安装依赖[requirements], 别名: ir")
@cli.app.command("ir", help="安装依赖[requirements], 别名: installreq")
def pip_install_req() -> None:
    """安装依赖, 使用 requirements."""
    _runners.get("install", BaseRunner()).run(
        libnames=[],
        options=["-r", "requirements.txt"],
    )


@cli.app.command("reinstall", help="重新安装依赖, 别名: r")
@cli.app.command("r", help="重新安装依赖, 别名: reinstall")
def pip_reinstall(libnames: List[str] = _libnames_default) -> None:
    """重新安装依赖."""
    _runners.get("reinstall", BaseRunner()).run(libnames=libnames)


@cli.app.command("uninstall", help="卸载依赖, 别名: u")
@cli.app.command("u", help="卸载依赖, 别名: uninstall")
def pip_uninstall(libnames: List[str] = _libnames_default) -> None:
    """卸载依赖."""
    _runners.get("uninstall", BaseRunner()).run(libnames=libnames)


@cli.app.command("uninstallreq", help="卸载依赖, 使用 requirements, 别名: ur")
@cli.app.command("ur", help="卸载依赖, 使用 requirements, 别名: uninstallreq")
def pip_uninstall_req() -> None:
    """卸载依赖."""
    _runners.get("uninstall", BaseRunner()).run(
        libnames=[],
        options=["-r", "requirements.txt"],
    )
