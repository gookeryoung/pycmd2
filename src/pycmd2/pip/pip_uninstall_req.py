"""功能：卸载库, 使用 requirements.txt"""

from pycmd2.common.cli import run_cmd
from pycmd2.common.cli import setup_client

cli = setup_client()


def pip_uninstall_req() -> None:
    run_cmd(["pip", "uninstall", "-r", "requirements.txt", "-y"])


@cli.app.command()
def main():
    pip_uninstall_req()
