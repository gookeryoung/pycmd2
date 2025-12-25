from __future__ import annotations

import abc
import http.server
import os
import platform
import shutil
import socketserver
import subprocess
import threading
import time
from functools import cached_property
from pathlib import Path
from typing import Optional

import typer
import webview


def _check_command_available(cmd: str) -> bool:
    """检查可执行文件是否存在."""
    return shutil.which(cmd) is not None


class BaseServer(abc.ABC):
    """服务器基类."""

    CWD = Path(__file__).parent
    FRONT_DIR = CWD / "frontend"
    DIST_DIR = CWD / "frontend" / "output"
    DEV_MODE = False

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

    @abc.abstractmethod
    def start(self, port: int = 5173, host: str = "127.0.0.1") -> None:
        """启动服务器."""

    def start_webview_window(
        self,
        url: str,
        *,
        title: str = "PyCmd2 WebView",
    ) -> None:
        """启动 WebView 窗口."""
        try:
            webview.create_window(
                title=f"{title}{' # [DEV]' if self.DEV_MODE else ''}",
                url=url,
                width=1200,
                height=800,
                resizable=True,  # 允许调整窗口大小
                min_size=(800, 600),  # 设置最小窗口大小
                # 设置窗口居中显示
                x=None,
                y=None,
            )
            webview.start(debug=self.DEV_MODE)
        except (RuntimeError, OSError, ImportError) as e:
            typer.echo(f"启动 WebView 窗口时出错: {e!s}", err=True)
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
        except (OSError, subprocess.SubprocessError) as e:
            typer.echo(f"停止服务器时出错: {e!s}", err=True)

    def find_package_manager(self) -> Optional[str]:
        """查找可用的包管理器."""
        for cmd in ["yarn", "npm"]:
            if _check_command_available(f"{cmd}{self.cmd_suffix}"):
                return f"{cmd}{self.cmd_suffix}"
        return None

    def find_build_command(self) -> Optional[str]:
        """查找可用的构建命令."""
        for cmd in ["vite", "yarn", "npm"]:
            if _check_command_available(f"{cmd}{self.cmd_suffix}"):
                return f"{cmd}{self.cmd_suffix}"
        return None


class NativeDevServer(BaseServer):
    """本地开发服务器."""

    DEV_MODE = True

    def start(self, port: int = 5173, host: str = "127.0.0.1") -> None:
        """启动服务器."""
        assert self.FRONT_DIR.exists(), "未找到前端 `frontend` 目录"

        if not (self.FRONT_DIR / "node_modules").exists():
            typer.echo("未找到依赖项, 正在安装...")
            self._install_dependencies()

        typer.echo("正在启动开发服务器...")
        vite_cmd = f"vite{self.cmd_suffix}"
        if _check_command_available(vite_cmd):
            try:
                self.server_proc = subprocess.Popen(
                    [vite_cmd, "--port", str(port), "--host", host],
                    cwd=str(self.FRONT_DIR),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            except (subprocess.CalledProcessError, OSError) as e:
                typer.echo(f"启动 Vite 开发服务器失败: {e!s}")
                return
        else:
            typer.echo("未找到 Vite 命令, 请检查是否已安装")
            return

        self.start_webview_window(url=f"http://{host}:{port}")

    def _install_dependencies(self) -> None:
        """安装依赖."""
        cmd = self.find_package_manager()
        if cmd is None:
            msg = "未找到 yarn 或 npm 命令"
            raise RuntimeError(msg)

        # 保存当前工作目录
        original_dir = Path.cwd()
        try:
            os.chdir(str(self.FRONT_DIR))
            subprocess.run([cmd, "install"], check=True)
        finally:
            # 恢复原始工作目录
            os.chdir(original_dir)


class NativeStaticServer(BaseServer):
    """本地模式, 静态服务器."""

    DEV_MODE = False

    def __init__(self) -> None:
        super().__init__()

    def start(self) -> None:
        """启动服务器."""
        # 检查是否需要构建
        if not self.DIST_DIR.exists() or not self.index_html.exists():
            typer.echo("未找到生产环境文件, 正在构建...")
            self.build()
        else:
            typer.echo("已找到生产环境文件, 直接启动.")

        typer.echo("正在启动生产服务器...")
        self.start_webview_window(url=str(self.index_html))

    def _install_dependencies(self) -> None:
        """安装依赖."""
        cmd = self.find_package_manager()
        if cmd is None:
            msg = "未找到 yarn 或 npm 命令"
            raise RuntimeError(msg)

        # 保存当前工作目录
        original_dir = Path.cwd()
        try:
            os.chdir(str(self.FRONT_DIR))
            subprocess.run([cmd, "install"], check=True)
        finally:
            # 恢复原始工作目录
            os.chdir(original_dir)

    def build(self) -> None:
        """构建前端."""
        command = self.find_build_command()
        if command is None:
            msg = "未找到 yarn 或 npm 或 vite 命令"
            raise RuntimeError(msg)

        # 保存当前工作目录
        original_dir = Path.cwd()
        try:
            os.chdir(str(self.FRONT_DIR))
            subprocess.run([command, "build"], check=True)
        finally:
            # 恢复原始工作目录
            os.chdir(original_dir)


class ServeServer(BaseServer):
    """本地开发服务器."""

    DEV_MODE = True

    def start(self, port: int = 8000, host: str = "127.0.0.1") -> None:
        """启动静态文件服务器."""
        # 切换到静态文件目录
        original_dir = Path.cwd()
        os.chdir(self.DIST_DIR)

        try:
            # 创建服务器
            handler = http.server.SimpleHTTPRequestHandler
            httpd = socketserver.TCPServer(("", 8000), handler)

            # 在新线程中启动服务器
            server_thread = threading.Thread(target=httpd.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            url = f"http://{host}:{port}"
            typer.echo(f"静态文件服务器已启动, 请访问: {url}")
            typer.echo("按 Ctrl+C 停止服务器")

            # 保持服务器运行，直到用户手动停止
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                typer.echo("\n正在停止服务器...")
                httpd.shutdown()
                httpd.server_close()
        finally:
            # 恢复原始工作目录
            os.chdir(original_dir)
