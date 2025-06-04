"""功能: 自动推送到github, gitee等远端, 推送前检查是否具备条件."""

import logging
import shutil
import subprocess

from pycmd2.common.cli import get_client

cli = get_client()


def _get_cmd_full_path(cmd: str) -> str:
    """获取git命令的完整路径."""
    full_path = shutil.which(cmd)
    if not full_path:
        msg = f"命令不存在: {cmd}"
        raise Exception(msg)
    return full_path


def check_git_status() -> bool:
    """检查是否存在未提交的修改."""
    result = subprocess.run(
        [_get_cmd_full_path("git"), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.stdout.strip():
        logging.error(f"存在未提交的修改, 请先提交更改: [red]{result}")
        return False
    return True


def check_sensitive_data() -> bool:
    """检查敏感信息(正则表达式可根据需求扩展)."""
    result = subprocess.run(
        [_get_cmd_full_path("git"), "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=False,
    )
    sensitive_files = [".env", "credentials.json"]
    for file in result.stdout.splitlines():
        if file in sensitive_files:
            logging.error(f"检测到敏感文件, 禁止推送: [red]{file}")
            return False
    return True


def push(
    remote: str,
) -> None:
    if not check_git_status():
        return

    if not check_sensitive_data():
        return

    cli.run_cmd(["git", "fetch", remote])
    cli.run_cmd(["git", "pull", "--rebase", remote])
    cli.run_cmd(["git", "push", "--all", remote])


@cli.app.command()
def main() -> None:
    remotes = ["origin", "gitee.com", "github.com"]
    cli.run(push, remotes)
