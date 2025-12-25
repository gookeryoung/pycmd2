from __future__ import annotations

import abc
import os
import platform
import shutil
import subprocess
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

    def start_native(
        self,
        url: str,
        *,
        title: str = "PyCmd2 WebView",
    ) -> None:
        """启动本地 WebView 窗口."""
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

    def install_dependencies(self) -> None:
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

    def find_build_command(self) -> Optional[str]:
        """查找可用的构建命令."""
        for cmd in ["vite", "yarn", "npm"]:
            if _check_command_available(f"{cmd}{self.cmd_suffix}"):
                return f"{cmd}{self.cmd_suffix}"
        return None

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
            build_proc = subprocess.run([command, "build"], check=True)
            if build_proc.returncode != 0:
                msg = "构建失败"
                raise RuntimeError(msg)
        finally:
            # 恢复原始工作目录
            os.chdir(original_dir)


class NativeDevServer(BaseServer):
    """本地开发服务器."""

    DEV_MODE = True

    def start(self, port: int = 5173, host: str = "127.0.0.1") -> None:
        """启动服务器."""
        assert self.FRONT_DIR.exists(), "未找到前端 `frontend` 目录"

        if not (self.FRONT_DIR / "node_modules").exists():
            typer.echo("未找到依赖项, 正在安装...")
            self.install_dependencies()

        typer.echo("正在启动开发服务器...")
        vite_cmd = f"vite{self.cmd_suffix}"
        if _check_command_available(vite_cmd):
            try:
                self.server_proc = subprocess.Popen(
                    [vite_cmd, "--port", str(port), "--host", host],
                    cwd=str(self.FRONT_DIR),
                    stdout=None,  # 输出到标准输出，这样可以看到Vite命令行信息
                    stderr=None,  # 错误输出到标准错误
                    text=True,
                )
            except (subprocess.CalledProcessError, OSError) as e:
                typer.echo(f"启动 Vite 开发服务器失败: {e!s}")
                return
        else:
            typer.echo("未找到 Vite 命令, 请检查是否已安装")
            return

        self.start_native(url=f"http://{host}:{port}")


class NativeProdServer(BaseServer):
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
        self.start_native(url=str(self.index_html))

    def install_dependencies(self) -> None:
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


class ServeServer(NativeProdServer):
    """本地开发服务器."""

    def start(
        self,
        port: int = 8000,
        host: str = "127.0.0.1",
        *,
        dev: bool = False,
    ) -> None:
        """启动静态文件服务器."""
        assert self.FRONT_DIR.exists(), "未找到前端 `frontend` 目录"

        vite_cmd = f"vite{self.cmd_suffix}"
        if _check_command_available(vite_cmd):
            original_dir = Path.cwd()
            os.chdir(str(self.FRONT_DIR))
            try:
                if dev:
                    # 开发模式
                    self.server_proc = subprocess.Popen(
                        [vite_cmd, "--port", str(port), "--host", host],
                        cwd=str(self.FRONT_DIR),
                        stdout=None,  # 输出到标准输出，这样可以看到Vite命令行信息
                        stderr=None,  # 错误输出到标准错误
                        text=True,
                    )
                    typer.echo(f"Vite 开发服务器已启动, 访问地址: http://{host}:{port}")
                else:
                    if not self.DIST_DIR.exists() or not self.index_html.exists():
                        typer.echo("未找到生产环境文件, 正在构建...")
                        self.build()

                    # 启动预览服务器
                    self.server_proc = subprocess.Popen(
                        [vite_cmd, "preview", "--port", str(port), "--host", host],
                        cwd=str(self.FRONT_DIR),
                        stdout=None,
                        stderr=None,
                        text=True,
                    )
                    typer.echo(f"Vite 预览服务器已启动, 访问地址: http://{host}:{port}")
            except (subprocess.CalledProcessError, OSError) as e:
                typer.echo(f"启动 Vite 服务器失败: {e!s}")
                return
            finally:
                os.chdir(original_dir)
        else:
            typer.echo("未找到 Vite 命令, 请检查是否已安装")
