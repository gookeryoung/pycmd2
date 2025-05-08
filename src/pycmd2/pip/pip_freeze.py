"""功能：输出库清单到当前目录下的 requirements.txt 中"""

from pathlib import Path

from pycmd2.common.cli import run_cmd_redirect
from pycmd2.common.cli import setup_client

cli = setup_client()
cwd = Path.cwd()


def run_pip_freeze() -> None:
    run_cmd_redirect("pip freeze >requirements.txt")


@cli.app.command()
def main():
    run_pip_freeze()
