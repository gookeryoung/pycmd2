"""功能: 重新启动 TGitCache.exe, 刷新缓存."""

from typing import ClassVar

from pycmd2.client import get_client
from pycmd2.commands.runner import BaseRunner

cli = get_client()


def _git_restart_tgitcache() -> None:
    if cli.is_windows:
        cli.run_cmd(["taskkill", "/f", "/t", "/im", "tgitcache.exe"])
    else:
        cli.run_cmd(["kill", "-9", "tgitcache"])


class GitRestartTGitCacheRunner(BaseRunner):
    """GitRestartTGitCacheRunner 类."""

    DESCRIPTION = "重新启动 TGitCache.exe, 刷新缓存"
    SUBCOMMANDS: ClassVar = [_git_restart_tgitcache]
