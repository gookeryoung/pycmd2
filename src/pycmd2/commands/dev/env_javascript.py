"""功能: 初始化 python 环境变量."""

from __future__ import annotations

import logging

from typer import Argument

from pycmd2.client import get_client

cli = get_client()
logger = logging.getLogger(__name__)


NODE_VERSIONS: dict[str, str] = {
    "V20": "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -",
    "V18": "curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -",
}


def install_nodejs(node_ver: str) -> None:
    cli.run_cmdstr(NODE_VERSIONS.get(node_ver, ""))


@cli.app.command()
def main(
    version: str = Argument(default="V18", help=f"nodejs 版本: {NODE_VERSIONS.keys()}"),
) -> None:
    if cli.is_windows:
        logger.error("当前系统为windows, 请下载压缩包直接安装")
        return

    install_nodejs(version)
