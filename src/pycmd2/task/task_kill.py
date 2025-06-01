"""
功能：结束进程
命令: taskk [PROC]
"""

from typer import Argument
from typing_extensions import Annotated

from pycmd2.common.cli import get_client

cli = get_client()


@cli.app.command()
def main(
    proc: Annotated[str, Argument(help="待结束进程")],
):
    cli.run_cmd(["taskkill", "/f", "/t", "/im", f"{proc}*"])
