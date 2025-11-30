from __future__ import annotations

import typer

from pycmd2.client import get_client
from pycmd2.commands import ParallelRunner
from pycmd2.commands import StrListCommandRunner

from .git_add import git_add
from .git_clean import git_clean
from .git_init import GitInitRunner
from .git_push_all import GitPushAllRunner

cli = get_client()


@cli.app.command("add", help="添加所有文件, 别名: a")
@cli.app.command("a", help="添加所有文件, 别名: add")
def add() -> None:
    ParallelRunner().run(git_add)


@cli.app.command("clean", help="清理 git 目录, 别名: c")
@cli.app.command("c", help="清理 git 目录, 别名: clean")
def clean(
    *,
    force: bool = typer.Option(False, "--force", "-f", help="强制清理"),
) -> None:
    ParallelRunner().run(lambda: git_clean(force=force))


@cli.app.command("init", help="初始化 git 目录, 别名: i")
@cli.app.command("i", help="初始化 git 目录, 别名: init")
def init() -> None:
    GitInitRunner().run()


@cli.app.command("push", help="推送所有分支, 别名: p")
@cli.app.command("p", help="推送所有分支, 别名: push")
def push() -> None:
    GitPushAllRunner().run()


@cli.app.command("re", help="重新启动 TGitCache.exe, 刷新缓存, 别名: restart")
@cli.app.command("restart", help="重新启动 TGitCache.exe, 刷新缓存, 别名: re")
def restart_tgitcache() -> None:
    if cli.is_windows:
        cmds = [
            "taskkill",
            "/f",
            "/t",
            "/im",
            "tgitcache.exe",
        ]
    else:
        cmds = ["kill", "-9", "tgitcache"]

    StrListCommandRunner().run(cmds)
