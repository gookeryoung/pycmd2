from __future__ import annotations

import logging
from typing import ClassVar
from typing import Dict

import typer

from pycmd2.client import get_client
from pycmd2.commands.core.runner import StringCommandRunner
from pycmd2.config import TomlConfigMixin

from .base import BaseEnvTool
from .python import PythonEnvtool
from .rust import RustEnvTool


class EnvToolConfig(TomlConfigMixin):
    """环境配置工具配置."""

    NODE_VERSIONS: ClassVar[Dict[str, str]] = {
        "V20": "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -",
        "V18": "curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -",
    }


class _Config:
    python = "python"
    rust = "rust"


_tools: dict[str, BaseEnvTool] = {
    _Config.python: PythonEnvtool(),
    _Config.rust: RustEnvTool(),
}


cli = get_client()
conf = EnvToolConfig()
logger = logging.getLogger(__name__)


def get_env_tool(tool_name: str) -> BaseEnvTool:
    """获取环境配置工具.

    Args:
        tool_name (str): 环境配置工具名称

    Returns:
        BaseEnvTool: 环境配置工具对象

    Raises:
        ValueError: 未找到环境配置工具
    """
    tool = _tools.get(tool_name.lower())
    if not tool:
        msg = f"未找到环境配置工具: {tool_name}"
        raise ValueError(msg)
    return tool


@cli.app.command("python", help="python 环境配置工具, 别名: py")
@cli.app.command("py", help="python 环境配置工具, 别名: python")
def python_env_tool(
    pypi_token: str = typer.Argument(help="PyPI token值", default=""),
    *,
    override: bool = typer.Option(help="是否覆盖已存在选项", default=True),
) -> None:
    """Python 环境配置工具."""
    tool = get_env_tool(_Config.python)
    tool.run(pypi_token=pypi_token, override=override)


@cli.app.command("javascript", help="javascript 环境配置工具, 别名: js")
@cli.app.command("js", help="javascript 环境配置工具, 别名: javascript")
def javascript_env_tool(
    version: str = typer.Argument(help="nodejs 版本", default="V18"),
) -> None:
    """JavaScript 环境配置工具."""
    if cli.is_windows:
        logger.error("当前系统为windows, 请下载压缩包直接安装")
        return

    StringCommandRunner().run(conf.NODE_VERSIONS.get(version, ""))


@cli.app.command("rust", help="rust 环境配置工具, 别名: rs")
@cli.app.command("rs", help="rust 环境配置工具, 别名: rust")
def rust_env_tool(
    install_version: str = typer.Argument(help="安装的 rust 版本", default="nightly"),
    *,
    override: bool = typer.Option(help="是否覆盖已存在选项", default=True),
) -> None:
    """Rust 环境配置工具."""
    tool = get_env_tool(_Config.rust)
    tool.run(install_version=install_version, override=override)
