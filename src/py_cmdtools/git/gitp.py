"""功能：自动推送到github, gitee等远端, 推送前检查是否具备条件."""

import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor

from py_cmdtools.common.cli import setup_client

cli = setup_client()


def check_git_status():
    """检查是否存在未提交的修改"""

    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if result.stdout.strip():
        logging.error(f"存在未提交的修改，请先提交更改: [red]{result}")
        return False
    return True


def check_sensitive_data():
    """检查敏感信息（正则表达式可根据需求扩展）"""

    result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    sensitive_files = [".env", "credentials.json"]
    for file in result.stdout.splitlines():
        if file in sensitive_files:
            logging.error(f"检测到敏感文件, 禁止推送: [red]{file}")
            return False
    return True


def fetch(remote: str = "origin"):
    """拉取远端"""
    try:
        subprocess.run(["git", "fetch", remote], check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        logging.error(f"拉取远端失败: [red]{remote}")
        return False


def pull_rebase(remote: str = "origin"):
    """拉取最新代码并变基"""
    try:
        subprocess.run(["git", "pull", "--rebase", remote], check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"拉取失败，存在冲突需要解决: [red]{e}")
        return False


def run(remote: str):
    if not check_git_status():
        return
    if not check_sensitive_data():
        return
    if not fetch(remote):
        return
    if not pull_rebase(remote):
        return

    try:
        subprocess.check_call(["git", "push", "--all", remote], shell=True)
        logging.info(f"推送成功: [green bold]{remote}")
    except subprocess.CalledProcessError as e:
        logging.error(f"推送失败: [green bold]{remote}[/], [red bold]{e}")


@cli.app.command()
def main():
    remotes = ["origin", "gitee.com", "github.com"]
    with ThreadPoolExecutor(max_workers=5) as e:
        for remote in remotes:
            logging.info(f"推送到远端: [green bold]{remote}")
            e.submit(run, remote)
