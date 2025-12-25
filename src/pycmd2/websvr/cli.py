from __future__ import annotations

import typer

from pycmd2.websvr import server

app = typer.Typer()


@app.command("run", help="开发模式, 启动 Vite 构建工具并启动 WebView 应用, 默认别名: d")
def run(
    *,
    dev: bool = typer.Option(False, "--dev", "-d", help="开发模式"),
    build: bool = typer.Option(False, "--build", "-b", help="加载前构建"),
) -> None:
    """开发模式, 启动 Vite 构建工具并启动 WebView 应用, 默认别名: d."""
    if dev:
        svr = server.LocalDevServer()
        svr.start()
    else:
        svr = server.LocalProdServer()
        if build:
            svr.build()
        svr.start()
