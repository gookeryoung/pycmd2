"""功能：清理git"""

from pycmd2.common.cli import setup_client
from pycmd2.common.logger import run_cmd
from pycmd2.git.git_push_all import check_git_status

cli = setup_client()

# 排除目录
exclude_dirs = [
    ".venv",
]


@cli.app.command()
def main():
    if not check_git_status():
        return

    clean_cmd = ["git", "clean", "-xfd"]
    for exclude_dir in exclude_dirs:
        clean_cmd.extend(["-e", exclude_dir])

    run_cmd(clean_cmd)
    run_cmd(["git", "checkout", "."])
