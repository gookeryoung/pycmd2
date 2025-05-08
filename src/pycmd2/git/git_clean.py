"""功能：清理git"""

import subprocess

from pycmd2.common.cli import setup_client

from .git_push_all import check_git_status

cli = setup_client()


@cli.app.command()
def main():
    if not check_git_status():
        return

    subprocess.check_call(["git", "clean", "-xfd"], shell=True)
    subprocess.check_call(["git", "checkout", "."], shell=True)
