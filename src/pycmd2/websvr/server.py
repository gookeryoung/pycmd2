from __future__ import annotations

import abc
import os
import platform
import subprocess
from functools import cached_property
from pathlib import Path
from typing import Optional

import typer
import webview

from pycmd2.utils import check_command_available
from pycmd2.utils import check_port_available
from pycmd2.utils import check_proc_by_name


class BaseServer(abc.ABC):
    """服务器基类."""

    CWD = Path(__file__).parent
    FRONT_DIR = CWD / "frontend"
    DIST_DIR = CWD / "frontend" / "output"

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
                title=title,
                url=url,
                width=1200,
                height=800,
                resizable=True,  # 允许调整窗口大小
                min_size=(800, 600),  # 设置最小窗口大小
                # 设置窗口居中显示
                x=None,
                y=None,
            )
            webview.start(debug=False)
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
            if check_command_available(f"{cmd}{self.cmd_suffix}"):
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
            if check_command_available(f"{cmd}{self.cmd_suffix}"):
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
            build_proc = subprocess.run([command, "build"], check=False)
            if build_proc.returncode != 0:
                msg = "构建失败, 请检查代码是否有错误"
                raise RuntimeError(msg)
        finally:
            # 恢复原始工作目录
            os.chdir(original_dir)


class NativeServer(BaseServer):
    """本地模式, 静态服务器."""

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


class ServeServer(NativeServer):
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

        # 检查端口是否可用
        if not check_port_available(host, port):
            typer.echo(f"端口 {port} 已被占用, 尝试使用端口: {port + 1}", err=True)
            return self.start(port=port + 1, host=host, dev=dev)

        vite_cmd = f"vite{self.cmd_suffix}"
        if check_command_available(vite_cmd):
            original_dir = Path.cwd()
            try:
                os.chdir(str(self.FRONT_DIR))
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
                    # 生产模式：只在需要时构建
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
                return None
            finally:
                os.chdir(original_dir)
        else:
            typer.echo("未找到 Vite 命令, 请检查是否已安装")
        return None


def _get_nginx_conf(port: int, host: str, root_dir: str, working_dir: str) -> str:
    """生成 Nginx 配置文件内容."""
    # 设置错误日志和PID文件路径，使用工作目录下的logs和tmp目录
    logs_dir = f"{working_dir}/logs"
    tmp_dir = f"{working_dir}/tmp"

    return f"""
# 设置工作目录
error_log {logs_dir}/error.log;
pid {tmp_dir}/nginx.pid;

events {{
    worker_connections 1024;
}}

http {{
    include       mime.types;
    default_type  application/octet-stream;

    server {{
        listen       {port};
        server_name  {host};

        # 设置日志文件路径
        access_log {logs_dir}/access.log;

        location / {{
            root   {root_dir};
            index  index.html index.htm;
            try_files $uri $uri/ /index.html;
        }}
    }}
}}
    """


class NginxServeServer(ServeServer):
    """使用 Nginx 启动静态文件服务器."""

    def start(
        self,
        port: int = 8000,
        host: str = "127.0.0.1",
    ) -> None:
        """启动 Nginx 静态文件服务器."""
        assert self.FRONT_DIR.exists(), "未找到前端 `frontend` 目录"

        if not self.DIST_DIR.exists() or not self.index_html.exists():
            typer.echo("未找到生产环境文件, 正在构建...")
            self.build()

        if check_proc_by_name("nginx"):
            typer.echo("已找到 Nginx 进程, 先停止 Nginx")
            self.stop()

        typer.echo("正在启动 Nginx 服务器...")
        nginx_cmd = "nginx"
        if check_command_available(nginx_cmd):
            original_dir = Path.cwd()
            try:
                # 确保工作目录存在
                os.chdir(str(self.FRONT_DIR))

                # 创建必要的目录
                (self.FRONT_DIR / "logs").mkdir(exist_ok=True)
                (self.FRONT_DIR / "temp").mkdir(exist_ok=True)

                # 生成Nginx配置文件
                self.write_nginx_conf(port=port, host=host)

                # 启动Nginx
                self.server_proc = subprocess.Popen(
                    [nginx_cmd, "-c", "nginx.conf"],
                    cwd=str(self.FRONT_DIR),
                    stdout=None,
                    stderr=None,
                    text=True,
                )
                typer.echo(f"Nginx 服务器已启动, 访问地址: http://{host}:{port}")
            except (subprocess.CalledProcessError, OSError) as e:
                typer.echo(f"启动 Nginx 服务器失败: {e!s}")
                return
            finally:
                os.chdir(original_dir)
        else:
            typer.echo("未找到 Nginx 命令, 请检查是否已安装")

    def write_nginx_conf(self, port: int, host: str) -> None:
        """写入 Nginx 配置文件."""
        conf_path = self.FRONT_DIR / "nginx.conf"

        typer.echo("正在写入 Nginx 配置文件...")
        conf = _get_nginx_conf(
            port=port,
            host=host,
            root_dir=str(self.DIST_DIR),
            working_dir=str(self.FRONT_DIR),
        )
        conf_path.write_text(conf)
        typer.echo("Nginx 配置文件已写入: " + str(conf_path))

    def stop(self) -> None:
        """停止 Nginx 服务器."""
        typer.echo("正在尝试停止 Nginx 服务器...")
        try:
            # 使用nginx命令优雅停止
            pid_file = self.FRONT_DIR / "tmp" / "nginx.pid"
            if pid_file.exists():
                with Path(pid_file).open("r", encoding="utf-8") as f:
                    int(f.read().strip())

                # 使用nginx -s stop命令
                self.server_proc = subprocess.Popen(
                    ["nginx", "-s", "stop", "-c", str(self.FRONT_DIR / "nginx.conf")],
                    cwd=str(self.FRONT_DIR),
                    stdout=None,
                    stderr=None,
                    text=True,
                )

                # 等待进程结束
                try:
                    import time

                    for _ in range(10):  # 最多等待10秒
                        if self.server_proc.poll() is not None:
                            break
                        time.sleep(1)

                    if self.server_proc.poll() is not None:
                        typer.echo("Nginx 服务器已正常关闭")
                    else:
                        typer.echo("Nginx 服务器未能正常关闭, 尝试强制终止")
                        self.server_proc.terminate()
                        self.server_proc.wait()
                        typer.echo("Nginx 服务器已强制关闭")
                except Exception as e:  # noqa: BLE001
                    typer.echo(f"等待 Nginx 服务器关闭时出错: {e!s}")
            else:
                typer.echo("Nginx 服务器未运行")
                return
        except (OSError, subprocess.SubprocessError) as e:
            typer.echo(f"停止 Nginx 服务器时出错: {e!s}", err=True)
