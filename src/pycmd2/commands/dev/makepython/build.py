from __future__ import annotations

import logging
import platform
import shutil
from abc import ABC
from abc import abstractmethod
from typing import ClassVar
from typing import List

from pycmd2.client import get_client
from pycmd2.compat import tomllib

cli = get_client()
logger = logging.getLogger(__name__)


class BaseBuild(ABC):
    """BaseMake 基类."""

    EXECUTABLE: str | None = None
    OPTIONS: ClassVar[List[str]] = []

    @abstractmethod
    def run(self) -> None:
        """Make project.

        Raises:
            ValueError: 如果 EXECUTABLE 未设置
        """
        if not self.is_valid():
            msg = f"EXECUTABLE `{self.EXECUTABLE}` is not set"
            raise ValueError(msg)

        if not cli.cwd.is_dir():
            msg = f"{cli.cwd} is not a directory"
            raise ValueError(msg)

    def is_valid(self) -> bool:
        """检查构建工具是否可用.

        Returns:
            bool: 是否可用
        """
        return bool(self.EXECUTABLE) and shutil.which(self.EXECUTABLE) is not None


class HatchlingBuild(BaseBuild):
    """HatchlingBuild 类."""

    EXECUTABLE = "hatchling"

    def run(self) -> None:
        """Make project."""
        super().run()


class MaturinBuild(BaseBuild):
    """MaturinMake 类."""

    EXECUTABLE = "maturin"

    def run(self) -> None:
        """Make project."""
        super().run()

        arch = platform.machine()
        target = f"{arch}-win7-windows-msvc" if platform.system() == "Windows" else f"{arch}-unknown-linux-gnu"
        cli.run_cmd(["maturin", "build", *self.OPTIONS, "--release", "--target", target])


class PoetryBuild(BaseBuild):
    """PoetryBuild 类."""

    EXECUTABLE = "poetry"

    def run(self) -> None:
        """Make project."""
        super().run()


_build_tools: dict[str, BaseBuild] = {
    "hatchling": HatchlingBuild(),
    "maturin": MaturinBuild(),
    "poetry": PoetryBuild(),
}


def get_build_tool() -> BaseBuild | None:
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
