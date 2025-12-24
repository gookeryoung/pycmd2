from __future__ import annotations

import os
import platform
import shutil
import subprocess
from functools import cached_property
from pathlib import Path

import typer


def check_command_available(cmd: str) -> bool:
    """检查可执行文件是否存在."""
    return shutil.which(cmd) is not None


class BaseServer:
    """服务器基类."""

    def start(self) -> None:
        """启动服务器."""


class LocalDevServer(BaseServer):
    """本地开发服务器."""

    def __init__(
        self,
        port: int = 5173,
        host: str = "127.0.0.1",
    ) -> None:
        self.port = port
        self.host = host
        self.frontend_dir = Path(__file__).parent / "frontend"

    def start(self) -> None:
        """启动服务器."""
        assert self.frontend_dir.exists(), "未找到前端 `frontend` 目录"

        if not (self.frontend_dir / "node_modules").exists():
            typer.echo("未找到依赖项, 正在安装...")
            self._install_dependencies()

    @cached_property
    def cmd_suffix(self) -> str:
        """命令后缀."""
        if platform.system() == "Windows":
            return ".cmd"
        return ""

    def _install_dependencies(self) -> None:
        """安装依赖."""
        if check_command_available(f"yarn{self.cmd_suffix}"):
            cmd = f"yarn{self.cmd_suffix}"
        elif check_command_available(f"npm{self.cmd_suffix}"):
            cmd = f"npm{self.cmd_suffix}"
        else:
            msg = "未找到 yarn 或 npm 命令"
            raise RuntimeError(msg)

        os.chdir(str(self.frontend_dir))
        subprocess.run([cmd, "install"], cwd=str(self.frontend_dir), check=True)
