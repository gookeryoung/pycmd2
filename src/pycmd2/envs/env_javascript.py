"""功能：初始化 python 环境变量"""

import logging
from typing import Dict

from typer import Argument
from typing_extensions import Annotated

from pycmd2.common.cli import get_client

cli = get_client()


NODE_VERSIONS: Dict[str, str] = dict(
    V20="curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -",
    V18="curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -",
)


def install_nodejs(node_ver: str) -> None:
    cli.run_cmdstr(NODE_VERSIONS.get(node_ver, ""))


@cli.app.command()
def main(
    node_ver: Annotated[
        str, Argument(help=f"nodejs 版本: {NODE_VERSIONS.keys()}")
    ] = "V18",
):
    if cli.IS_WINDOWS:
        logging.error("当前系统为windows, 请下载压缩包直接安装")
        return

    install_nodejs(node_ver)
