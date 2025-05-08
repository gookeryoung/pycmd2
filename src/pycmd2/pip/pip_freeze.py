"""功能：输出库清单到当前目录下的 requirements.txt 中"""

from pathlib import Path

from pycmd2.common.cli import run_cmd_redirect
from pycmd2.common.cli import setup_client

cli = setup_client()
cwd = Path.cwd()


def pip_freeze() -> None:
    options = r' | grep -v "^\-e" '
    run_cmd_redirect(f"pip freeze {options} > requirements.txt")


@cli.app.command()
def main():
    pip_freeze()
