from __future__ import annotations

import typer

from pycmd2.client import get_client
from pycmd2.commands.runner import BaseRunner

from .git_clean import GitCleanForceRunner
from .git_clean import GitCleanRunner
from .git_init import GitInitRunner


class _Config:
    clean = "clean"
    clean_force = "clean_force"
    init = "init"


_tools: dict[str, BaseRunner] = {
    _Config.clean: GitCleanRunner(),
    _Config.clean_force: GitCleanForceRunner(),
    _Config.init: GitInitRunner(),
}

cli = get_client()


def get_runner(name: str) -> BaseRunner:
    """获取执行器.

    Args:
        name (str): 执行器名称

    Returns:
        BaseRunner: 执行器对象

    Raises:
        ValueError: 如果执行器不存在
    """
    runner = _tools.get(name)
    if runner is None:
        msg = f"未找到执行器: {name}"
        raise ValueError(msg)

    return runner


@cli.app.command("init", help="初始化 git 目录, 别名: i")
@cli.app.command("i", help="初始化 git 目录, 别名: init")
def init() -> None:
    get_runner(_Config.init).run()


@cli.app.command("clean", help="清理 git 目录, 别名: c")
@cli.app.command("c", help="清理 git 目录, 别名: clean")
def clean(*, force: bool = typer.Option(False, "--force", "-f", help="强制清理")) -> None:  # noqa: FBT003
    if force:
        get_runner(_Config.clean_force).run()
    else:
        get_runner(_Config.clean).run()
