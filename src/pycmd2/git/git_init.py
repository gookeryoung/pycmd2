"""功能：清理git"""

import os
from pathlib import Path

from pycmd2.common.cli import run_cmd
from pycmd2.common.cli import setup_client

cli = setup_client()
cwd = Path.cwd()


@cli.app.command()
def main():
    os.chdir(str(cwd))
    run_cmd(["git", "init"])
    run_cmd(["git", "add", "."])
    run_cmd(["git", "commit", "-m", "initial commit"])
