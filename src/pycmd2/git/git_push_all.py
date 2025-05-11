"""功能：自动推送到github, gitee等远端, 推送前检查是否具备条件."""

import logging
import subprocess

from pycmd2.common.cli import get_client

cli = get_client()


def check_git_status():
    """检查是否存在未提交的修改"""

    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    if result.stdout.strip():
        logging.error(f"存在未提交的修改，请先提交更改: [red]{result}")
        return False
    return True


def check_sensitive_data():
    """检查敏感信息（正则表达式可根据需求扩展）"""

    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
    )
    sensitive_files = [".env", "credentials.json"]
    for file in result.stdout.splitlines():
        if file in sensitive_files:
            logging.error(f"检测到敏感文件, 禁止推送: [red]{file}")
            return False
    return True


def push(
    remote: str,
):
    if not check_git_status():
        return

    if not check_sensitive_data():
        return

    cli.run_cmd(["git", "fetch", remote])
    cli.run_cmd(["git", "pull", "--rebase", remote])
    cli.run_cmd(["git", "push", "--all", remote])


@cli.app.command()
def main():
    remotes = ["origin", "gitee.com", "github.com"]
    cli.run(push, remotes)
