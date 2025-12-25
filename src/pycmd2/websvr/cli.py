from __future__ import annotations

import typer

from pycmd2.websvr import server

app = typer.Typer()


@app.command("build")
@app.command("b")
def build() -> None:
    """构建静态文件, 默认别名: b."""
    svr = server.NativeProdServer()
    svr.build()


@app.command("run")
@app.command("r")
def run(
    port: int = typer.Option(5173, "--port", "-p", help="指定端口 (仅开发模式)"),
    host: str = typer.Option("127.0.0.1", "--host", "-H", help="指定主机 (仅开发模式)"),
    *,
    dev: bool = typer.Option(False, "--dev", "-d", help="开发模式"),
    build: bool = typer.Option(False, "--build", "-b", help="加载前构建"),
) -> None:
    """开发模式, 启动 Vite 构建工具并启动 WebView 应用, 默认别名: r."""
    if dev:
        svr = server.NativeDevServer()
        svr.start(port=port, host=host)
        return

    svr = server.NativeProdServer()
    if build:
        svr.build()
    svr.start()


@app.command("serve")
@app.command("s")
def serve(
    *,
    dev: bool = typer.Option(False, "--dev", "-d", help="开发模式"),
    port: int = typer.Option(5173, "--port", "-p", help="指定端口 (仅开发模式)"),
    host: str = typer.Option("127.0.0.1", "--host", "-H", help="指定主机 (仅开发模式)"),
) -> None:
    """仅启动 Web 服务模式, 不创建 WebView 窗口, 默认别名: s."""
    svr = server.ServeServer()
    svr.start(port=port, host=host, dev=dev)
