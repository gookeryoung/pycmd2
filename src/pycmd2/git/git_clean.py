"""功能：清理git"""

from pycmd2.common.cli import run_cmd
from pycmd2.common.cli import setup_client
from pycmd2.git.git_push_all import check_git_status

cli = setup_client()


@cli.app.command()
def main():
    if not check_git_status():
        return

    run_cmd(["git", "clean", "-xfd"])
    run_cmd(["git", "checkout", "."])
