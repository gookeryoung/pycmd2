from __future__ import annotations

import logging
import platform

from pycmd2.client import get_client
from pycmd2.compat import tomllib

from .base import BaseCommand

cli = get_client()
logger = logging.getLogger(__name__)


class HatchlingBuild(BaseCommand):
    """HatchlingBuild 类."""

    EXECUTABLE = "hatchling"

    def run(self) -> None:
        """Make project."""
        super().run()


class MaturinBuild(BaseCommand):
    """MaturinMake 类."""

    EXECUTABLE = "maturin"

    def run(self) -> None:
        """Make project."""
        super().run()

        arch = platform.machine()
        target = f"{arch}-win7-windows-msvc" if platform.system() == "Windows" else f"{arch}-unknown-linux-musl"
        cli.run_cmd(["maturin", "build", *self.OPTIONS, "--release", "--target", target])


class PoetryBuild(BaseCommand):
    """PoetryBuild 类."""

    EXECUTABLE = "poetry"

    def run(self) -> None:
        """Make project."""
        super().run()


_build_tools: dict[str, BaseCommand] = {
    "hatchling": HatchlingBuild(),
    "maturin": MaturinBuild(),
    "poetry": PoetryBuild(),
}


def get_build_command() -> BaseCommand | None:
    """获取构建工具.

    Returns:
        BaseBuild: 构建工具

    Raises:
        FileNotFoundError: 如果 pyproject.toml 不存在
    """
    pyproject_file = cli.cwd / "pyproject.toml"
    if not pyproject_file.exists():
        msg = f"pyproject.toml 文件不存在, 无法获取构建工具: {pyproject_file}"
        raise FileNotFoundError(msg)

    with pyproject_file.open("rb") as f:
        config = tomllib.load(f)
        if "build-system" in config:
            build_system = config["build-system"]
            if "build-backend" in build_system:
                build_backend = build_system["build-backend"]
                if "maturin" in build_backend:
                    return _build_tools["maturin"]
                if "poetry" in build_backend:
                    return _build_tools["poetry"]
                if "hatchling" in build_backend:
                    return _build_tools["hatchling"]
    logger.error("未找到构建工具, 请手动构建")
    return None
