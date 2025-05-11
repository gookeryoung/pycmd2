"""功能：清理git"""

from pycmd2.common.cli import get_client
from pycmd2.git.git_push_all import check_git_status

cli = get_client()

# 排除目录
exclude_dirs = [
    ".venv",
]


@cli.app.command()
def main() -> None:
    if not check_git_status():
        return

    clean_cmd = ["git", "clean", "-xfd"]
    for exclude_dir in exclude_dirs:
        clean_cmd.extend(["-e", exclude_dir])

    cli.run_cmd(clean_cmd)
    cli.run_cmd(["git", "checkout", "."])
