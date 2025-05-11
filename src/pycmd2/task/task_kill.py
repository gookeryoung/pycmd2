"""功能：结束进程"""

from typer import Argument

from pycmd2.common.cli import get_client

cli = get_client()


@cli.app.command()
def main(proc: str = Argument(help="待结束进程")):
    cli.run_cmd(["taskkill", "/f", "/t", "/im", f"{proc}*"])
