"""功能: 初始化 python 环境变量."""

from __future__ import annotations

import logging

from pycmd2.client import get_client

from .base import BaseEnvTool

cli = get_client()
logger = logging.getLogger(__name__)


NODE_VERSIONS: dict[str, str] = {
    "V20": "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -",
    "V18": "curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -",
}


def install_nodejs(node_ver: str) -> None:
    cli.run_cmdstr(NODE_VERSIONS.get(node_ver, ""))


class JavaScriptEnvTool(BaseEnvTool):
    """JavaScript 环境配置工具."""

    def _install_nodejs(self, node_ver: str) -> None:
        cli.run_cmdstr(NODE_VERSIONS.get(node_ver, ""))

    def run(self, version: str = "V18") -> None:
        """安装 nodejs."""
        if cli.is_windows:
            logger.error("当前系统为windows, 请下载压缩包直接安装")
            return

        install_nodejs(version)
