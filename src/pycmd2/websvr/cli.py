from __future__ import annotations

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
    svr = server.ServeServer()
    svr.start(port=port, host=host, dev=True)


@app.command("run")
@app.command("r")
def run() -> None:
    """开发模式, 启动 Vite 构建工具并启动 WebView 应用, 默认别名: r."""
    svr = server.NativeServer()
    svr.start()


@app.command("serve")
@app.command("s")
def serve(
    *,
    port: int = typer.Argument(5173, help="指定端口 (仅开发模式)"),
    host: str = typer.Option("127.0.0.1", "--host", "-H", help="指定主机 (仅开发模式)"),
) -> None:
    """仅启动 Web 服务模式, 不创建 WebView 窗口, 默认别名: s."""
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
    svr = server.NginxServeServer()
    svr.start(port=port, host=host)
