from __future__ import annotations

import os
import platform
import shutil
import subprocess
from functools import cached_property
from pathlib import Path
from typing import Optional

import typer
import webview


def check_command_available(cmd: str) -> bool:
    """检查可执行文件是否存在."""
    return shutil.which(cmd) is not None


class BaseServer:
    """服务器基类."""

    CWD = Path(__file__).parent
    FRONT_DIR = CWD / "frontend"
    DIST_DIR = CWD / "frontend" / "dist"

    def __init__(self) -> None:
        self.server_proc: Optional[subprocess.Popen] = None

    @cached_property
    def cmd_suffix(self) -> str:
        """命令后缀."""
        if platform.system() == "Windows":
            return ".cmd"
        return ""

    @cached_property
    def index_html(self) -> Path:
        """index.html 文件路径."""
        return self.DIST_DIR / "index.html"

    def start(self) -> None:
        """启动服务器."""

    def start_webview_window(self, url: str, *, debug: bool = False) -> None:
        """启动 WebView 窗口."""
        try:
            webview.create_window(
                title="我的全栈应用 (开发模式)",
                url=url,
                width=1200,
                height=800,
            )
            webview.start(debug=debug)
        except Exception:  # noqa: BLE001
            typer.echo("启动 WebView 窗口时出错", err=True)
        finally:
            self.stop()

    def stop(self) -> None:
        """停止服务器."""
        if self.server_proc is None or self.server_proc.poll() is not None:
            typer.echo("无需停止服务器, 因为服务器未启动")
            return

        typer.echo("正在停止服务器...")
        try:
            if platform.system() == "Windows":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(self.server_proc.pid)],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                self.server_proc.terminate()

            try:
                self.server_proc.wait(timeout=10)
                typer.echo("Vite 开发服务器已正常关闭")
            except subprocess.TimeoutExpired:
                typer.echo("Vite 开发服务器未能正常关闭, 尝试强制终止")
                if platform.system() != "Windows":
                    self.server_proc.kill()
                self.server_proc.wait()
                typer.echo("Vite 开发服务器已强制关闭")
        except ProcessLookupError:
            typer.echo("无法停止服务器, 因为服务器已不存在")
        except Exception:  # noqa: BLE001
            typer.echo("停止服务器时出错", err=True)


class LocalDevServer(BaseServer):
    """本地开发服务器."""

    def __init__(
        self,
        port: int = 5173,
        host: str = "127.0.0.1",
    ) -> None:
        super().__init__()

        self.port = port
        self.host = host

    def start(self) -> None:
        """启动服务器."""
        assert self.FRONT_DIR.exists(), "未找到前端 `frontend` 目录"

        if not (self.FRONT_DIR / "node_modules").exists():
            typer.echo("未找到依赖项, 正在安装...")
            self._install_dependencies()

        typer.echo("正在启动开发服务器...")
        vite_cmd = f"vite{self.cmd_suffix}"
        if check_command_available(vite_cmd):
            try:
                self.server_proc = subprocess.Popen(
                    [vite_cmd, "--port", str(self.port), "--host", self.host],
                    cwd=str(self.FRONT_DIR),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            except (subprocess.CalledProcessError, OSError):
                typer.echo("启动 Vite 开发服务器失败")
        else:
            typer.echo("未找到 Vite 命令, 请检查是否已安装")

        self.start_webview_window(url=f"http://{self.host}:{self.port}")

    def _install_dependencies(self) -> None:
        """安装依赖."""
        if check_command_available(f"yarn{self.cmd_suffix}"):
            cmd = f"yarn{self.cmd_suffix}"
        elif check_command_available(f"npm{self.cmd_suffix}"):
            cmd = f"npm{self.cmd_suffix}"
        else:
            msg = "未找到 yarn 或 npm 命令"
            raise RuntimeError(msg)

        os.chdir(str(self.FRONT_DIR))
        subprocess.run([cmd, "install"], cwd=str(self.FRONT_DIR), check=True)


class LocalProdServer(BaseServer):
    """本地生产服务器."""

    def __init__(self) -> None:
        super().__init__()

    def start(self) -> None:
        """启动服务器."""
        if not self.DIST_DIR.exists():
            typer.echo("未找到生产环境文件, 正在构建...")
            self._build_frontend()

        if not self.index_html.exists():
            typer.echo("未找到生产环境文件, 正在构建...")
            self._build_frontend()
        else:
            typer.echo("已找到生产环境文件, 直接启动...")
            self.start_webview_window(url=str(self.index_html))

    def _build_frontend(self) -> None:
        """构建前端."""
        cmds = ["vite", "yarn", "npm"]
        for cmd in cmds:
            if check_command_available(f"{cmd}{self.cmd_suffix}"):
                command = f"{cmd}{self.cmd_suffix}"
                os.chdir(str(self.FRONT_DIR))
                subprocess.run([command, "build"], cwd=str(self.FRONT_DIR), check=True)
                return

        msg = "未找到 yarn 或 npm 或 vite 命令"
        raise RuntimeError(msg)
