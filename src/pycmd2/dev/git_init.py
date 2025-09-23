"""功能: 初始化 git 目录.

命令: gitinit
"""

import os

from pycmd2.client import get_client

cli = get_client()


@cli.app.command()
def main() -> None:
    os.chdir(str(cli.cwd))
    cli.run_cmd(["git", "init"])
    cli.run_cmd(["git", "add", "."])
    cli.run_cmd(["git", "commit", "-m", "initial commit"])
