"""功能: 自动推送到github, gitee等远端, 推送前检查是否具备条件."""

import logging
import shutil
import subprocess

from pycmd2.client import get_client

cli = get_client()
logger = logging.getLogger(__name__)


class CommandNotFoundError(Exception):
    """Exception raised when a command is not found in the system path."""


def _get_cmd_full_path(cmd: str) -> str:
    """获取git命令的完整路径.

    Args:
        cmd (str): 命令名

    Returns:
        str: 命令的完整路径

    Raises:
        CommandNotFoundError: 命令不存在时抛出异常
    """
    full_path = shutil.which(cmd)
    if not full_path:
        msg = f"命令不存在: {cmd}"
        raise CommandNotFoundError(msg)
    return full_path


def check_git_status() -> bool:
    """检查是否存在未提交的修改.

    Returns:
        bool: 是否存在未提交的修改
    """
    result = subprocess.run(
        [_get_cmd_full_path("git"), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.stdout.strip():
        logger.error(f"存在未提交的修改, 请先提交更改: [red]{result}")
        return False
    return True


def check_sensitive_data() -> bool:
    """检查敏感提交信息(正则表达式可根据需求扩展).

    Returns:
        bool: 是否存在敏感提交信息
    """
    result = subprocess.run(
        [_get_cmd_full_path("git"), "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=False,
    )
    sensitive_files = [".env", "credentials.json"]
    for file in result.stdout.splitlines():
        if file in sensitive_files:
            logger.error(f"检测到敏感文件, 禁止推送: [red]{file}")
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
