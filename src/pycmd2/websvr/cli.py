from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import typer

from pycmd2.websvr import server

app = typer.Typer()


@app.command("build")
@app.command("b")
def build() -> None:
    """构建静态文件, 默认别名: b."""
    svr = server.NativeServer()
    svr.build()


@app.command("clean")
@app.command("c")
def clean() -> None:
    """清理静态文件, 默认别名: c."""
    svr = server.NativeServer()
    svr.clean()


@app.command("install")
@app.command("i")
def install() -> None:
    """安装依赖, 默认别名: i."""
    svr = server.NativeServer()
    svr.install_dependencies()


@app.command("lint")
@app.command("l")
def lint() -> None:
    """代码检查."""
    svr = server.NativeServer()
    svr.lint()


@app.command("d")
def dev(
    port: int = typer.Argument(
        default=5173,
        help="指定端口 (仅开发模式)",
    ),
    host: str = typer.Option("127.0.0.1", "--host", "-H", help="指定主机 (仅开发模式)"),
) -> None:
    """开发模式, 启动 Vite 构建工具并启动 WebView 应用, 默认别名: dev."""
    api_server = server.ApiServer()
    api_server.start()

    svr = server.ServeServer()
    svr.start(port=port, host=host, dev=True)


@app.command("run")
@app.command("r")
def run(
    *,
    debug: bool = typer.Option(False, "--debug", "-d", help="启用调试模式"),
) -> None:
    """开发模式, 启动 Vite 构建工具并启动 WebView 应用, 默认别名: r."""
    api_server = server.ApiServer()
    api_server.start()

    svr = server.NativeServer()
    svr.start(debug=debug)


@app.command("serve")
@app.command("s")
def serve(
    *,
    port: int = typer.Argument(5173, help="指定端口 (仅开发模式)"),
    host: str = typer.Option("127.0.0.1", "--host", "-H", help="指定主机 (仅开发模式)"),
) -> None:
    """仅启动 Web 服务模式, 不创建 WebView 窗口, 默认别名: s."""
    api_server = server.ApiServer()
    api_server.start()

    svr = server.ServeServer()
    svr.start(port=port, host=host)


@app.command("nginx-server")
@app.command("ns")
def serve_nginx(
    *,
    port: int = typer.Argument(5173, help="指定端口 (仅开发模式)"),
    host: str = typer.Option("127.0.0.1", "--host", "-H", help="指定主机 (仅开发模式)"),
) -> None:
    """使用 Nginx 启动 Web 服务模式, 不创建 WebView 窗口, 默认别名: ns."""
    api_server = server.ApiServer()
    api_server.start()

    svr = server.NginxServeServer()
    svr.start(port=port, host=host)


@app.command("api-server")
@app.command("api")
def start_api_server(
    *,
    port: int = typer.Option(8001, "--port", "-p", help="指定API服务器端口"),
    host: str = typer.Option("127.0.0.1", "--host", "-H", help="指定API服务器主机"),
) -> None:
    """启动FastAPI后端服务器, 默认别名: api."""
    api_dir = Path(__file__).parent / "api"

    # 检查API目录是否存在
    if not api_dir.exists():
        typer.echo(f"API目录不存在: {api_dir}", err=True)
        raise typer.Exit(1)

    # 切换到API目录
    original_dir = Path.cwd()
    try:
        os.chdir(api_dir)

        # 启动FastAPI服务器
        typer.echo("正在启动FastAPI服务器...")
        typer.echo(f"访问地址: http://{host}:{port}")
        typer.echo(f"API文档: http://{host}:{port}/docs")

        # 使用subprocess启动uvicorn
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
            "--log-level",
            "info",
        ]

        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        typer.echo("FastAPI服务器已停止")
    except subprocess.CalledProcessError as e:
        typer.echo(f"启动FastAPI服务器失败: {e}", err=True)
        typer.Exit(1)
    finally:
        os.chdir(original_dir)
