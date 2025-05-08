"""功能：结束进程"""

from typer import Argument

from pycmd2.common.cli import setup_client
from pycmd2.common.logger import run_cmd

cli = setup_client()


@cli.app.command()
def main(proc: str = Argument(help="待结束进程")):
    run_cmd(["taskkill", "/f", "/t", "/im", f"{proc}*"])
