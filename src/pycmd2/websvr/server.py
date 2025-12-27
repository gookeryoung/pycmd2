from __future__ import annotations

import abc
import http.server
import os
import platform
import shutil
import socketserver
import subprocess
import sys
import threading
import time
from functools import cached_property
from pathlib import Path
from typing import Optional

import typer
import webview

from pycmd2.utils import check_command_available
from pycmd2.utils import check_port_available
from pycmd2.utils import check_proc_by_name
from pycmd2.utils import kill_proc_by_port


class BaseServer(abc.ABC):
    """服务器基类."""

    CWD = Path(__file__).parent
    FRONTEND_DIR = CWD / "frontend"
    DIST_DIR = CWD / "frontend" / "deploy"

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
        assert cmd, "未找到包管理器"

        # 保存当前工作目录
        original_dir = Path.cwd()
        try:
            os.chdir(str(self.FRONTEND_DIR))
            subprocess.run([cmd, "install"], check=True)
        finally:
            # 恢复原始工作目录
            os.chdir(original_dir)

    def build(self) -> None:
        """构建前端."""
        command = self.find_package_manager()
        assert command, "未找到构建命令"

        original_dir = Path.cwd()
        try:
            os.chdir(str(self.FRONTEND_DIR))
            build_proc = subprocess.run([command, "run", "build"], check=False)
            if build_proc.returncode != 0:
                msg = "构建失败, 请检查代码是否有错误"
                raise RuntimeError(msg)
        finally:
            os.chdir(original_dir)

    def clean(self) -> None:
        """清理构建文件."""
        if not self.DIST_DIR.exists():
            typer.echo("构建文件不存在, 无需清理")
            return

        try:
            shutil.rmtree(self.DIST_DIR)
        except OSError as e:
            typer.echo(f"清理构建文件时出错: {e!s}", err=True)
        else:
            typer.echo("清理构建文件成功")

    def lint(self) -> None:
        """检查代码."""
        command = self.find_package_manager()
        assert command, "未找到包管理器"

        original_dir = Path.cwd()
        typer.echo("正在检查代码...")
        try:
            os.chdir(str(self.FRONTEND_DIR))
            subprocess.run([command, "run", "lint"], check=True)
        except subprocess.CalledProcessError as e:
            typer.echo(f"检查代码时出错: {e!s}", err=True)
        else:
            typer.echo("检查代码成功")
        finally:
            os.chdir(original_dir)


class ApiServer(BaseServer):
    """API 服务器."""

    API_DIR = BaseServer.CWD / "api"

    def start(self, port: int = 8001, host: str = "127.0.0.1") -> None:
        """启动服务器."""
        if not self.API_DIR.exists():
            typer.echo("API 目录不存在, 请先运行 pycmd2 cli install")
            return

        # 检查端口是否可用
        if not check_port_available(host, port):
            typer.echo(f"端口 {port} 已被占用, 尝试终止占用进程")
            kill_proc_by_port(port)

        def start_server() -> None:
            original_dir = Path.cwd()
            os.chdir(self.API_DIR)
            try:
                cmd = [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "main:app",
                    "--host",
                    host,
                    "--port",
                    str(port),
                    "--reload",
                ]
                subprocess.run(cmd, check=True)
            except (subprocess.CalledProcessError, OSError) as e:
                typer.echo(f"启动 API 服务器时出错: {e!s}", err=True)
                typer.Exit(1)
            finally:
                os.chdir(original_dir)

        typer.echo("正在启动开发服务器, 使用单独线程...")
        api_thread = threading.Thread(target=start_server, daemon=True)
        api_thread.start()


class NativeServer(BaseServer):
    """本地模式, 静态服务器."""

    def start(
        self,
        title: str = "PyCmd2 WebView",
        *,
        port: int = 11888,
        debug: bool = False,
    ) -> None:
        """启动服务器."""
        # 检查是否需要构建
        if not self.DIST_DIR.exists() or not self.index_html.exists():
            typer.echo("未找到生产环境文件, 正在构建...")
            self.build()

        typer.echo("正在启动生产服务器...")
        try:
            # 设置服务器
            class FrontendRouterHandler(http.server.SimpleHTTPRequestHandler):
                DIST_DIR = BaseServer.DIST_DIR

                def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
                    super().__init__(
                        *args,
                        directory=str(self.DIST_DIR),
                        **kwargs,
                    )

                def do_GET(self) -> None:
                    path = self.path.split("?")[0].split("#")[0]  # 去除查询参数和锚点

                    if path in {"/", ""}:
                        self.path = "/"
                    else:
                        requested_file = Path(self.DIST_DIR) / Path(
                            path.lstrip("/"),
                        )
                        if not requested_file.exists():
                            self.path = "/"

                    super().do_GET()

            # 启动HTTP服务器
            if not check_port_available("127.0.0.1", port):
                typer.echo(f"端口 {port} 已被占用, 尝试使用端口: {port + 1}")
                return self.start(title, port=port + 1, debug=debug)

            typer.echo(f"启动内部HTTP服务器, 端口: {port}")
            with socketserver.TCPServer(("", port), FrontendRouterHandler) as httpd:
                # 在后台线程中启动服务器
                server_thread = threading.Thread(
                    target=httpd.serve_forever,
                    daemon=True,
                )
                server_thread.start()

                # 等待服务器启动
                time.sleep(0.5)

                try:
                    webview.create_window(
                        title=title,
                        url=f"http://127.0.0.1:{port}",
                        width=1200,
                        height=800,
                        resizable=True,  # 允许调整窗口大小
                        min_size=(800, 600),  # 设置最小窗口大小
                        # 设置窗口居中显示
                        x=None,
                        y=None,
                    )
                    webview.start(debug=debug)
                finally:
                    # 关闭HTTP服务器
                    httpd.shutdown()
                    httpd.server_close()
                    typer.echo("内部HTTP服务器已关闭")
        except (RuntimeError, OSError, ImportError) as e:
            typer.echo(f"启动 WebView 窗口时出错: {e!s}", err=True)
        finally:
            self.stop()


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
        assert self.FRONTEND_DIR.exists(), "未找到前端 `frontend` 目录"

        # 检查端口是否可用
        if not check_port_available(host, port):
            typer.echo(f"端口 {port} 已被占用, 尝试使用端口: {port + 1}", err=True)
            return self.start(port=port + 1, host=host, dev=dev)

        vite_cmd = f"vite{self.cmd_suffix}"
        if check_command_available(vite_cmd):
            original_dir = Path.cwd()
            try:
                os.chdir(str(self.FRONTEND_DIR))
                if dev:
                    # 开发模式
                    self.server_proc = subprocess.Popen(
                        [vite_cmd, "--port", str(port), "--host", host],
                        cwd=str(self.FRONTEND_DIR),
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

                    # 启动预览服务器，配置spa模式以支持前端路由
                    self.server_proc = subprocess.Popen(
                        [
                            vite_cmd,
                            "preview",
                            "--port",
                            str(port),
                            "--host",
                            host,
                            "--base",
                            "/",
                        ],
                        cwd=str(self.FRONTEND_DIR),
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


def _get_nginx_conf(port: int, host: str, dist_dir: str, working_dir: str) -> str:
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

        # API 路由 - 代理到后端API服务器
        location /api/ {{
            proxy_pass http://127.0.0.1:8001/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}

        location /health {{
            proxy_pass http://127.0.0.1:8001/health;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}

        # 静态资源 - 直接从文件系统提供服务
        location /static/ {{
            alias {dist_dir}/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}

        # 主页和其他所有路由 - 提供 index.html 以支持前端路由
        location / {{
            root   {dist_dir};
            index  index.html index.htm;
            try_files $uri $uri/ /index.html;
        }}
    }}
}}
    """


class NginxServeServer(ServeServer):
    """使用 Nginx 启动静态文件服务器."""

    NGINX_CONF_DIR = ServeServer.FRONTEND_DIR.parent / "nginx"

    def start(
        self,
        port: int = 8000,
        host: str = "127.0.0.1",
    ) -> None:
        """启动 Nginx 静态文件服务器."""
        assert self.FRONTEND_DIR.exists(), "未找到前端 `frontend` 目录"
        assert self.NGINX_CONF_DIR.exists(), "未找到 `nginx` 配置根目录"

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
                os.chdir(str(self.FRONTEND_DIR))

                # 创建必要的目录
                for directory in ["logs", "tmp", "temp"]:
                    (self.NGINX_CONF_DIR / directory).mkdir(exist_ok=True)

                # 生成Nginx配置文件
                self.write_nginx_conf(port=port, host=host)

                # 启动Nginx
                self.server_proc = subprocess.Popen(
                    [nginx_cmd, "-c", "nginx.conf"],
                    cwd=str(self.NGINX_CONF_DIR),
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
        conf_path = self.NGINX_CONF_DIR / "nginx.conf"

        typer.echo("正在写入 Nginx 配置文件...")
        conf = _get_nginx_conf(
            port=port,
            host=host,
            dist_dir=str(self.DIST_DIR),
            working_dir=self.NGINX_CONF_DIR.as_posix(),
        )
        conf_path.write_text(conf)
        typer.echo("Nginx 配置文件已写入: " + str(conf_path))

    def stop(self) -> None:
        """停止 Nginx 服务器."""
        typer.echo("正在尝试停止 Nginx 服务器...")
        try:
            # 使用nginx命令优雅停止
            pid_file = self.NGINX_CONF_DIR / "tmp" / "nginx.pid"
            if pid_file.exists():
                with Path(pid_file).open("r", encoding="utf-8") as f:
                    int(f.read().strip())

                # 使用nginx -s stop命令
                self.server_proc = subprocess.Popen(
                    [
                        "nginx",
                        "-s",
                        "stop",
                        "-c",
                        str(self.NGINX_CONF_DIR / "nginx.conf"),
                    ],
                    cwd=str(self.NGINX_CONF_DIR),
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
